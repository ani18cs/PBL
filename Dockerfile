FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (gcc, python-dev if needed, but slim is sufficient here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy platform source code
COPY . .

# Expose TCP Target Server (8080) and Flask SocketIO dashboard (5000)
EXPOSE 8080 5000

ENV PYTHONUNBUFFERED=1

# Launch application entrypoint
CMD ["python", "app.py"]
