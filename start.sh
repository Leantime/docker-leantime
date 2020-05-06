#!/bin/sh

APP_DIR="/var/www/html"
CONFIG="/var/www/html/config/configuration.php"

if [ -f "$CONFIG" ]; then
    echo "Config file already exists!"
else
    echo "Creating configuration file!"
    cd $APP_DIR
    cp config/configuration.sample.php ${CONFIG}

    if [ -z "$LEAN_SESSION_PASSWORD" ]; then
        #generating 32 character string for session password
        SESSION_PASSWORD=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w ${1:-32} | head -n 1)
        sed -i 's/$sessionpassword = "3evBlq9zdUEuzKvVJHWWx3QzsQhturBApxwcws2m"/$sessionpassword = "'"${SESSION_PASSWORD}"'"/g' ${CONFIG}
    fi

fi

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

