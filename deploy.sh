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

# 检查并安装 Docker
install_docker() {
    if ! check_command docker; then
        log_info "正在安装 Docker..."
        curl -fsSL https://get.docker.com | sh
        sudo systemctl start docker
        sudo systemctl enable docker
    else
        log_info "Docker 已安装"
    fi
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

# 配置 Docker
configure_docker() {
    log_info "配置 Docker..."
    
    # 创建 Docker 配置目录
    sudo mkdir -p /etc/docker
    
    # 配置镜像加速器
    cat << EOF | sudo tee /etc/docker/daemon.json
{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://docker.mirrors.ustc.edu.cn",
        "https://registry.docker-cn.com",
        "https://hub-mirror.c.163.com"
    ]
}
EOF
    
    # 重启 Docker 服务
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    
    log_info "Docker 配置完成"
    return 0
}

# 安装必要工具
install_tools() {
    log_info "安装必要工具..."
    
    # 检测包管理器
    if command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        sudo yum install -y lsof firewalld
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
    elif command -v apt-get >/dev/null 2>&1; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y lsof ufw
        sudo ufw enable
    else
        log_error "不支持的操作系统"
        return 1
    fi
    
    log_info "工具安装完成"
    return 0
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

# 设置环境变量
setup_env() {
    log_info "设置环境变量..."
    
    # 设置API和Web端口
    export API_PORT=3102
    export WEB_PORT=3101
    
    # 将环境变量写入配置文件，以便持久化
    cat > /etc/profile.d/blogkeeper.sh << EOF
export API_PORT=3102
export WEB_PORT=3101
EOF
    
    # 立即生效
    source /etc/profile.d/blogkeeper.sh
    
    log_info "环境变量设置完成"
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

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 检查前端构建目录
    if [ ! -d "web/dist" ]; then
        log_error "前端构建目录不存在: web/dist"
        return 1
    fi
    
    # 停止现有服务
    docker-compose down
    
    # 启动服务
    if [ -f "docker-compose.yml" ]; then
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
    else
        log_error "docker-compose.yml 不存在"
        return 1
    fi
    
    log_info "服务启动完成"
    return 0
}

# 修复yum的Python版本
fix_yum() {
    log_info "修复yum配置..."
    
    # 备份原始yum文件
    if [ ! -f /usr/bin/yum.backup ]; then
        sudo cp /usr/bin/yum /usr/bin/yum.backup
    fi
    
    # 修改yum脚本，强制使用python2
    sudo sed -i '1c #!/usr/bin/python2' /usr/bin/yum
    sudo sed -i '1c #!/usr/bin/python2' /usr/libexec/urlgrabber-ext-down
    
    log_info "yum配置修复完成"
}

# 检查并安装Python 3.9
install_python() {
    log_info "检查Python版本..."
    
    # 检查是否已安装Python 3.9
    if ! command -v python3.9 &> /dev/null; then
        log_warn "未检测到Python 3.9，开始安装..."
        
        # 确保yum使用python2
        fix_yum
        
        log_info "安装编译依赖..."
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y openssl-devel bzip2-devel libffi-devel xz-devel zlib-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel python39-devel

        cd /tmp
        wget https://www.python.org/ftp/python/3.9.18/Python-3.9.18.tgz
        tar xzf Python-3.9.18.tgz
        cd Python-3.9.18
        ./configure --enable-optimizations --with-ensurepip=install --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
        make -j $(nproc)
        sudo make altinstall
        
        cd /tmp
        rm -rf Python-3.9.18 Python-3.9.18.tgz
    fi
    
    # 设置Python版本的软链接
    log_info "配置Python版本..."
    
    # 备份原有的Python软链接
    if [ -L /usr/bin/python ]; then
        sudo mv /usr/bin/python /usr/bin/python.backup
    fi
    if [ -L /usr/bin/python3 ]; then
        sudo mv /usr/bin/python3 /usr/bin/python3.backup
    fi
    
    # 设置Python 2.7
    sudo ln -sf /usr/bin/python2.7 /usr/bin/python2
    
    # 设置Python 3.9为默认Python
    sudo ln -sf /usr/local/bin/python3.9 /usr/bin/python3
    sudo ln -sf /usr/local/bin/python3.9 /usr/bin/python
    sudo ln -sf /usr/local/bin/pip3.9 /usr/bin/pip3
    sudo ln -sf /usr/local/bin/pip3.9 /usr/bin/pip
    
    # 验证Python版本
    log_info "验证Python版本..."
    python -V | grep -q "Python 3.9" || {
        log_error "Python 3.9设置为默认版本失败"
        exit 1
    }
    
    log_info "升级pip并安装依赖..."
    python -m pip install --upgrade pip
    cd /root/BlogKeeper/api
    
    # 清理并重新安装依赖
    pip uninstall -y -r requirements.txt || true
    pip install --no-cache-dir -r requirements.txt
    
    # 验证platform模块
    python -c "import platform; print(platform.system())" || {
        log_error "Python platform模块验证失败"
        exit 1
    }
    
    log_info "Python 3.9环境安装完成，已设置为默认Python版本"
    log_info "可以使用以下命令访问不同版本："
    log_info "- python 或 python3 -> Python 3.9"
    log_info "- python2 -> Python 2.7"
}

# 主函数
main() {
    log_info "开始部署 BlogKeeper..."
    
    # 检查是否为root用户
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
    
    # 首先修复yum
    fix_yum
    
    # 安装必要工具
    install_tools
    
    # 检查并安装Python
    install_python
    
    # 检查并安装Docker
    install_docker
    
    # 检查并安装Docker Compose
    install_docker_compose
    
    # 配置Docker
    configure_docker
    
    # 检查端口占用
    check_port 3101 || exit 1
    check_port 3102 || exit 1
    
    # 停止已运行的服务
    stop_services
    
    # 开放防火墙端口
    open_ports
    
    # 设置环境变量
    setup_env
    
    # 拉取代码
    pull_code
    
    # 启动服务
    start_services
    
    log_info "部署完成！"
    log_info "前端访问地址: http://localhost:${WEB_PORT}"
    log_info "后端API地址: http://localhost:${API_PORT}"
}

# 执行主函数
main
