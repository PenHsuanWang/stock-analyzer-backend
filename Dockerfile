# Use Ubuntu 22.04 as the base image
# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables to non-interactive (this prevents prompts during package installation)
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install Python and pip
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Add the current directory to the PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Copy the entire project into the container
COPY . /app/

# Install Python dependencies and local wheel
RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && python3 -m pip install --no-cache-dir dist/stock_analyzer-*.whl

# Expose the port the server listens on
EXPOSE 8000

# Set the entry point to the application server
ENTRYPOINT ["python3", "src/run_server.py"]
#CMD ["/bin/bash"]
