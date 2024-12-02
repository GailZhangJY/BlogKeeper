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

# 检查端口占用
check_port() {
    local port=$1
    log_info "检查端口 ${port} 是否可用..."
    
    if netstat -tuln | grep ":${port}" >/dev/null 2>&1; then
        log_error "端口 ${port} 已被占用"
        return 1
    fi
    
    log_info "端口 ${port} 可用"
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
setup_environment() {
    log_info "设置环境变量..."
    
    # 创建环境变量文件
    cat > .env << EOF
# API配置
API_PORT=3102
API_HOST=0.0.0.0
DEBUG=False

# Web配置
WEB_PORT=3101
API_URL=http://localhost:3102
EOF

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

# 主函数
main() {
    log_info "开始部署 BlogKeeper..."
    
    # 安装必要工具
    install_tools || exit 1
    install_docker || exit 1
    install_docker_compose || exit 1
    configure_docker || exit 1
    
    # 检查必要端口
    check_port 3101 || exit 1
    check_port 3102 || exit 1
    
    # 开放防火墙端口
    open_ports || exit 1
    
    # 设置环境变量
    setup_environment || exit 1
    
    # 拉取最新代码
    if ! pull_code; then
        log_error "代码拉取失败"
        exit 1
    fi
    
    # 启动服务
    if ! start_services; then
        log_error "服务启动失败"
        exit 1
    fi
    
    log_info "部署完成！"
    log_info "前端访问地址: http://localhost:3101"
    log_info "后端API地址: http://localhost:3102"
}

# 执行主函数
main
