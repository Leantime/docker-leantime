FROM php:7.2-fpm


# Set working directory
WORKDIR /var/www/html

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-mysql-client \
    libfreetype6-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    locales \
    jpegoptim optipng pngquant gifsicle \
    git \
    curl \
    nano \
    zip \
    unzip \
    npm \
    wget \
    supervisor \
    apache2


# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Installing extensions
RUN docker-php-ext-install mysqli pdo_mysql mbstring exif pcntl pdo bcmath
RUN docker-php-ext-configure gd --with-gd --with-jpeg-dir=/usr/include/ --with-png-dir=/usr/include/
RUN docker-php-ext-install gd



RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer


RUN groupadd -g 1000 www
RUN useradd -u 1000 -ms /bin/bash -g www www


RUN cd /var/www/html && \
    wget https://github.com/Leantime/leantime/releases/download/v2.0.4/Leantime-V2.0.4.tar.gz && \
    tar -zxvf Leantime-V2.0.4.tar.gz --strip-components 1


RUN chmod 775 . && \
    chgrp www-data . && \
    chmod g+s .


COPY ./start.sh /start.sh

RUN chown root:root /start.sh && \
    chmod 4755 /start.sh


COPY config/custom.ini /usr/local/etc/php/conf.d/custom.ini

# Configure supervisord
COPY config/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY config/app.conf /etc/apache2/sites-available/000-default.conf

RUN a2enmod proxy_fcgi rewrite

# Expose port 9000 and start php-fpm server
ENTRYPOINT ["/start.sh"]
EXPOSE 80
