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
    if [ ! -d "/etc/docker" ]; then
        sudo mkdir -p /etc/docker
    fi
    
    # 配置 Docker 镜像加速
    if [ ! -f "/etc/docker/daemon.json" ]; then
        echo '{
            "registry-mirrors": [
                "https://registry.cn-hangzhou.aliyuncs.com",
                "https://mirror.ccs.tencentyun.com",
                "https://docker.mirrors.ustc.edu.cn"
            ],
            "insecure-registries": [],
            "debug": true,
            "experimental": true
        }' | sudo tee /etc/docker/daemon.json
        
        # 重启 Docker 服务
        sudo systemctl daemon-reload
        sudo systemctl restart docker
    fi
}

# 检查端口占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        log_error "端口 $1 已被占用"
        return 1
    fi
    return 0
}

# 检查环境变量文件
check_env_file() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log_warn "未找到 .env 文件，将使用 .env.example 创建"
            cp .env.example .env
            log_info "请修改 .env 文件中的配置"
        else
            log_error "未找到 .env 和 .env.example 文件"
            return 1
        fi
    fi
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
    # 强制重新构建镜像
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务健康状态
    if docker-compose ps | grep -q "Exit"; then
        log_error "部分服务启动失败，请检查日志"
        docker-compose logs
        return 1
    fi
    
    log_info "所有服务已成功启动"
}

# 安装 Python 3.9
install_python39() {
    if command -v python3.9 &> /dev/null; then
        log_info "Python 3.9 已安装"
        return 0
    fi

    log_info "安装 Python 3.9..."
    
    # 安装依赖
    sudo yum update -y
    sudo yum install wget -y
    sudo yum groupinstall "Development Tools" -y
    sudo yum install openssl-devel bzip2-devel libffi-devel xz-devel -y

    # 下载并编译 Python 3.9
    cd /opt
    sudo wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
    sudo tar xzf Python-3.9.16.tgz
    cd Python-3.9.16
    sudo ./configure --enable-optimizations
    sudo make altinstall

    # 创建软链接
    sudo ln -sf /usr/local/bin/python3.9 /usr/local/bin/python3
    sudo ln -sf /usr/local/bin/pip3.9 /usr/local/bin/pip3

    # 验证安装
    if ! command -v python3.9 &> /dev/null; then
        log_error "Python 3.9 安装失败"
        return 1
    fi

    log_info "Python 3.9 安装成功"
    python3.9 --version
    pip3.9 --version
}

# 主函数
main() {
    log_info "开始部署 BlogKeeper..."
    
    # 安装必要工具
    install_docker
    install_docker_compose
    configure_docker
    install_python39
    
    # 检查必要端口
    check_port 3101 || exit 1
    check_port 3102 || exit 1
    
    # 检查环境变量
    # check_env_file || exit 1
    
    # 拉取代码
    pull_code
    
    # 启动服务
    start_services
    
    log_info "部署完成！"
    log_info "前端访问地址: http://localhost:3101"
    log_info "后端访问地址: http://localhost:3102"
}

# 执行主函数
main
