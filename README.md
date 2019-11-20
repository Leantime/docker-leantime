
<img src="https://leantime.io/logos/leantime-logo-transparentBg-landscape-1500.png"/>

# Leantime Docker #

Leantime is an open source project management system for small teams and startups written in PHP, Javascript with MySQL. [https://leantime.io](https://leantime.io)

This is the git repository for the official <a href="https://hub.docker.com/r/leantime/leantime">Docker image for Leantime</a>. This image was built using the <a href="https://github.com/Leantime/leantime/releases">latest Leantime release</a>


## How to use this image

To launch this image you will need your MySQL database credentials. 

```
docker run -d -p 80:80 --network leantime-net \
-e DB_HOST=mysql_leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
--name leantime leantime/leantime:2.0
```
Once started you can go to `<yourdomain.com>/install` and run the installation script.

## Full set up with MySql and Network

If you don't have a mysql database set up and would like to create a container follow these instruction.

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
--name mysql_leantime mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

3. Create the Leantime container.

```
docker run -d -p 80:80 --network leantime-net \
-e DB_HOST=mysql_leantime \
-e MYSQL_USER=admin \
-e MYSQL_PASSWORD=321.qwerty \
-e MYSQL_DATABASE=leantime \
--name leantime leantime/leantime:2.0
```

4. Run the installation script at `<yourdomain.com>/install`

