# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Install uv, the package manager
RUN pip install uv

# Copy the dependency descriptor files
COPY ../pyproject.toml ../uv.lock ./

# Create a virtual environment and install dependencies using uv
RUN uv sync

# Copy the rest of the application code into the container
COPY . .

# Expose port 5001 (ensure your Flask app binds to 0.0.0.0)
EXPOSE 5001

# Run the Flask application using the virtual environment
CMD ["uv", "run", "-m", "regulation_task.regulatory_compliance_processor.web.app", "--port=5001"]

