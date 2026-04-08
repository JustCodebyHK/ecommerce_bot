FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy all your files into /app
COPY . /app

# --- THE NUCLEAR FIX ---
# This ensures a folder named 'server' exists and puts app.py inside it,
# regardless of where it is in your GitHub repo.
RUN mkdir -p /app/server && \
    cp /app/app.py /app/server/app.py || true && \
    touch /app/server/__init__.py

# Install dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system fastapi uvicorn httpx openai openenv

ENV PYTHONPATH="/app"
EXPOSE 7860

# Run the app from the folder we just forced into existence
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
