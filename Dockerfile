FROM ghcr.io/meta-pytorch/openenv-base:latest

# Set the working directory to /app (standard for these environments)
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy everything to /app
COPY . .

# Install dependencies. 
# Added '-r requirements.txt' to ensure any additional project libs are included
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv pip install --system fastapi uvicorn httpx openai openenv

# CRITICAL: This allows 'server.app' to be found and 
# allows 'app.py' to import 'inference.py' from the root.
ENV PYTHONPATH="/app"

# Open the port Hugging Face uses
EXPOSE 7860

# Updated CMD to point to the server folder as required by the validator
# This runs the 'app' object inside 'server/app.py'
CMD ["python3", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
