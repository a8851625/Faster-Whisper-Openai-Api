# 使用官方 Python 3.9 镜像作为基础镜像
FROM nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu22.04 

# 安装 Python 和依赖项
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-setuptools \
    python3-dev \
    vim curl wget \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到容器的工作目录
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露服务端口
EXPOSE 5000

# 启动 Flask 应用
CMD ["python", "app.py"]

