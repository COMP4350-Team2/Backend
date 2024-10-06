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

## API Usage
GET /api/get_all_ingredients

Header parameters:
   key-name: value format ????

Body: What's required? Possibly we only have GET requests now so there won't be body yet

Respond Body: #if json, preferably json :giggle_giggle, face_with_hand_over_mouth:
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
