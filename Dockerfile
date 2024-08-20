FROM python:3.11-slim

# Install dependencies required for building h5py and other packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    libhdf5-dev \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run your application
CMD ["python", "main.py"]
