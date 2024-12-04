FROM python:3.9

# 安装 wkhtmltopdf 及其依赖
RUN apt-get update && apt-get install -y \
    wget \
    xfonts-75dpi \
    xfonts-base \
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fontconfig \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    wkhtmltopdf \
    # 下载并安装更多中文字体
    && mkdir -p /usr/share/fonts/chinese \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

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