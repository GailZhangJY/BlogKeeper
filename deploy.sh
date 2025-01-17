#!/bin/bash

# 设置错误时退出
set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 打印带颜色的信息
log_info() {
    echo -e "${GREEN}[INFO] $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

log_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装"
        return 1
    fi
    return 0
}

# 修复网络配置
fix_network() {
    log_info "修复网络配置..."
    
    # 安装 iptables 服务
    sudo yum install -y iptables-services
    
    # 停止并禁用 firewalld
    sudo systemctl stop firewalld || true
    sudo systemctl disable firewalld || true
    
    # 启用并启动 iptables
    sudo systemctl enable iptables
    sudo systemctl start iptables
    
    # 清理现有规则
    sudo iptables -F
    sudo iptables -X
    sudo iptables -t nat -F
    sudo iptables -t nat -X
    sudo iptables -t mangle -F
    sudo iptables -t mangle -X
    sudo iptables -P INPUT ACCEPT
    sudo iptables -P FORWARD ACCEPT
    sudo iptables -P OUTPUT ACCEPT
    
    # 保存 iptables 规则
    sudo service iptables save
    
    # 确保网络模块加载
    sudo modprobe br_netfilter
    sudo modprobe overlay
    
    # 配置内核参数
    cat << EOF | sudo tee /etc/sysctl.d/99-docker.conf
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF
    
    # 应用内核参数
    sudo sysctl --system
}

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装"
    else
        log_info "安装 Docker..."
        # 卸载旧版本
        sudo yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

        # 安装必要的依赖
        sudo yum install -y yum-utils device-mapper-persistent-data lvm2

        # 添加 Docker 仓库
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

        # 安装 Docker
        sudo yum install -y docker-ce docker-ce-cli containerd.io
    fi

    # 修复网络配置
    fix_network

    # 启动 Docker（添加错误处理）
    log_info "启动 Docker 服务..."
    if ! sudo systemctl start docker; then
        log_error "Docker 服务启动失败，尝试修复..."
        
        # 停止 Docker 相关服务
        sudo systemctl stop docker
        sudo systemctl stop docker.socket
        sudo systemctl stop containerd
        
        # 强制结束相关进程
        sudo killall -9 docker || true
        sudo killall -9 containerd || true
        
        # 清理 Docker 目录
        log_info "清理 Docker 目录..."
        sudo systemctl stop docker.service
        sudo systemctl stop containerd.service
        
        # 使用 find 和 rm 逐个删除文件
        sudo find /var/lib/docker -type f -exec rm -f {} \;
        sudo find /var/lib/docker -type l -exec rm -f {} \;
        sudo find /var/lib/docker -type d -empty -delete
        
        sudo rm -f /etc/docker/daemon.json
        
        # 重新创建 Docker 目录
        sudo mkdir -p /var/lib/docker
        sudo mkdir -p /etc/docker
        
        # 重新安装 Docker
        sudo yum remove -y docker-ce docker-ce-cli containerd.io
        sudo yum clean all
        sudo yum makecache
        sudo yum install -y docker-ce docker-ce-cli containerd.io
        
        # 设置正确的权限
        sudo chown root:root /var/lib/docker
        sudo chmod 701 /var/lib/docker
        
        # 重置 systemd 配置
        sudo systemctl daemon-reload
        
        # 再次修复网络配置
        fix_network
        
        # 再次尝试启动
        if ! sudo systemctl start docker; then
            log_error "Docker 服务启动失败，请检查系统日志"
            log_info "运行以下命令查看详细错误："
            log_info "systemctl status docker.service"
            log_info "journalctl -xe"
            exit 1
        fi
    fi

    # 设置开机启动
    sudo systemctl enable docker

    # 验证安装
    if ! docker --version; then
        log_error "Docker 安装失败"
        exit 1
    fi
    
    log_info "Docker 安装成功"
}

# 配置 Docker
configure_docker() {
    log_info "检查 Docker 配置..."
    
    # 如果 Docker 已经在运行且配置文件存在，跳过配置
    if [ -f "/etc/docker/daemon.json" ] && systemctl is-active docker &> /dev/null; then
        log_info "Docker 已配置且正在运行，跳过配置"
        return 0
    fi
    
    log_info "配置 Docker..."
    
    # 确保目录存在
    sudo mkdir -p /etc/docker
    
    # 检查是否需要更新配置
    local need_restart=false
    if [ ! -f "/etc/docker/daemon.json" ]; then
        need_restart=true
    else
        local old_config=$(cat /etc/docker/daemon.json)
        local new_config='{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com"
    ],
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "iptables": true,
    "ip-forward": true,
    "ip-masq": true,
    "userland-proxy": false
}'
        if [ "$old_config" != "$new_config" ]; then
            need_restart=true
        fi
    fi
    
    # 仅在需要时更新配置并重启
    if [ "$need_restart" = true ]; then
        # 配置 Docker 镜像加速和其他选项
        sudo tee /etc/docker/daemon.json > /dev/null << EOL
{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com"
    ],
    "storage-driver": "overlay2",
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "iptables": true,
    "ip-forward": true,
    "ip-masq": true,
    "userland-proxy": false
}
EOL
    
        # 设置正确的权限
        sudo chown root:root /etc/docker/daemon.json
        sudo chmod 644 /etc/docker/daemon.json
        
        # 重启 Docker 服务
        log_info "配置已更改，重启 Docker 服务..."
        sudo systemctl daemon-reload
        
        if ! sudo systemctl restart docker; then
            log_error "Docker 服务重启失败"
            log_info "请检查 Docker 日志："
            sudo systemctl status docker.service
            exit 1
        fi
        
        # 等待 Docker 服务完全启动
        sleep 5
    fi
    
    # 验证 Docker 是否正常运行
    if ! docker info &> /dev/null; then
        log_error "Docker 配置失败，服务未正常运行"
        exit 1
    fi
    
    log_info "Docker 配置完成"
}

# 检查并安装 Docker Compose
install_docker_compose() {
    if ! check_command docker-compose; then
        log_info "正在安装 Docker Compose..."
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    else
        log_info "Docker Compose 已安装"
    fi
}

# 安装必要工具
install_tools() {
    log_info "安装必要工具..."
    
    local tools=(
        "wget"
        "git"
        "curl"
        "net-tools"
    )
    
    local need_install=false
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            need_install=true
            break
        fi
    done
    
    if [ "$need_install" = true ]; then
        sudo yum install -y wget git curl net-tools
    else
        log_info "所需工具已安装"
    fi
    
    return 0
}

# 安装 Python 3.9
install_python39() {
    # 检查 Python 3.9 是否已安装且可用
    if command -v python3.9 &> /dev/null && python3.9 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)" &> /dev/null; then
        log_info "Python 3.9 已安装"
        
        # 检查 pip 是否正常工作
        if python3.9 -m pip --version &> /dev/null; then
            log_info "pip 已安装且正常工作"
            return 0
        fi
    fi

    log_info "安装 Python 3.9..."
    
    # 添加 EPEL 仓库
    if ! rpm -q epel-release &> /dev/null; then
        sudo yum install -y epel-release
    fi
    
    # 添加 IUS 仓库
    if ! rpm -q ius-release &> /dev/null; then
        sudo yum install -y https://repo.ius.io/ius-release-el7.rpm
    fi
    
    # 安装 Python 3.9（如果未安装）
    if ! rpm -q python39 &> /dev/null; then
        sudo yum install -y python39 python39-devel
    fi
    
    # 安装 pip（如果未安装）
    if ! python3.9 -m pip --version &> /dev/null; then
        sudo yum install -y python39-pip
    fi
    
    # 创建软链接（如果不存在）
    if [ ! -f /usr/local/bin/python3 ]; then
        sudo ln -sf /usr/bin/python3.9 /usr/local/bin/python3
    fi
    if [ ! -f /usr/local/bin/pip3 ]; then
        sudo ln -sf /usr/bin/pip3.9 /usr/local/bin/pip3
    fi

    # 验证安装
    if ! command -v python3.9 &> /dev/null; then
        log_error "Python 3.9 安装失败"
        return 1
    fi

    log_info "Python 3.9 安装成功"
    python3.9 --version
    python3.9 -m pip --version
}

# 强制释放端口
force_free_port() {
    local port=$1
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "尝试释放端口 ${port} (第 ${attempt} 次尝试)..."
        
        # 查找并终止占用端口的进程
        pid=$(lsof -t -i:${port})
        if [ ! -z "$pid" ]; then
            log_warn "端口 ${port} 被进程 ${pid} 占用，正在结束进程..."
            kill -9 $pid
            sleep 2
        fi
        
        # 检查端口是否已释放
        if ! netstat -tuln | grep ":${port}" > /dev/null; then
            log_info "端口 ${port} 已释放"
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    log_error "无法释放端口 ${port} (已尝试 ${max_attempts} 次)"
    return 1
}

# 检查端口占用
check_port() {
    local port=$1
    log_info "检查端口 ${port} 是否可用..."
    
    if netstat -tuln | grep ":${port}" > /dev/null; then
        log_error "端口 ${port} 已被占用"
        # 尝试强制释放端口
        if ! force_free_port $port; then
            return 1
        fi
    fi
    
    log_info "端口 ${port} 可用"
    return 0
}

# 停止已运行的服务
stop_services() {
    log_info "正在停止已运行的服务..."
    
    # 停止后端服务
    if pgrep -f "python.*api.py" > /dev/null; then
        log_info "停止后端 Python 服务..."
        pkill -9 -f "python.*api.py"
        sleep 2
    fi
    
    # 停止前端服务
    if pgrep -f "node.*vite" > /dev/null; then
        log_info "停止前端 Vite 服务..."
        pkill -9 -f "node.*vite"
        sleep 2
    fi

    # 停止所有可能的Node进程（包括npm和yarn）
    if pgrep -f "node" > /dev/null; then
        log_info "停止所有Node相关进程..."
        pkill -9 -f "node"
        sleep 2
    fi
    
    # 强制释放必要端口
    local ports_freed=true
    for port in 3101 3102; do
        if ! force_free_port $port; then
            ports_freed=false
        fi
    done
    
    if [ "$ports_freed" = false ]; then
        log_error "部分端口无法释放"
        return 1
    fi
    
    log_info "所有服务已停止，端口已释放"
    return 0
}

# 开放防火墙端口
open_ports() {
    log_info "开放防火墙端口..."
    
    # 直接使用 iptables
    sudo iptables -A INPUT -p tcp --dport 3101 -j ACCEPT
    sudo iptables -A INPUT -p tcp --dport 3102 -j ACCEPT
    
    # 保存规则
    if [ -d "/etc/sysconfig" ]; then
        # CentOS
        sudo service iptables save
    else
        # Ubuntu/Debian
        sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
    fi
    
    log_info "端口开放完成"
    return 0
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    # 确保目录存在
    mkdir -p api
    mkdir -p web
    
    # API 环境变量
    if [ ! -f api/.env ]; then
        log_info "创建 api/.env 文件..."
        cat > api/.env << EOL
API_HOST=127.0.0.1
API_PORT=3102
CORS_ORIGINS=http://localhost:3101,http://127.0.0.1:3101
EOL
    fi
    
    # Web 环境变量
    if [ ! -f web/.env ]; then
        log_info "创建 web/.env 文件..."
        cat > web/.env << EOL
VITE_API_HOST=http://127.0.0.1:3102
EOL
    fi
    
    log_info "环境变量配置完成"
}

# 拉取代码
pull_code() {
    local SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
    log_info "脚本所在目录: $SCRIPT_DIR"
    
    if [ -d "$SCRIPT_DIR/BlogKeeper" ]; then
        log_info "更新现有代码..."
        cd "$SCRIPT_DIR/BlogKeeper"
        if [ -d ".git" ]; then
            git pull
        else
            log_error "BlogKeeper 目录存在但不是git仓库，删除后重新克隆"
            cd "$SCRIPT_DIR"
            rm -rf BlogKeeper
            git clone git@github.com:GailZhangJY/BlogKeeper.git BlogKeeper
        fi
    else
        log_info "克隆代码库到 BlogKeeper 目录..."
        cd "$SCRIPT_DIR"
        git clone git@github.com:GailZhangJY/BlogKeeper.git BlogKeeper
    fi
    
    # 确保在 BlogKeeper 目录中
    cd "$SCRIPT_DIR/BlogKeeper"
}

# 备份日志
backup_logs() {
    log_info "备份容器日志..."
    
    # 创建日志目录（如果不存在）
    local log_dir="$SCRIPT_DIR/BlogKeeper/logs"
    mkdir -p "$log_dir"
    
    # 获取当前时间戳
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    
    # 备份 API 容器日志
    local api_log_file="$log_dir/api_${timestamp}.log"
    if docker ps -q -f name=blogkeeper-api-1 >/dev/null; then
        log_info "备份 API 容器日志到: $api_log_file"
        docker logs blogkeeper-api-1 > "$api_log_file" 2>&1
    else
        log_warn "API 容器未运行，跳过日志备份"
    fi
    
    # 压缩一周前的日志文件
    find "$log_dir" -name "*.log" -type f -mtime +7 -exec gzip {} \;
    
    # 删除超过30天的压缩日志
    find "$log_dir" -name "*.log.gz" -type f -mtime +30 -delete
    
    log_info "日志备份完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 备份现有容器的日志（如果存在）
    backup_logs
    
    # 检查前端构建目录
    if [ ! -d "web/dist" ]; then
        log_error "前端构建目录不存在: web/dist"
        return 1
    fi
    
    # 重启 Docker 服务
    log_info "重启 Docker 服务..."
    sudo systemctl restart docker
    sleep 5  # 等待 Docker 服务完全启动
    
    # 清理 Docker 网络
    log_info "清理 Docker 网络..."
    docker network prune -f
    
    # 停止现有服务
    log_info "停止现有服务..."
    docker-compose down --remove-orphans
    
    # 启动服务
    if [ -f "docker-compose.yml" ]; then
        log_info "启动新服务..."
        docker-compose up -d --build
        
        # 等待服务启动
        log_info "等待服务启动..."
        sleep 10
        
        # 检查服务状态
        if ! docker-compose ps | grep "Up" > /dev/null; then
            log_error "服务启动失败，请检查docker-compose日志"
            docker-compose logs
            return 1
        fi
        
        log_info "服务启动成功！"
        log_info "前端访问地址: http://localhost:3101"
        log_info "后端API地址: http://localhost:3102"
    else
        log_error "docker-compose.yml 不存在"
        return 1
    fi
    
    return 0
}

# 主函数
main() {
    log_info "开始部署 BlogKeeper..."
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 安装必要工具
    install_tools
    
    # 安装 Python 3.9
    install_python39
    
    # 检查并安装 Docker
    install_docker
    
    # 检查并安装 Docker Compose
    install_docker_compose
    
    # 配置 Docker
    configure_docker
    
    # 检查端口占用
    check_port 3101 || exit 1
    check_port 3102 || exit 1
    
    # 停止已运行的服务
    stop_services
    
    # 开放防火墙端口
    open_ports
    
    # 拉取代码
    pull_code
    
    # 配置环境变量
    setup_env
    
    # 启动服务
    start_services
    
    log_info "部署完成！"
    log_info "前端访问地址: http://localhost:3101"
    log_info "后端API地址: http://localhost:3102"
}

# 执行主函数
main
