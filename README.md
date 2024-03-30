## Train Station API Service

Train Station API Service is a web application built with Django REST Framework offering a platform
for managing and accessing data related to train stations, It provides APIs for various functionalities
like creating, listing, filtering and managing train stations, train, trips, orders.

## Features
* Unauthenticated users can't do anything
* Authenticated users can list and retrieve resource, except user can create order and ticket
* Superuser (admin, staff) can create every resource, list and retrieve
* Secure authenticated system. Train Station API provides registration anda JWT
    (JSON Web Token) authentications. Users register then login for obtaining JWT
    access token to authenticate themselves and refresh token for refreshing access
    token when it is expired
* Users can filter trains by train type and name
* Users can filter trips by trip route and departure date
* Users can upload images for crew members
* API documentation 
* Admin panel /admin/

## Installation
1. Clone git repository to your local machine:
```
    git clone https://github.com/MilArtem78/train_station_API_service.git
```
2. Copy the `.env.sample` file to `.env` and configure the environment variables
```
    cp .env.sample .env
```
3. Run command. Docker should be installed:
```
    docker-compose up --build
    docker-compose up
```
4. You can use the following test credentials:
#### Test superuser:
- **Email** admin_test@gmail.com
- **Password** admin_test
#### Test user:
- **Email** user_test@gmail.com
- **Password** user_test

It is recommended to create your own user accounts fot production use.

### Usage
To access the API, navigate to http://localhost:8000/api/ in your web browser and enter one of endpoints.

### Endpoints
Train Station API endpoints 
- `/train_station/`
- `/train_station/stations/`
- `/train_station/train_types/`
- `/train_station/crews/`
- `/train_station/trains/`
- `/train_station/orders/`
- `/station/routes/`
- `/train_station/trips/`

User API endpoints:
- `/user/register/`
- `/user/token/`
- `/user/token/refresh/`
- `/user/token/verify/`

Admin (superuser) endpoint:
- `/admin/`

Documentation:

- `/doc/swagger/`: To access the API documentation, you can visit the interactive Swagger UI.
