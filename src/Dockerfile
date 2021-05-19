FROM amsterdam/python:3.9-buster
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
COPY requirements.txt /app/
RUN LIBGDAL_VERSION=$(gdal-config --version) pip3 install --no-cache-dir -r requirements.txt
RUN rm requirements.txt

# Copy gobmanagement module
COPY gobmanagement gobmanagement

# Copy deploy dir
COPY deploy /deploy/

# Build
COPY build.sh /app
RUN ./build.sh

# OAuth2 Proxy
COPY ./oauth2-proxy oauth2-proxy
COPY ./oauth2-proxy.cfg oauth2-proxy.cfg
RUN chmod 755 oauth2-proxy
RUN mkdir -p /var/log/oauth2-proxy && chown datapunt /var/log/oauth2-proxy

USER datapunt

CMD ["/deploy/docker-run.sh"]
