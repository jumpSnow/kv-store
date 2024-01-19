# Use an official Python runtime as a parent image
FROM python:3.13.0a3-alpine


MAINTAINER Mengdi Wei "mwei6@ucsc.edu"

# Set the working directory to /CSE138_assignment3
WORKDIR /cse138_assignment4

# Copy the current directory contents into the container at /CSE138_assignment3
ADD . /cse138_assignment4

# Install Flask if needed
RUN pip install -r requirements.txt

EXPOSE 13800
# Run app.py when the container launches
CMD ["python", "./manage.py" ]