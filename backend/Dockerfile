# Use Ubuntu as the base image
FROM python:3.8-slim

# Copy the current directory contents into the container at /backend
COPY . /backend

# Set the working directory inside the container
WORKDIR /backend

# Install the requirements needed for the project
RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 3000

CMD ["gunicorn", "--bind", "0.0.0.0:3000", "app:app"]