#!/bin/sh

APP_DIR="/var/www/html"
CONFIG="/var/www/html/config/configuration.php"

if [ -f "$CONFIG" ]; then
    echo "Config file already exists!"
else
    echo "Creating configuration file!"
    cd $APP_DIR
    cp /var/www/html/config/configuration.sample.php /var/www/html/config/configuration.php
    sed -i 's/$dbHost="localhost"/$dbHost="'"${DB_HOST}"'"/g' config/configuration.php && \
    sed -i 's/$dbUser=""/$dbUser="'"${MYSQL_USER}"'"/g' config/configuration.php && \
    sed -i 's/$dbPassword=""/$dbPassword="'"${MYSQL_PASSWORD}"'"/g' config/configuration.php && \
    sed -i 's/$dbDatabase=""/$dbDatabase="'"${MYSQL_DATABASE}"'"/g' config/configuration.php

    #generating 32 character string for session password
    SESSION_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w ${1:-32} | head -n 1)
    sed -i 's/$sessionpassword = "3evBlq9zdUEuzKvVJHWWx3QzsQhturBApxwcws2m"/$sessionpassword = "'"${SESSION_PASSWORD}"'"/g' config/configuration.php

fi

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf