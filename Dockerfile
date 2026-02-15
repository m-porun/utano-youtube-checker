FROM ghcr.io/astral-sh/uv:latest AS uv_bin

FROM python:3.14-slim
COPY --from=uv_bin /uv /uvx /bin/

WORKDIR /app

# 先に依存関係だけインストール
COPY pyproject.toml ./
RUN uv sync --no-install-project

# コードをコピー
COPY . .

# PATHを通してコンテナ起動時に実行
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "check_youtube_utano.py"]
