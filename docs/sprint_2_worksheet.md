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
The latest profiler results with an attempt to visit every endpoint is located in the [docs/sprint_2_profiler](docs/sprint_2_profiler).

The slowest endpoint is the `api/v2/user_list_ingredients/set_ingredient`. The reason being it is calling the database twice the amount another endpoint would as it is editing two different objects in the database wheras other endpoints are just editing one object in the database.

This could be possibly fixed by making the save run once instead of twice by using something similar to django bulk_commit command or transaction command, hence sending the database request once. But this is something that needs to be explored as this command from Django might not work well with the Mongo database (our current setup).

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

My best work is the API design to update the ingredients in our user's ingredients lists. Our user_ingredients_lists is one of the most complex object in terms of database handling and the number of various API requests a user needs. This implementation was the third version after going through several discussions with the group especially the frontends' needs. Previously, we had made it so that there was only one API endpoint to add, delete, or set a user's ingredients in the lists and it would change what action it was doing depending on the sender's body request. However, this would result in way too many checks for one endpoint and a drastic slowdown to run one endpoint. With this commit, I was able to separate the APIs into three different calls in order to make it a single responsibility and the API calls became much faster. Additionally, the API became easier to use.  
[Link to the API part of the change](https://github.com/COMP4350-Team2/Backend/blob/3230457caffed596ea62c2f88346c56636714423/cupboard_app/views.py#L246-L502).  
[Link to the Database queries to handle the API](https://github.com/COMP4350-Team2/Backend/blob/3230457caffed596ea62c2f88346c56636714423/cupboard_app/queries.py#L246-L405).

Note: After the commits in the links, some additional commits happened to fix any bugs.

### Ahmed

Added caching to the backend concrete implementation. API calls are only made initially and then every 5 minutes. Cached values returned otherwise. Updates, puts, adds or removes to the backend state is reflected in the instance variables. Made the backend calls much faster. The desktop front-end is to be used at home so eventual consistency is acceptable here. The "refresh time" can be easily modified to adjust consistency and concurrency needs. [Link to file diff](https://github.com/COMP4350-Team2/Desktop-WebApp/commit/adec1fe094054da4697dc39e5cd9165ad7b58011#diff-4c8075b4448df5037b73f539d020d590520363b9466be2752c69e589618bb7d7R16-R498).

### Hien

Create a Loading screen for a smooth, responsive, and engaging user experience. A few places in our app had been leaving an idle gap where the authentication is processed, page transitions, or data APIs fetching. By adding this Loading screen, I was able to help enhance the app experience, and still adding a small branding touch with the team’s logo in the background.
[Pull Request #25](https://github.com/COMP4350-Team2/Mobile-Webapp/pull/25) > [Commit](https://github.com/COMP4350-Team2/Mobile-Webapp/pull/25/commits/9ac801c33c636247c10075d1bad7c2f6bdb23e54)

### Jethro

Set up docker to run the backend server in a containerized fashion. The actual code is disappointingly simple for the amount of headache that went into getting this thing functional but it is what I am most proud of for this sprint due do how complex the proccess to get here was. https://github.com/COMP4350-Team2/Backend/blob/59dac849baf4d700b368d1ae43eb9e40bdd6fbdc/Dockerfile#L1-L22

### Sam

In our app, one of the things a user can do is move any given ingredient from one list to another. This is done so that a user can move an ingredient from let’s say Grocery to Pantry (if the user just purchased an ingredient they wanted). Our backend did not have an API endpoint for updating ingredients. Therefore, I had to do a combination of removing the ingredient from the current list and adding it to another. However, at any point, the API request for either removing or adding can fail and I think I came up with a pretty cool way of doing a soft rollback in case anything fails. The method I designed can be found [here](https://github.com/COMP4350-Team2/Mobile-Webapp/blob/9f3c70d1cb6e189503344782680457144bf060f1/src/services/Backend.ts#L249-L303). Nothing too special; just proud of its robustness.

### Vaughn

I would consider this update list ingredient query my best code because it encapsulates my work with the schema and database design, showcasing how all the different mongo collections work together and connect with our backend. It works with all major document types from the database, including the ingredients, user lists and users. Additionally, the checks are efficient and consistent, all exceptions are handled when lists don’t exist, or ingredients can’t be updated. The documentation of this code is also clear, the docstring provides a clear and concise description of what the function does and what the arguments are. [Link to the code.](https://github.com/COMP4350-Team2/Backend/blob/066349abcc7d39e781a4944ff24e2bb7998a6b76/cupboard_app/queries.py#L294-L355)
