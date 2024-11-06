# Cupboard by Team TeaCup

## Cupboard Meeting Minutes

[Meeting Minutes Word Document for Team Teacup](https://umanitoba-my.sharepoint.com/:w:/g/personal/seoa_myumanitoba_ca/ES0XvzVCruJMvQMZnQftuaMBZt7z6owPIiaymP5jdOUhIw?e=Qlf8kV)

## Cupboard Issue Tracking

Our team issue tracking is available in Linear. Please see UMLearn submission for the link.

## Architecture Diagram

![Architecture Diagram](/docs/images/sprint_2/Sprint_2_Architecture.jpg)

## Get Started Documentation

The Get started documentation is available in the README.md for each respective repository:  
[Backend Get Started](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#prerequisites)  
[Backend Get Started - with Docker](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#docker-commands)  
[Desktop Get Started](https://github.com/COMP4350-Team2/Desktop-WebApp#requirements)  
[Mobile Get Started](https://github.com/COMP4350-Team2/Mobile-Webapp#prerequisites)

## API Documentation

The API documentation is available following the information at the bottom in the backend README.md.  
[Link to API documentation](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#cupboard-api-usage)

The API documentation can also be accessed via putting the `schema.yml` file in the repository into https://editor.swagger.io/ However, you will not be able to test the API endpoints themselves via this method.

## Testing
### Regression Testing
#### Backend
All tests in the backend were created and ran using Django's testing tool along with the unittest library to mock the authentication access token.

To run the regression testing in the backend, we run the following command:
```
python manage.py test
```

The test script for APIs can be found in the [test_api.py file](https://github.com/COMP4350-Team2/Backend/blob/main/cupboard_app/test_api.py).  
The test script for the Database queries can be found in the [test_queries.py file](https://github.com/COMP4350-Team2/Backend/blob/main/cupboard_app/test_queries.py).

Last snapshot of the execution and results of the regression testing:
![Backend Regression Testing Results](/docs/images/sprint_2/backend_regression_testing.png)

#### Frontends
For the frontends, alongside acceptance tests for the new features, we always made sure to test related features which could possibly be impacted by new changes. This guarantees nothing is broken, all components are fully compatible and create a smooth user experience.

### Testing Slowdown
Overall, we have not created more than one test plan depending on the type of release and still following the same test plan as before.

#### Backend
In our CI/CD pipeline, we had to remove the unit test (test_queries.py) runs because it was taking too long (~10 mins). Instead, we are just running the integration tests (test_api.py). During development, we still run all tests, both unit tests and integration tests to make sure our changes did not break anything.

#### Desktop Frontend
The desktop frontend does not do unit tests or integration tests in this sprint. All acceptance tests for every user story, new and old, are tested after any additional functionality is added. That is, we manually run acceptance tests in a regression manner. 

#### Mobile Frontend
The mobile frontend does not do unit tests or integration tests in this sprint. Instead, the team kept the acceptance tests for each user story that was accomplished.

### Not Tested
#### Backend
![Backend Coverage Report](/docs/images/sprint_2/backend_coverage.png)

All components used for the API service and Database connection are fully tested. Two scripts (api_helper.py and env_helper.py) are mostly tested according to the coverage report because the functions that are not tested are not used for the API or database connection. These two are solely helper functions that developers in our group run to help with the development i.e. generating a new secret key.

#### Desktop Frontend
No unit tests for the desktop frontend because it only makes API calls to the backend which are tested in the backend itself. However, we will be adding unit testing for the mock backend in the next sprint since it is starting to increase in complexity as we add features. The mock backend mimics the behavior of the backend API so testing the mock would be a good alternative to testing with the actual backend.

#### Mobile Frontend
No unit tests for the mobile frontend because almost all the functionality in the frontend is dependent on API calls to the backend and those components are all tested in the backend. The frontend testing was deemed redundant. However, for the next sprint, the team has decided to introduce some unit tests that will be performed with the mocks. The team decided to include unit tests for the next sprint because the complexity of the mocks has developed to a point where doing unit tests will be good practice to ensure our mocks are correctly mimicking the real environment.

## Profiler
We use the pyinstrument library to run a profiler on our API.
The latest profiler run with an attempt to visit every endpoint is in the following folder:






## Last Dash
#### Backend
The backend may need some refactoring to accommodate adding images to our ingredients in next sprint, which could lead to the uncovering of some accumulated technical debt. Models will have to be changed, and migrations will need to be made along with some unknown conflicts that could arise.

The backend will also be having API calls to handle login, logout and signup with Auth0 for added security issues. See the Desktop frontend section for more information. 

#### Desktop Frontend
There were issues performing continuous delivery (CD) for the desktop frontend. The frontend relies on environment variables (specifically for Auth0) at runtime. Since the desktop frontend’s host machine is the user’s host machine, giving the users these environment variables become necessary to run a non-mock version. This is not secure since anyone who has these variables can decrypt any user’s Auth0 JWT token. Seeing as such, the desktop frontend will need to offload login/logout, registration and getting JWT token to a backend endpoint. Furthermore, testing needs to be added for the frontend as the complexity of the features increases.

#### Mobile Frontend
The team has yet to agree on a collection of elements for a user-friendly and appealing design of the UI (such as button layouts, color schemes, and such). The current implementation, although consistent, is still raw and needs a more solid backbone. One of our next important tasks is to carry out a major UI change to create a consistent, modernized look, following our UI draft. Additionally, as mentioned earlier, the complexity of the mocks has been steadily increasing with each sprint. The team has therefore decided that the best practice for robustness would be to introduce unit tests and automated acceptance tests in the next sprint.

## Showoff

### Agape

### Ahmed

### Hien

### Jethro

### Sam

### Vaughn
