# syntax=docker/dockerfile:1
FROM amsterdam/gob_wheelhouse:3.9-buster as wheelhouse
MAINTAINER datapunt@amsterdam.nl


# Application stage.
FROM amsterdam/gob_baseimage:3.9-buster as application
MAINTAINER datapunt@amsterdam.nl
# GOB base image: SQL Server driver.

# Fill the wheelhouse.
COPY --from=wheelhouse /opt/wheelhouse /opt/wheelhouse

# Install gobmanagement service in /app folder.
WORKDIR /app

# Install required Python packages.
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install --no-cache-dir \
	--find-links /opt/wheelhouse --requirement requirements.txt
RUN rm requirements.txt
# Wheelhouse cleanup.
RUN rm -rf /opt/wheelhouse

# Copy gobmanagement module.
COPY gobmanagement gobmanagement

# Build gRPC Proto definition.
COPY build.sh /app
RUN ./build.sh

# OAuth2 Proxy.
COPY ./oauth2-proxy oauth2-proxy
COPY ./oauth2-proxy.cfg oauth2-proxy.cfg
RUN chmod 755 oauth2-proxy
RUN mkdir -p /var/log/oauth2-proxy && chown datapunt /var/log/oauth2-proxy

USER datapunt

CMD uwsgi


# Development.
FROM application as development
# Install GOB-Core in development mode. Will be overridden with
# mounts from the developer filesystem. Changes made to GOB-Core
# will be available immediately.
USER root
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Core.git
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install -e /app/GOB-Core
USER datapunt


# Test.
FROM application as test
USER root
# Remove gobcore tests
RUN rm -rf /app/src/gobcore/tests

# Copy tests module and tests
COPY tests tests
COPY test.sh pytest.ini .coveragerc .flake8 ./

# Copy Jenkins files.
COPY .jenkins /.jenkins

# gRPC Proto definition generation test.
RUN chown datapunt /app/gobmanagement/grpc/protos/jobs.proto /app/gobmanagement/grpc/out/jobs_pb2_grpc.py
RUN mkdir -p /app/shared/message_broker && chown datapunt /app/shared
USER datapunt
