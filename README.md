# This is the README for the Backend

## Technologies To Be Used
### Backend API Server
- **Language:** python
- **Platform:** AWS Elastic Beanstalk
### Database
- **Engine:** Djongo
- **Platform:** Mongo Atlas
### Authentication
- **Platform:** Auth0

## Links To Other Repos
[Link to Desktop Webapp](https://github.com/COMP4350-Team2/Desktop-WebApp) <br/>
[Link to Mobile Webapp](https://github.com/COMP4350-Team2/Mobile-WebApp)

## Prerequisites
Have python version >= 3.12 and < 3.12.13 installed on machine

Install all the requirements by running:
```
pip install -r requirements.txt
```

## Environment Variables Instructions
- Download `SAMPLE.env` and rename it to `.env`. 
- Enter the required details. (Contact a member of the dev team for a copy of the proper file)

## Run
Run the following to run the Django server on the specified PORT in the `.env` file.
```
python manage.py runserver
```

## Profiling
To profile the API, set the environment variable `RUN_PROFILER=true`. This will turn on the profiler when running the service.
Profiler outputs are available in the `profiles/` directory which contains html files that you can open in the browser.

To profile the tests, run 
```
pyinstrument manage.py test
```

To profile an actual run, run the server with the following command:
```
pyinstrument manage.py runserver
```

## Cupboard API Usage
For the official API documentation, run the backend and go to one of the following links in your browser:  
Swagger UI: http://localhost:6060/api/[version]/doc/  
```
http://localhost:6060/api/v2/doc/
```  

Redoc UI: http://localhost:6060/api/[version]/redoc/  
```
http://localhost:6060/api/v2/redoc/
```

To test the user authentication required endpoints, click the **authorize** button and put your Auth0 access token.

## Docker Commands
build docker image
```
docker build -t cupboard_backend:latest .
```

upload .env to docker (manual .env change only) where "aws.pem" is the location of the pem file for aws auth
```
scp -i aws.pem -o StrictHostKeyChecking=no .env ec2-user@35.183.197.0:/home/ec2-user
```

run docker image 
```
docker run -p 6060:6060 --env-file .env cupboard_backend:latest
```

create docker image zip
```
docker save -o cupboard_backend.tar cupboard_backend:latest
```

load docker image zip
```
docker image load --input cupboard_backend.tar
```

push to dockerhub using default tag (latest)
```
docker push swanso15/cupboard_backend
```

pull to dockerhub using default tag (latest)
```
docker pull swanso15/cupboard_backend
```

## Locust Load Testing
1. Run the backend server if load testing on development. Otherwise, skip this step.
```
python manage.py runserver
```
2. Run locust in the command line in the base backend directory (where this file is found).
```
locust
```
3. A message similar to "Starting web interface at http://localhost:8089 (accepting connections from all network interfaces)" will appear in the command line. Copy the url that appears into the browser.
4. In the browser, enter the following values:  
**Number of Concurrent Users**: 100
**Number of Users per Second**: 1
**Host**: [AWS instance url or server url with port i.e. http://2.4.5.7:6060 (this is not the actual ip)]  

To remove load test values from the database:
1. Open the shell with the command:
```
python manage.py shell
```
2. In the shell, run:
```
exec(open('utils/db_helper/remove_load_test_values.py').read())
```
