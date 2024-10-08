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

## Cupboard API Usage

### Get all ingredients
```http
GET /api/get_all_ingredients
```
Header parameters:
- HTTP_AUTHORIZATION: "Bearer [auth0 token]"
  - Replace [auth0 token] with access token provided after user completes Auth0 login

Success Response:
```
{
   "result": [
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
```

### Create user
```http
POST /api/create_user
```
Header parameters:
- HTTP_AUTHORIZATION: "Bearer [auth0 token]"
  - Replace [auth0 token] with access token provided after user completes Auth0 login

Success Response:
```
{
   "result": "Item created successfully."
}
```
Or
```
{
   "result": "Item already exists."
}
```
