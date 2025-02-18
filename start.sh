#!/bin/sh

# Function to set permissions
set_permissions() {
    # Only set permissions if running as root
    if [ "$(id -u)" = "0" ]; then
        chown -R www-data:www-data /var/www/html
        chmod -R 775 /var/www/html

        # Ensure specific directories exist and have correct permissions
        local dirs="/var/www/html/userfiles /var/www/html/public/userfiles /var/www/html/storage/logs /var/www/html/app/Plugins"
        for dir in $dirs; do
            mkdir -p "$dir"
            chown -R www-data:www-data "$dir"
            chmod 2775 "$dir"
        done

        # Ensure supervisord can write its pid file
        mkdir -p /run && chown www-data:www-data /run
    fi
}

# Handle PUID/PGID
if [ -n "${PUID}" ] && [ -n "${PGID}" ]; then
    if [ -n "${PUID}" ] && [ "${PUID}" != "1000" ]; then
        usermod -u "${PUID}" www-data
    fi
    if [ -n "${PGID}" ] && [ "${PGID}" != "1000" ]; then
        groupmod -g "${PGID}" www-data
    fi

    # After changing UID/GID, we need to fix permissions
    set_permissions
fi

# Always ensure correct permissions
set_permissions

if [[  -n "${LEAN_DB_PASSWORD_FILE}" ]]; then
  LEAN_DB_PASSWORD=$(cat "${LEAN_DB_PASSWORD_FILE}")
  export LEAN_DB_PASSWORD
fi

if [[  -n "${LEAN_EMAIL_SMTP_PASSWORD_FILE}" ]]; then
  LEAN_EMAIL_SMTP_PASSWORD=$(cat "${LEAN_EMAIL_SMTP_PASSWORD_FILE}")
  export LEAN_EMAIL_SMTP_PASSWORD
fi

if [[  -n "${LEAN_S3_SECRET_FILE}" ]]; then
  LEAN_S3_SECRET=$(cat "${LEAN_S3_SECRET_FILE}")
  export LEAN_S3_SECRET
fi

if [[  -n "${LEAN_SESSION_PASSWORD_FILE}" ]]; then
  LEAN_SESSION_PASSWORD=$(cat "${LEAN_SESSION_PASSWORD_FILE}")
  export LEAN_SESSION_PASSWORD
fi

if [[  -n "${LEAN_REDIS_PASSWORD_FILE}" ]]; then
  LEAN_REDIS_PASSWORD=$(cat "${LEAN_REDIS_PASSWORD_FILE}")
  export LEAN_REDIS_PASSWORD
fi

if [[  -n "${LEAN_DB_HOST_FILE}" ]]; then
  LEAN_DB_HOST=$(cat "${LEAN_DB_HOST_FILE}")
  export LEAN_DB_HOST
fi

if [[  -n "${LEAN_DB_DATABASE_FILE}" ]]; then
  LEAN_DB_DATABASE=$(cat "${LEAN_DB_DATABASE_FILE}")
  export LEAN_DB_DATABASE
fi

if [[  -n "${LEAN_DB_USER_FILE}" ]]; then
  LEAN_DB_USER=$(cat "${LEAN_DB_USER_FILE}")
  export LEAN_DB_USER
fi

if [[  -n "${LEAN_EMAIL_SMTP_USERNAME_FILE}" ]]; then
  LEAN_EMAIL_SMTP_USERNAME=$(cat "${LEAN_EMAIL_SMTP_USERNAME_FILE}")
  export LEAN_EMAIL_SMTP_USERNAME
fi

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
