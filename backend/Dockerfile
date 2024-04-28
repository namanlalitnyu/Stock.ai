# Use Ubuntu as the base image
FROM ubuntu:latest

# Set the working directory inside the container
WORKDIR /backend

# Copy the current directory contents into the container at /backend
COPY . /backend

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3-pip python3-venv

# Create a Python virtual environment and activate it
RUN python3 -m venv venv
ENV PATH="/backend/venv/bin:$PATH"

# Install the requirements needed for the project
RUN pip install -r requirements.txt

EXPOSE 5000

# Run the app when the container launches
ENTRYPOINT ["python"]
CMD ["app.py"]
