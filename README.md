
<img src="https://leantime.io/logos/leantime-logo-transparentBg-landscape-1500.png" width="400"/>

# Leantime&trade; Docker

[![License Badge](https://img.shields.io/github/license/leantime/leantime?style=flat-square)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
[![Version](https://img.shields.io/github/package-json/v/leantime/leantime/master?style=flat-square)](https://github.com/Leantime/leantime/releases)
[![Docker Hub Badge](https://img.shields.io/docker/pulls/leantime/leantime?style=flat-square)](https://hub.docker.com/r/leantime/leantime)
[![Discord Badge](https://img.shields.io/discord/990001288026677318?label=Discord&style=flat-square)](https://discord.gg/4zMzJtAq9z)
<br />

Leantime is an open source project management system for small teams and startups written in PHP, Javascript using MySQL. [https://leantime.io](https://leantime.io)

This is the official <a href="https://hub.docker.com/r/leantime/leantime">Docker image for Leantime</a>. It was built using the <a href="https://github.com/Leantime/leantime/releases">latest Leantime release</a>.

## How to use this image
Below you will find examples on how to get started with Leantime trough `docker run` or `docker compose`.

### Full Set up with docker-compose

One command install with docker compose.

```
git clone https://github.com/Leantime/docker-leantime.git
cd docker-leantime
cp sample.env .env
docker compose up -d
```

Dont forget to update the `.env` file for production.

### Full set up with docker run

#### 1. Create the network so Leantime can communicate with the MySql container.

```
docker network create leantime-net
```

#### 2. Create the MySQL container.
If you don't have a MySQL database set up and would like to create a container follow these instruction, otherwise jump to step 3.

```
docker run -d --restart unless-stopped -p 3306:3306 --network leantime-net \
-e MYSQL_ROOT_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
--name mysql_leantime mysql:8.0 --character-set-server=UTF8MB4 --collation-server=UTF8MB4_unicode_ci
```

#### 3. Create the Leantime container.

```
docker run -d --restart unless-stopped -p 80:80 --network leantime-net \
-e LEAN_DB_HOST=mysql_leantime \
-e LEAN_DB_USER=admin \
-e LEAN_DB_PASSWORD=321.qwerty \
-e LEAN_DB_DATABASE=leantime \
--name leantime leantime/leantime:latest
```

4. Run the installation script at `<yourdomain.com>/install`

## Full Set up with docker-compose

One command install with docker-compose.

```sh
git clone https://github.com/Leantime/docker-leantime.git
cd docker-leantime
cp sample.env .env
nano .env    # Change the secrets for security
docker-compose up -d
```

## Docker secrets

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

### Support ###
* Documentation [https://docs.leantime.io](https://docs.leantime.io)
* Community Forum [https://community.leantime.io](https://community.leantime.io)
* Discussions on [Discord](https://discord.gg/4zMzJtAq9z)
* File a bug report [https://github.com/Leantime/leantime/issues/new](https://github.com/Leantime/leantime/issues/new)
