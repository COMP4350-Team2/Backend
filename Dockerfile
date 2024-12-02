# Use an official Python runtime as a parent image
FROM python:3.12

# Set the root directory inside the container
WORKDIR /opt/cupboard

# Install dependencies, the --no-cache-dir prevents pip from using its cache
# during the installation process
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend directory
COPY . .

# Expose the port this will run on
EXPOSE 6060

# Start the app using server command
CMD ["python", "manage.py", "runserver"]
