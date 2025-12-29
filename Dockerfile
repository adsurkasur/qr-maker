FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for cairo and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make start.sh executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["bash", "start.sh"]