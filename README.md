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

You may get a Userwarning if you do not have any static files. This is the expected behaviour and should not affect running the development server. If you want to avoid the warning, run the command below beforehand.  
Note: you will get a folder containing several static files after running this command:
```
python manage.py collectstatic
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
http://localhost:6060/api/v3/doc/
```  

Redoc UI: http://localhost:6060/api/[version]/redoc/  
```
http://localhost:6060/api/v3/redoc/
```

To test the user authentication required endpoints, click the **authorize** button and put your Auth0 access token.

## Docker Commands
To build and run the docker image in development, you will only need to run the following command:
```
docker compose up --build
```

For manual docker commands for AWS, please see the following commands below:  
Build the docker image:
```
docker compose build
```

Tag the docker image:
```
docker tag cupboard_backend:latest teacupbackend/cupboard_backend:latest
```

Push the image to dockerhub using "latest" tag
```
docker push teacupbackend/cupboard_backend:latest
```

Upload .env to docker (manual .env change only) where "aws.pem" is the location of the pem file for aws auth
```
scp -i aws.pem -o StrictHostKeyChecking=no .env ec2-user@3.99.18.11:/home/ec2-user
```

In AWS, either through the AWS EC2 container console or via ssh:  
Pull the image from dockerhub using "latest" tag
```
docker pull teacupbackend/cupboard_backend:latest
```

Stop the current containers
```
docker ps -a -q | xargs -r docker stop
```

Remove the current containers
```
docker ps -a -q | xargs -r docker remove
```

Run docker image 
```
docker run -d -p 6060:6060 --env-file .env teacupbackend/cupboard_backend:latest
```
