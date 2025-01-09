# Use the official Rasa image
FROM rasa/rasa:3.1.0

# Copy project files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Install additional dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Rasa's default port and custom action port
EXPOSE 5005
EXPOSE 5055

# Start the Rasa server and action server
CMD ["sh", "-c", "rasa run --enable-api --cors '*' --port 5005 & rasa run actions --port 5055"]
