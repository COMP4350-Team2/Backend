# Cupboard Backend
This repository contains the code for the Cupboard App backend. It was developed as a group project for the University of Manitoba Fall 2024 COMP 4350 class by Team 2 - Teacup.  

By running this code, you will have access to the Cupboard App API documentation and the API endpoints.

To go to the deployed Cupboard App API go to https://teacup-cupboard-api.me/api/v3/doc

Links to the other repositories can be found below:
- [Link to Desktop Webapp](https://github.com/COMP4350-Team2/Desktop-NativeApp)  
- [Link to Mobile Webapp](https://github.com/COMP4350-Team2/Mobile-WebApp)

## Table of Contents
- [Background](#background)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Other Development Command](#other-development-commands)
- [Contributors](#contributors)
- [License](#license)

## Background
The Cupboard App was developed to be the ultimate kitchen companian that takes the hassle out of meal planning and grocery management.  

The features include:
- A list of common ingredients users can add to their lists.
- The ability to create custom ingredients.
- The ability to manage lists of ingredients.
- The ability to create recipes.

## Technologies Used
### API Server:
- **Language:** Python
- **Platform:** AWS EC2 Instance
### Database
- **Engine:** Djongo
- **Platform:** MongoDB Atlas
### Authentication
- **Platform:** Auth0

## Getting Started
### Requirements
Python version >= 3.12 and < 3.12.13 installed on machine.  
Pip installed on machine.

Install all the repository requirements by running:
```
pip install -r requirements.txt
```

### Environment Variables
- Download `SAMPLE.env` and rename it to `.env`. 
- Enter the required details. (Contact a member of the dev team for a copy of the proper file).

### Run
You may get a userwarning if you do not have any static files. This is the expected behaviour and should not affect running the development server. If you want to avoid the warning, run the command below before running the server.  
Note: you will get a folder containing several static files after running this command:
```
python manage.py collectstatic
```

To run the server on a Django development server on the specified PORT in the `.env` file run
```
python manage.py runserver
```
or run the server on gunicorn production server using docker
```
docker compose up --build
```

## Usage
### API documentation
For the official API documentation, run the backend and go to one of the following links in your browser:  
Swagger UI: http://localhost:6060/api/[version]/doc/  
```
http://localhost:6060/api/v3/doc/
```  

Redoc UI: http://localhost:6060/api/[version]/redoc/  
```
http://localhost:6060/api/v3/redoc/
```

To test the user authentication required endpoints, click the **authorize** button and put your Auth0 access token.  

The API documentation can also be accessed via putting the `schema.yml` file in the repository into https://editor.swagger.io/ However, you will not be able to test the API endpoints themselves via this method.

### Running the API endpoints
To run the actual endpoints, send HTTP requests to the url with the correct request type and parameters (if applicable) following the API documentation. i.e.
```
curl --request GET ^
--url http://localhost:6060/api/v3/ingredients \
--header "Authorization: Bearer [access_token]"
```

## Other Development Commands
### Profiling
For profiling, we use pyinstrument.  
To profile the API, set the environment variable `RUN_PROFILER=true`. This will turn on the profiler when running the server.
Profiler outputs are available in the `profiles/` directory which contains html files that you can open in the browser.

To profile the tests, run 
```
pyinstrument manage.py test
```

To profile an actual run, run the server with the following command:
```
pyinstrument manage.py runserver
```

### Load Testing
For load testing, we use locust.
#### Run Load Test
1. If load testing on development, run the server locally by running the command under [run section](#run). Otherwise, skip this step.
2. Run locust in the command line in the base backend directory (where this file is found).
   ```
   locust
   ```
3. A message will appear in the command line. i.e. "Starting web interface at http://localhost:8089 (accepting connections from all network interfaces)." Copy the url that appears in the message into the browser.
4. In the browser, enter the following values:  
**Number of Concurrent Users**: 100  
**Number of Users per Second**: 1  
**Host**: [AWS instance url or server url with port i.e. http://2.4.5.7:6060 (this is not the actual ip)]  

#### Remove Load Test Values from the Database
1. Open the shell with the command:
   ```
   python manage.py shell
   ```
2. In the shell, run:
   ```
   exec(open('utils/db_helper/remove_load_test_values.py').read())
   ```

### Docker Commands
#### Build and Run Docker in Development
To build and run the Docker image in development, you will only need to run
```
docker compose up --build
```

#### AWS Manual Uploads
For manual docker commands for AWS, please see the following commands below:  
1. Build the docker image:
   ```
   docker compose build
   ```
2. Tag the docker image:
   ```
   docker tag cupboard_backend:latest teacupbackend/cupboard_backend:latest
   ```
3. Push the image to dockerhub using "latest" tag
   ```
   docker push teacupbackend/cupboard_backend:latest
   ```
4. Upload .env to docker (manual .env change only) where "aws.pem" is the location of the pem file for aws auth
   ```
   scp -i aws.pem -o StrictHostKeyChecking=no .env ec2-user@3.99.18.11:/home/ec2-user
   ```
5. Connect to the AWS EC2 container either through the AWS dashboard console or via ssh where "aws.pem" is the location of the pem file for aws auth
   ```
   ssh -i aws.pem ec2-user@3.99.18.11
   ```
6. In the AWS console, pull the image from Dockerhub using the "latest" tag
   ```
   docker pull teacupbackend/cupboard_backend:latest
   ```
7. Stop the current containers
   ```
   docker ps -a -q | xargs -r docker stop
   ```
8. Remove the current containers
   ```
   docker ps -a -q | xargs -r docker remove
   ```
9. Run docker image 
   ```
   docker run -d -p 6060:6060 --env-file .env teacupbackend/cupboard_backend:latest
   ```

## Contributors
This project exists thanks to all the people who contributed.  
<a href="https://github.com/COMP4350-Team2/Backend/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=COMP4350-Team2/Backend" />
</a>

Image made with [contrib.rocks](https://contrib.rocks).

## License
[GNU GENERAL PUBLIC LICENSE](LICENSE) © Teacup (COMP4350-Team2)
