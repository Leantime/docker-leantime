
<img src="https://leantime.io/logos/leantime-logo-transparentBg-landscape-1500.png" width="400"/>

# Leantime Docker #

Leantime is an open source project management system for small teams and startups written in PHP, Javascript using MySQL. [https://leantime.io](https://leantime.io)

This is the official <a href="https://hub.docker.com/r/leantime/leantime">Docker image for Leantime</a>. It was built using the <a href="https://github.com/Leantime/leantime/releases">latest Leantime release</a>.


## How to use this image

To run this image you will need an existing MySQL database. 

```
docker run -d -p 80:80 --network leantime-net \
-e DB_HOST=mysql_leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
--name leantime leantime/leantime:latest
```
Once started you can go to `<yourdomain.com>/install` and run the installation script.

## Full set up with MySQL and network

If you don't have a MySQL database set up and would like to create a container follow these instruction.

1. Create the network so Leantime can communicate with the MySql container.

```
docker network create leantime-net
```

2. Create the MySQL container.

```
docker run -d -p 3306:3306 --network leantime-net \
-e MYSQL_ROOT_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
--name mysql_leantime mysql:5.7 --character-set-server=utf8 --collation-server=utf8_unicode_ci
```

3. Create the Leantime container.

```
docker run -d -p 80:80 --network leantime-net \
-e DB_HOST=mysql_leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
--name leantime leantime/leantime:latest
```

4. Run the installation script at `<yourdomain.com>/install`

