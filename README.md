# This is the README for the Backend

## Technologies To Be Used
### Backend API Server
- **Language:** python
- **Platform:** AWS Elastic Beanstalk
### Database
- **Engine:** PostgreSQL
- **Platform:** MS Azure
### Authentication
- **Platform:** Auth0

## Links To Other Repos
[Link to Desktop Webapp](https://github.com/COMP4350-Team2/Desktop-WebApp) <br/>
[Link to Mobile Webapp](https://github.com/COMP4350-Team2/Mobile-WebApp)

## Prerequisites
Install all the requirements by running:
`pip install -r requirements.txt`

## Environment Variables Instructions
- Download `SAMPLE.env` and rename it to `.env`. 
- Enter the required details.

## Run
Once all the Prerequsites and Dependencies are installed and the environment variables are set, run the following to apply all changes to the db:
`python manage.py migrate`

Then run the following to run the Django server on the specified PORT in the `.env` file.
`python manage.py runserver`
