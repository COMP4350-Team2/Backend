# Cupboard by Team TeaCup

## Cupboard Meeting Minutes

[Meeting Minutes Word Document for Team Teacup](https://umanitoba-my.sharepoint.com/:w:/g/personal/seoa_myumanitoba_ca/ES0XvzVCruJMvQMZnQftuaMBZt7z6owPIiaymP5jdOUhIw?e=Qlf8kV)

## Cupboard Issue Tracking

Our team issue tracking is available in Linear. Please see UMLearn submission for the link.

## Architecture Diagram

![Architecture Diagram](/docs/images/sprint_3/Sprint_3_Architecture.jpg)

## Get Started Documentation

The Get started documentation is available in the README.md for each respective repository:  
[Backend Get Started](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#prerequisites)  
[Desktop Get Started](https://github.com/COMP4350-Team2/Desktop-NativeApp#requirements)  
[Mobile Get Started](https://github.com/COMP4350-Team2/Mobile-Webapp#prerequisites)

## API Documentation

The API documentation is available following the information at the bottom in the backend README.md.  
[Link to API documentation](https://github.com/COMP4350-Team2/Backend?tab=readme-ov-file#cupboard-api-usage)

The API documentation can also be accessed via putting the `schema.yml` file in the repository into https://editor.swagger.io/ However, you will not be able to test the API endpoints themselves via this method.

## Load Testing
Link to the Load Test document in the folder

Describe the environment for load testing, such as tool, load test cases.  
- We used Locust (https://locust.io/) to do the testing and tested all api endpoints users would be expected to have access to when performing regular function. Here is a link to our locust file defining the tests [INSERT LINK TO OUR LOCUSTFILE IN GITHUB] 

provide the test report for load testing.  
- Report is proviced, named Load_test_report.txt in this directory

discuss one bottleneck found in the load testing.  
- Patch requests sent to /api/v3/user/lists/ingredients to change an ingredient in a users list took over 35.5 seconds on average, according to the load test output, which was the longest of all requests. 

Load testing should test the non-functional requirements - did you meet your goals? Why or why not? Could you meet your goals with money? 
- We were not able to meet the non-funtional requirement of having a response time of less than 1s when having 100 concurrent users. This is likely because of the machine we are running the backend is the smallest possible allowed by AWS (its free), and as such thier are likely limitations on its capability. Money would likely allow us to do this as it would not just allow for faster machines but also to build out faster surrounding architecture. 

## Security Analysis
Link to the Security Report

Describe the choice of the security analysis tool and how do you run it. The security analysis tool should analyze the language that is used in the majority of your source code. 
- We used Bandit to do static analysis of our code. To run it, first install it with `pip install bandit` then run the following at the top of the project directory `bandit -r . > bandit_security_analysis.txt` to run it recursivly on all files in this and all sub-directories. 

Attach a report as an appendix below from static analysis tools by running the security analysis tool on your source code. Randomly select 5 detected problems and discuss what you see. Note that you are not required to fix the alarms (bugs and vulnerabilities) in the course. 
- Security report provided in Bandit_security_analysis.txt , no high or critical problems were found. There were only 6 issues in total, most of the other medium or low priority problems was it suspecting things like access_token = “ “ was us storing credentials in plain text and not realizing these were default placeholder values (it makes a similar mistake thinking a variable holding a date-time format for a string was actually plain text security credentials). The other kind of error was noting that we may not be sending time out requests with some of our auth0 requests 

Handle (or mitigate) all Critical and High priority vulnerabilities in the project. Attach commits where these are handled. If there are no critical or high vulnerabilities, discuss 2 other problems found. 
-  No critical/high problems found, other problems included “Possible hardcoded password: ''” thinking that ‘’ could be a hardcoded password (its just an empty default or “Possible hardcoded password: '%Y-%m-%d %H:%M:%S'” again mistakenly identifying a date-time format string as a hardcoded password. 

## Continuous Integration and Deployment (CI/CD)
### Backend
We use GitHub actions for the CI/CD in the backend repository. We have two GitHub Actions .yml files. One for the CI and the other for the CD. They are set to run when there is a push to main or if it is triggered manually. If the former method is used, then the CD pipeline waits for the CI to succeed before executing. Otherwise the CD will not run.  

The CI/CD pipeline files can be found in the [.github workflows directory](/.github/workflows).  
A snapshot of the CI/CD execution can be found under the Actions tab at the top of this page: https://github.com/COMP4350-Team2/Backend/actions

### Desktop Native App
CI/CD environment and clickable link to the pipeline.

Provide link to the workflow

Snapshots of the CI/CD execution

### Mobile Web App
For the Mobile WebApp, the team decided to use Github actions for CI/CD as well. There are a total of two **(2)** files responsible for CI and CD:
- [mobile_ci.yml](https://github.com/COMP4350-Team2/Mobile-Webapp/blob/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows/mobile_ci.yml): This file triggers (our CI) on every push to `main` and ensures the build is successful followed by pushing our Docker image to Dockerhub. 
- [deploy.yml](https://github.com/COMP4350-Team2/Mobile-Webapp/blob/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows/deploy.yml): This file triggers (our CD) on every `release` of the WebApp and ensures that the latest release is deployed to Vercel. **Note**: Vercel does Blue-Green for us!

The CI/CD pipelines can be found in the [.github workflows directory](https://github.com/COMP4350-Team2/Mobile-Webapp/tree/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows). <br>
A snapshot of the CI/CD execution can be found under the actions tab at the top of [this page](https://github.com/COMP4350-Team2/Mobile-Webapp/actions)


## Thoughts
Although the team is proud of what they were able to accomplish, the teammates still had thoughts on how the project could have been improved in retrospect. Firstly, for the Mobile WebApp, the team would have liked to start off with mockup tools (Figma) and have the design ready in the earlier sprints. This way, the team could have designed the Mobile WebApp component-by-component and with a predetermined layout. Secondly, for the Desktop NativeApp, we would have liked to use Data Binding compatible DSOs which would make UI creation much easier. This would reduce the memory footprint, drastically reduce LOC and make the UI more robust. A dedicated authentication server abstracting away the details of the login/logout would be an improvement. The backend had similarly named DSOs and some inconsistent API naming, both of which could be improved to make development easier. Additionally, we would have liked to develop more helpful features and design the UI in a professional way. More specifically, we would like to provide list sharing and make the UI closely mimic industry standards, making the app more suitable for a professional setting. 

## Other Thoughts
- **Sam**: I believe providing the students with more robust criteria and requirements for each sprint’s deliverables would be helpful. Sometimes it felt a little up in the air. Some sprints we got more than expected and some we got less. 
- **Ahmed**: Make the TA’s more available to the students. Highlight the expectations of each sprint more clearly. There were conflicting requirements in the worksheet, rubric and class discussions. Lastly, tightening requirements but reducing the volume of requirements may help students produce more robust and professional products. 
- **Vaughn**: I feel like the requirement of having two front ends is a little redundant, in my opinion having one front end would allow for more time to develop interesting and creative features. 
