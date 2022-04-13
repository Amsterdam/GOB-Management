FROM amsterdam/python:3.9-buster as application
MAINTAINER datapunt@amsterdam.nl

# Install gobmanagement service in /app folder
WORKDIR /app

# Install SQL Server driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install GDAL
RUN apt-get install -y libgdal-dev

# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Install required Python packages
RUN LIBGDAL_VERSION=$(gdal-config --version) && pip3 install GDAL==${LIBGDAL_VERSION}
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobmanagement module
COPY gobmanagement gobmanagement

# Build
COPY build.sh /app
RUN ./build.sh

# OAuth2 Proxy
COPY ./oauth2-proxy oauth2-proxy
COPY ./oauth2-proxy.cfg oauth2-proxy.cfg
RUN chmod 755 oauth2-proxy
RUN mkdir -p /var/log/oauth2-proxy && chown datapunt /var/log/oauth2-proxy

USER datapunt

CMD uwsgi

FROM application as development
# Install GOB-Core and GOB-Config in development mode. Will be overridden with
# mounts from the developer filesystem. Changes made to GOB-Core and GOB-Config
# will be available immediately.
USER root
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Core.git
RUN LIBGDAL_VERSION=$(gdal-config --version) pip install -e /app/GOB-Core
RUN git clone --depth=1 https://github.com/Amsterdam/GOB-Config.git
RUN pip install -e /app/GOB-Config
USER datapunt


FROM application as test
# Run tests as root for now
USER root
# Remove gobcore/gobconfig tests
RUN rm -rf /app/src/gobcore/tests
RUN rm -rf /app/src/gobconfig/tests

# Copy tests
COPY tests tests
COPY .flake8 .flake8
COPY test.sh test.sh
COPY .coveragerc .coveragerc

# Copy jenkins files
COPY .jenkins /.jenkins

RUN mkdir -p /app/shared/message_broker && chown datapunt /app/shared
USER datapunt
