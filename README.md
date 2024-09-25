# Django Scalable Tracking Number API with HAProxy, Redis, and PostgreSQL

## Overview

This project is a scalable API for generating unique tracking numbers, designed using Django REST Framework. The architecture is optimized for high concurrency and includes the following components:

- **HAProxy Load Balancer**: Distributes HTTP requests across multiple Django app instances.
- **Redis**: Acts as a caching layer to improve performance.

## Features

- Generates unique tracking numbers based on various parameters.
- Redis cache for improved performance.
- Load-balanced across multiple Django instances using HAProxy.

## Prerequisites

Ensure that you have the following software installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo/tracking-api.git
cd tracking-api
```

### Step 2: Environment Variables
Create a .env file in the project root and add the following environment variables:

```bash
DEBUG=True
DATABASE_URL=postgres://myuser:mypassword@db-master:5432/mydatabase
SLAVE_DATABASE_URL=postgres://myuser:mypassword@db-slave:5432/mydatabase
REDIS_URL=redis://redis:6379/1
SECRET_KEY=your-secret-key
```
### Step 3: Build and Run the Application with Docker Compose
The application is designed to run in multiple containers using Docker Compose. This includes:


- redis: Redis instance for caching.
- web1, web2: Django app instances.
- haproxy: Load balancer for distributing requests between Django app instances.

Build and Start the Application

```bash
docker-compose up --build
```

Docker Compose will:

- Build the Django app containers.
- Launch the Redis cache.
- Start the HAProxy load balancer.
- You should now have the application running on http://localhost:8000.

### Step 4: Apply Database Migrations
Once the containers are running, you need to apply the migrations:

```bash
docker-compose exec web1 python manage.py migrate
docker-compose exec web2 python manage.py migrate
```

### Step 5 : Accessing the API
The API can be accessed via:

Tracking Number Generation:
``` perl
GET http://localhost:8000/next-tracking-number/?origin_country_id=MY&destination_country_id=ID&weight=1.234&created_at=2018-11-20T19:29:32+08:00&customer_id=de619854-b59b-425e-9db4-943979e1bd49&customer_name=RedBox%20Logistics&customer_slug=redbox-logistics
```

### Redis Cache Configuration
Redis is configured as the cache backend for Django. The CACHES setting in settings.py ensures Redis is used to cache database queries and other expensive operations. To customize the cache configuration:

``` python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  # Refers to the Redis container
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### HAProxy Load Balancer
The HAProxy instance balances HTTP traffic between multiple Django instances. The HAProxy configuration is located in the haproxy.cfg file:

``` txt
frontend http-in
    bind *:8000
    default_backend django_backend

backend django_backend
    balance roundrobin
    server web1 web1:8000 check
    server web2 web2:8000 check
```



### Scaling the Application
To scale the number of Django instances (e.g., for high-traffic scenarios), simply update the docker-compose.yml file:

```yaml
# Add more instances as needed
  web3:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8003:8000"
    depends_on:
      - db
      - redis
    networks:
      - app-network
```
After updating, re-run:

``` bash
docker-compose up --build
```

### Deploying to Heroku
To deploy the application to Heroku, follow these steps:

1. Setup Heroku App for Docker
First, make sure the Heroku CLI is installed and logged in:

``` bash
heroku login
```
2. Create a Heroku App
You can create a Heroku app via CLI, specifying that you’ll be using Docker:

```bash
heroku create tracking_api   s --stack=container
```

This sets up your Heroku app to use Docker.

3. Use Heroku Postgres and Redis Add-ons
Since Heroku doesn’t support docker-compose, you can use Heroku's managed Postgres and Redis services instead of running them in containers.

Add the required Heroku Postgres and Redis add-ons:

```bash
heroku addons:create heroku-postgresql:hobby-dev --app tracking_api
heroku addons:create heroku-redis:hobby-dev --app tracking_api
```

These commands provision PostgreSQL and Redis instances on Heroku, which you can connect to your Django app.

4. Configure Django to Use Heroku's Databases
In your settings.py, adjust the database and cache configurations to use Heroku’s environment variables. Heroku automatically provides the database URL and Redis URL via environment variables.

Update your settings.py to:

```python
import os
import dj_database_url

# Use Heroku Postgres
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Use Heroku Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

5. Modify Dockerfile for Heroku
Heroku uses a single Dockerfile for building your web app. Ensure you have a Dockerfile that correctly sets up your Django app.

Example Dockerfile:

```Dockerfile
# Use the official Python image from the DockerHub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Run migrations and collect static files
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Start the Django app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tracking_api.wsgi:application"]
```
6. Heroku Procfile
Heroku requires a Procfile to tell it how to run your application. This can be used to run gunicorn instead of the Django development server:

Create a Procfile with the following content:

``` bash
web: gunicorn tracking_api.wsgi --log-file -
```

7. Deploy to Heroku
Commit your changes and push the Docker image to Heroku:

```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku master
```

This will build and deploy the Docker image to Heroku.

8. Scaling with Multiple Dynos
Since Heroku doesn't support docker-compose, you'll scale the web dynos (running your Django app) directly via Heroku.

Scale the app to use multiple web dynos (effectively what web1 and web2 were in the Docker Compose file):

```bash
heroku ps:scale web=2 --app tracking_api
```
This command scales the web process to two dynos, which Heroku will load balance across automatically.

9. Check Your Deployment
Visit the app URL provided by Heroku or check logs to ensure everything is running correctly:

```bash
heroku logs --tail --app tracking_api
```