FROM amsterdam/docker_python:latest
MAINTAINER datapunt@amsterdam.nl

# Install gobmanagement service in /app folder
WORKDIR /app

# Install required Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobmanagement module
COPY gobmanagement gobmanagement

CMD uwsgi --http-websockets --enable-threads --threads 4
