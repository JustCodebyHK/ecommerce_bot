FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system fastapi uvicorn httpx openai openenv

# This tells Python to treat /app as the home base for all imports
ENV PYTHONPATH="/app"
EXPOSE 7860

# We run from the root, targeting the folder specifically
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
