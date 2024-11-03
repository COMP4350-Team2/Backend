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
`pip install -r requirements.txt`

## Environment Variables Instructions
- Download `SAMPLE.env` and rename it to `.env`. 
- Enter the required details. (Contact a member of the dev team for a copy of the proper file)

## Run
Run the following to run the Django server on the specified PORT in the `.env` file.
`python manage.py runserver`

The previous is for running a locally hosted instance, for running in production on a hosted server in aws or elsewhere are required (not applicable for current development).

## Profiling
To profile the API, set the environment variable `RUN_PROFILER=true`. This will turn on the profiler when running the service.
Profiler outputs are available in the `profiles/` directory which contains html files that you can open in the browser.

To profile the tests, run `pyinstrument manage.py test`

## Cupboard API Usage
For the official API documentation, run the backend and go to one of the following links in your browser:  
Swagger UI: http://localhost:6060/api/<version>/doc/  
```http://localhost:6060/api/v2/doc/```  
Redoc UI: http://localhost:6060/api/<version>/redoc/
```http://localhost:6060/api/v2/redoc/```

To test the user authentication required endpoints, click the **authorize** button and put your Auth0 access token.
