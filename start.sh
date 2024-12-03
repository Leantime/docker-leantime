#!/bin/sh

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

/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
