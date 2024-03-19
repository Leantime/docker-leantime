FROM docker.io/library/php:8.1-fpm-alpine

# Build with: `docker build . --tag leantime:devel`

##########################
#### ENVIRONMENT INFO ####
##########################

# Change version to trigger build
ARG LEAN_VERSION=3.1.0-beta

WORKDIR /var/www/html

VOLUME [ "/sessions" ]

# Expose port 80 and start php-fpm server
ENTRYPOINT ["/start.sh"]
EXPOSE 80

########################
#### IMPLEMENTATION ####
########################

# Install dependencies
RUN apk add --no-cache \
    mysql-client \
    openldap-dev\
    libzip-dev \
    zip \
    freetype libpng libjpeg-turbo freetype-dev libpng-dev libjpeg-turbo-dev oniguruma-dev \
    icu-libs \
    jpegoptim optipng pngquant gifsicle \
    supervisor \
    apache2 \
    apache2-ctl \
    apache2-proxy


## Installing extensions ##
# Running in a single command is worse for caching/build failures, but far better for image size
RUN docker-php-ext-install \
    mysqli pdo_mysql mbstring exif pcntl pdo bcmath opcache ldap zip \
    && \
    docker-php-ext-enable zip \
    && \
    docker-php-ext-configure gd \
      --enable-gd \
      --with-jpeg=/usr/include/ \
      --with-freetype \
      --with-jpeg \
    && \
    docker-php-ext-install gd


## Installing Leantime ##

# (silently) Download the specified release, piping output directly to `tar`
RUN curl -sL https://github.com/Leantime/leantime/releases/download/v${LEAN_VERSION}/Leantime-v${LEAN_VERSION}.tar.gz | \
    tar \
      --ungzip \
      --extract \
      --verbose \
      --strip-components 1 \
      --numeric-owner \
      --owner=82 \
      --group=127

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY config/custom.ini /usr/local/etc/php/conf.d/custom.ini

# Configure supervisord
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY config/app.conf  /etc/apache2/conf.d/app.conf

RUN sed -i '/LoadModule rewrite_module/s/^#//g' /etc/apache2/httpd.conf && \
    sed -i 's#AllowOverride [Nn]one#AllowOverride All#' /etc/apache2/httpd.conf && \
    sed -i '$iLoadModule proxy_module modules/mod_proxy.so' /etc/apache2/httpd.conf

RUN mkdir -p "/sessions" && chown www-data:www-data /sessions && chmod 0777 /sessions
