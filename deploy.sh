#!/bin/bash

# 设置错误时退出
set -e

# 颜色定义
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}开始部署文捕(BlogKeeper)...${NC}"

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安装，正在安装..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 拉取最新代码
echo -e "${GREEN}拉取最新代码...${NC}"
if [ ! -d "BlogKeeper" ]; then
    git clone https://github.com/your-username/BlogKeeper.git
else
    cd BlogKeeper
    git pull
    cd ..
fi

cd BlogKeeper

# 检查端口占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "错误：端口 $1 已被占用"
        exit 1
    fi
}

# 检查必要端口
check_port 3101
check_port 3102

# 构建和启动容器
echo -e "${GREEN}构建和启动容器...${NC}"
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo -e "${GREEN}部署完成！${NC}"
echo "前端访问地址: http://localhost:3101"
echo "后端访问地址: http://localhost:3102"