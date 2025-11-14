FROM python:3.11-slim

# Install OS-level dependencies required by PyMuPDF (fitz)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libmujs-dev \
    zlib1g-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
