
FROM python:3.14-slim-trixie

# 使用官方 uv 二进制，固定版本
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

WORKDIR /app

ENV UV_PYTHON_DOWNLOADS=0 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

# 先安装依赖，利用 Docker 层缓存
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project --no-cache

# 再复制应用源码
COPY . .

CMD ["python", "app.py"]
