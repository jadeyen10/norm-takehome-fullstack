# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /norm-fullstack

# Unbuffered output so logs show up in Docker
ENV PYTHONUNBUFFERED=1

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install Python dependencies (torch/llama-index can be large)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Optional: override when running the container so app can reach host services
# e.g. -e QDRANT_HOST=host.docker.internal -e OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV QDRANT_HOST=localhost
ENV QDRANT_PORT=6333
ENV OLLAMA_BASE_URL=http://localhost:11434

# Copy the content of the local src directory to the working directory
COPY ./app /norm-fullstack/app
COPY ./docs /norm-fullstack/docs

EXPOSE 80

# Command to run on container start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]