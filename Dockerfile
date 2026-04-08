FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy everything
COPY . /app

# DEBUG: This will print the file list in your Hugging Face logs 
# so we can see where the 'server' folder actually is.
RUN ls -R /app

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system fastapi uvicorn httpx openai openenv

ENV PYTHONPATH="/app"
EXPOSE 7860

# We use the module syntax
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
