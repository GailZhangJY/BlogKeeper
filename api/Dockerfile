FROM python:3.9
# 设置pip源为清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/ \
    && pip config set install.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app
# 先复制 tools 目录，这样如果其他文件变化不会重新构建这一层
COPY tools /app/tools
# 设置 wkhtmltopdf 可执行权限
RUN chmod +x /app/tools/wkhtmltopdf/bin/wkhtmltopdf

# 复制其他文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 创建必要的目录并设置权限
RUN mkdir -p /app/temp /app/logs && \
    chmod -R 777 /app/temp /app/logs
# 启动 FastAPI 应用
CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "3102"]