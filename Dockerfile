FROM ghcr.io/meta-pytorch/openenv-base:latest

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy everything from your repo into /app
# This ensures /app/server/app.py exists
COPY . /app

# Install dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system fastapi uvicorn httpx openai openenv

# Force Python to look at the root directory for modules
ENV PYTHONPATH="/app"

# Expose the correct port
EXPOSE 7860

# We use the relative path from the WORKDIR
# This tells uvicorn: "Look in the 'server' folder for 'app.py' and the 'app' variable"
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
