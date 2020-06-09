FROM amsterdam/python:latest
MAINTAINER datapunt@amsterdam.nl

# Install gobmanagement service in /app folder
WORKDIR /app

# Install required Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobmanagement module
COPY gobmanagement gobmanagement

# Copy deploy dir
COPY deploy /deploy/

# Build
COPY build.sh /app
RUN ./build.sh

# Gatekeeper
COPY ./keycloak-gatekeeper.latest keycloak-gatekeeper
COPY ./gatekeeper.conf gatekeeper.conf
RUN chmod 755 keycloak-gatekeeper
RUN mkdir -p /var/log/gatekeeper && chown datapunt /var/log/gatekeeper

USER datapunt

CMD ["/deploy/docker-run.sh"]
