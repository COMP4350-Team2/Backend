# Cupboard by Team TeaCup

## Cupboard Meeting Minutes
[Meeting Minutes Word Document for Team Teacup](https://umanitoba-my.sharepoint.com/:w:/g/personal/seoa_myumanitoba_ca/ES0XvzVCruJMvQMZnQftuaMBZt7z6owPIiaymP5jdOUhIw?e=Qlf8kV)

## Cupboard Issue Tracking
Our team issue tracking is available in Linear. Please see UMLearn submission for the link.

## Architecture Diagram

![Architecture Diagram](/docs/images/sprint_1/Sprint_1_Architecture.jpg)

## Get Started Documentation
The Get started documentation is available in the README.md for each respective repository:  
[Backend Get Started](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#prerequisites)  
[Desktop Get Started](https://github.com/COMP4350-Team2/Desktop-WebApp#requirements)  
[Mobile Get Started](https://github.com/COMP4350-Team2/Mobile-Webapp#prerequisites)  

## Sequence Diagrams

### Login/Registration
![Login/Registration sequence diagram](/docs/images/sprint_1/login_registration_sequence_diagram.png)

### Get All Ingredients
![Get all ingredients sequence diagram](/docs/images/sprint_1/get_all_ingredients_sequence_diagram.png)

## API Documentation
The API documentation is available at the bottom in the backend README.md.  
[Link to API documentation](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#cupboard-api-usage)

## Testing Plan

Add testing plan description







### Unit/Integration/Acceptance Test
#### **Backend**:
Code and Line Coverage:
![Code and Line Coverage Image](/docs/images/sprint_1/sprint_1_coverage.png)
- Our APIs are in the `views.py` and it doesn’t have 100% coverage because: 
  - Line 41 is a validator and that is already tested in the `tests.py` via the public, private, and private-scoped class tests
  - Note: the test for create_user api for the case when email is not available in the payload was added later in the day on October 9, 2024. [Link to pull request](https://github.com/COMP4350-Team2/Backend/pull/13)
- Our logic code is in the `queries.py` and the `views.py` both of which have over 80% coverage 
- Our Integration tests are with the APIs in the `views.py` as mentioned above
#### **Frontend**:
For this sprint, the team’s primary focus (as per the client’s expectations) was to implement Authorization, Authentication, and Accounting (AAA). With that implemented (using Auth0), the team only had the capacity to finish a part of one of their features. As a result, there were a total of two methods (in both frontends) that had logic. Both of these methods exist only in the Backend/Services classes that are used to fetch responses from our API endpoints. The two methods are as follows:
- **User Creation**

  The team made the decision to use Auth0 for authentication and authorization. However, the accounting part had to be manually implemented. The team achieved accounting by fetching a response from our API endpoint (localhost:6060/api/create_user). This endpoint essentially sends a query to the database (and is tested in the backend) to create a new user. This query only adds a user to our Users table if the user with their access token (retrieved from Auth0) is not already in the table. Since this query and method is tested in the back-end, the team did not deem it necessary to test it in the front-end.
- **Getting all ingredients**

  This method, as above, fetches a response from our API endpoint (localhost:6060/api/get_all_ingredients) which includes all the ingredients made available to the user. This method, as above, is tested in the back-end and therefore the team did not explicitly test it in the front-end.

However, the team instead decided to follow the acceptance criteria for the User Stories the team was able to finish (present in both the front-ends’ README) and simulated (with instructions) the acceptance criteria. The expected behavior is also stated in the READMEs.

### Testing importance
#### Unit Testing:
- [test_create_ingredient() function](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L106-L118)
  - Tests if when create_ingredient() function is called with an ingredient name and type as arguments that the corresponding ingredient document exists in our mongo atlas database. 
- [test_get_all_ingredients() function](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L90-L104)
  - Tests if when get_all_ingredients() function is called that all ingredient documents that exist in our mongo atlas database are fetched and stored in a list.
- [test_create_list_ingredient() function](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L268-L289)
  - Tests if when create_list_ingredient() function is called that a dictionary object for that ingredient is created with the ingredient name, amount and unit included and correct.
#### Integration Testing:
- [PrivateMessageApi() class](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L312-L347)
  - Tests how the calls to private api (need to be authenticated) work if you have or do not have the access token or if you have or do not have the correct access token.
- [GetAllIngredientsApi() class](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L389-L416)
  - Ensures calls to the Get all ingredients api verifying all expected items are being returned in json format.
- [CreateUser() class](https://github.com/COMP4350-Team2/Backend/blob/83843c00dca66766e135d3503f20aa3bfad5f7d8/cupboard_app/tests.py#L419-L484)
  - Tests how the calls to the create_user api work if you have or do not have the access token and whether the access token has a valid username and email or if the user already exists in the database.
#### Acceptance Testing:
For the acceptance testing and their related user story, please look at the acceptance testing documents in the respective repositories' README.md.  
[Desktop-frontend](https://github.com/COMP4350-Team2/Desktop-WebApp/blob/main/README.md#acceptance-tests)  
[Mobile-frontend](https://github.com/COMP4350-Team2/Mobile-Webapp?tab=readme-ov-file#acceptance-tests)

## Reproducible environments
Team Cupboard (Team 2) tested the development environment to Team 3

Add testing results





