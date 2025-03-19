<a href="https://leantime.io"><img src="https://leantime.io/wp-content/uploads/2023/03/leantime_logo.png" alt="Leantime Logo" width="300"/></a>
# Leantime Docker Deployment Guide


[![License Badge](https://img.shields.io/github/license/leantime/leantime?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Docker Hub Badge](https://img.shields.io/docker/pulls/leantime/leantime?style=flat-square)](https://hub.docker.com/r/leantime/leantime)
![Github Downloads](https://img.shields.io/github/downloads/leantime/leantime/total)
[![Discord Badge](https://img.shields.io/discord/990001288026677318?label=Discord&style=flat-square)](https://discord.gg/4zMzJtAq9z)
[![Crowdin](https://badges.crowdin.net/leantime/localized.svg)](https://crowdin.com/project/leantime)
![GitHub Sponsors](https://img.shields.io/github/sponsors/leantime)
<br />

Leantime is an open source project management system for small teams and startups written in PHP, Javascript using MySQL. [https://leantime.io](https://leantime.io)

This is the official <a href="https://hub.docker.com/r/leantime/leantime">Docker image for Leantime</a>. It was built using the <a href="https://github.com/Leantime/leantime/releases">latest Leantime release</a>.

## How to use this image
Below you will find examples on how to get started with Leantime trough `docker run` or `docker compose`.

### Option 1: Quick Start with Docker Compose (Recommended)

```
    git clone https://github.com/Leantime/docker-leantime.git 
    cd docker-leantime 
    cp sample.env .env
```
Edit .env file with your settings and then run

```
    docker compose up -d
```

### Option 2: Direct Docker Run

#### Create network

``` 
docker network create leantime-net
```
#### Start Mysql

``` 
    docker run -d --restart unless-stopped -p 3306:3306 --network leantime-net \ 
    -e MYSQL_ROOT_PASSWORD= changeme123 \ 
    -e MYSQL_DATABASE=leant ime \ 
    -e MYSQL_USER=lean \ 
    -e MYSQL_PASSWORD=chang eme123 \ 
    --name mysql_leantime mysql:8.4
```

## Docker specific configuration options

### Port Configuration
By default, Leantime runs on port 8080 internally.

To map port 80 externally to 8080 internally in docker-compose.yml:

```
    ports: - "80:8080"
```


### Running as Non-Root User

You can map the container's internal user/group to match your host's user/group by setting the `PUID` and `PGID` environment variables. This helps avoid permission issues between the container and host machine. To find your host user/group ID, run `id username` on the host system. For example, to run the container as your current user, you would set:

```
    docker run -e PUID=$(id -u) -e PGID=$(id -g) leantime/leantime:latest
```

Or in docker-compose.yml:

```
services: 
    leantime: 
        environment: 
            - PUID=1000 # Replace with your user ID 
            - PGID=1000 # Replace with your group ID
```

### Volume Management
Important directories that should be persisted:

```
volumes: 
    - public_userfiles:/var/www/html/public/userfiles # Public files, logos 
    - userfiles:/var/www/html/userfiles # User uploaded files 
    - plugins:/var/www/html/app/Plugins # Plugin directory 
    - logs:/var/www/html/storage/logs # Application logs
```

### Docker secrets

As an alternative to passing sensitive information via environment variables, `_FILE` may be appended to the environment variables listed below, causing the initialization script to load the values for those variables from files present in the container. In particular, this can be used to load passwords from Docker secrets stored in `/run/secrets/<secret_name>` files. For example:

```
docker run -d --restart unless-stopped -p 80:80 --network leantime-net \
-e LEAN_DB_HOST=mysql_leantime \
-e LEAN_DB_USER=admin \
-e LEAN_DB_PASSWORD_FILE=/run/secrets/lean-db-password \
-e LEAN_DB_DATABASE=leantime \
--name leantime leantime/leantime:latest
```

Currently, this is only supported for `LEAN_DB_PASSWORD`, `LEAN_EMAIL_SMTP_PASSWORD`, `LEAN_S3_SECRET`, and `LEAN_SESSION_PASSWORD`.

## Common Issues & Solutions

### Permission Issues
If you see "Operation not permitted" errors:
1. Ensure volumes are properly created
2. Check ownership of mounted directories
3. Run container as root (default) or properly configure user permissions

Fix permissions manually:

```
    docker exec -it leantime chown -R www-data:www-data /var/www/html/userfiles \ 
                                       /var/www/html/public/userfiles \ 
                                       /var/www/html/storage/logs \ 
                                       /var/www/html/app/Plugins
    docker exec -it leantime chmod -R 775 /var/www/html/userfiles \ 
                                       /var/www/html/public/userfiles \ 
                                       /var/www/html/storage/logs \ 
                                       /var/www/html/app/Plugins
    
```

### Database Connection Issues
1. Verify database credentials in .env file
2. Ensure database container is running and healthy
3. Check network connectivity between containers

### Plugin Installation Issues
1. Ensure the plugins volume is properly mounted
2. Check write permissions on the plugins directory
3. Verify plugin compatibility with your Leantime version

### Nginx/PHP-FPM Issues
1. Check logs: `docker logs leantime`
2. Verify port mappings
3. Ensure no conflicts with host ports

## Leantime Environment Variables
See sample.env for all available options. Critical variables:

```
LEAN_DB_HOST=mysql_leantime 
LEAN_DB_USER=lean 
LEAN_DB_PASSWORD=changeme123 
LEAN_DB_DATABASE=leantime  
LEAN_SESSION_PASSWORD=your_secure_password
```

## Security Considerations
1. Always change default passwords
2. Use Docker secrets for sensitive data
3. Consider running as non-root user
4. Enable HTTPS in production
5. Restrict network access appropriately

## Support & Documentation
- [Official Documentation](https://docs.leantime.io)
- [Discord Channel](https://discord.gg/4zMzJtAq9z)
- [GitHub Issues](https://github.com/Leantime/leantime/issues)

