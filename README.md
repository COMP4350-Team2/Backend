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
Have python veraion 3.12 or greater installed on machine

Install all the requirements by running:
`pip install -r requirements.txt`

## Environment Variables Instructions
- Download `SAMPLE.env` and rename it to `.env`. 
- Enter the required details. (Contact a member of the dev team for a copy of the proper file)

## Run
Once all the Prerequsites and Dependencies are installed and the environment variables are set, run the following to apply all changes to the db:
`python manage.py migrate`

Then run the following to run the Django server on the specified PORT in the `.env` file.
`python manage.py runserver`

The previous is for running a locally hosted instance, for runing in production on a hosted server in aws or elsewhere are requiered (not applicable for current development)

## API Usage
GET /api/get_all_ingredients

Header parameters:
    HTTP_AUTHORIZATION:"Bearer [auth0 token]" # replace [auth0 token] with token provided after user completes auth0 login

Respond Body:
   {
      "result":[
        {
            "name":"ingredient_1"
            "type":"ingredient_type"
        },
        {
            "name":"ingredient_2"
            "type":"ingredint_type2"
        }
      ]
   }
