FROM python:3.9

# 设置pip源为清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app

# 先复制并安装依赖，这样如果代码改变但依赖没变，可以利用缓存
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录并设置权限
RUN mkdir -p /app/temp /app/logs && \
    chmod -R 777 /app/temp /app/logs

# 启动 FastAPI 应用
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3102"]