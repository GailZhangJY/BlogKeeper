FROM python:3.9-centos7

# 安装 wkhtmltopdf
RUN yum install -y https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.centos7.x86_64.rpm \
    && yum clean all

# 设置pip源为清华源
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && pip3 config set install.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app

# 先复制并安装依赖，这样如果代码改变但依赖没变，可以利用缓存
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录并设置权限
RUN mkdir -p /app/temp /app/logs && \
    chmod -R 777 /app/temp /app/logs

# 启动 FastAPI 应用
CMD ["python3", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3102"]