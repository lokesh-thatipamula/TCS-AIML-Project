# Multi-platform production container for Insurance Risk Profile Summarizer
FROM python:3.9-slim

WORKDIR /app

# Set non-buffering python stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copy application files
COPY agent/ ./agent/
COPY data/ ./data/
COPY static/ ./static/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY app.py .
COPY requirements.txt .

EXPOSE 8080

CMD ["python3", "app.py"]
