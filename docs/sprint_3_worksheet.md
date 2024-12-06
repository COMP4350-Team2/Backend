# Cupboard by Team TeaCup

## Cupboard Meeting Minutes

[Meeting Minutes Word Document for Team Teacup](https://umanitoba-my.sharepoint.com/:w:/g/personal/seoa_myumanitoba_ca/ES0XvzVCruJMvQMZnQftuaMBZt7z6owPIiaymP5jdOUhIw?e=Qlf8kV)

## Cupboard Issue Tracking

Our team issue tracking is available in Linear. Please see UMLearn submission for the link.

## Architecture Diagram

![Architecture Diagram](/docs/images/sprint_3/Sprint_3_Architecture.jpg)

## Getting Started Documentation

The getting started documentation is available in the README.md for each respective repository:  
[Backend Get Started](https://github.com/COMP4350-Team2/Backend#getting-started)  
[Desktop Get Started](https://github.com/COMP4350-Team2/Desktop-NativeApp#getting-started)  
[Mobile Get Started](https://github.com/COMP4350-Team2/Mobile-Webapp#getting-started)

## API Documentation
The current deployed API Documentation can be accessed via https://teacup-cupboard-api.me/api/v3/doc.

The development API documentation is available following the information in the backend README.md.  
[Link to API documentation](https://github.com/COMP4350-Team2/Backend#api-documentation)

The API documentation can also be accessed via putting the `schema.yml` file in the repository into https://editor.swagger.io/ However, you will not be able to test the API endpoints themselves via this method.

## Load Testing
The link to the locust test report can be found [here](/docs/sprint_3_reports/Load_testing_report.txt).  

We used Locust (https://locust.io/) to do the testing and tested all api endpoints users would be expected to have access to when performing regular function. The locust file can be found [here](https://github.com/COMP4350-Team2/Backend/blob/main/locustfile.py)   

One bottleneck we found in the load testing was the patch requests sent to /api/v3/user/lists/ingredients to change an ingredient in a users list that took over 35.5 seconds on average, according to the load test output, which was the longest of all requests. 

Our non-functional requirement was having a response time of less than 1 second when having 100 concurrent users. Unfortunately, we were not able to meet the non-functional requirement. This is likely because of the machine we are running the backend is the smallest possible allowed by AWS (free tier version), and as such there are limitations on its capability. Money would likely allow us to achieve this requirement as it would not just allow for faster machines but also handle several users with a load balancer (paid tier version). 

## Security Analysis
The link to the security analysis report can be found [here](/docs/sprint_3_reports/Bandit_security_analysis.txt).

We used Bandit to do static analysis of our code. To run it, we followed the following steps:
1. Install bandit with
   ```
   pip install bandit
   ```
2. Run the following at the top of the project directory to run it recursivly on all files in the directory and all sub-directories.
   ```
   bandit -r . > bandit_security_analysis.txt
   ```

After running the security analysis, no high or critical problems were found (see the report in the link above). There were only 6 issues in total. The issues were mostly of medium or low priority problems and it was because the analysis suspected things like access_token = "" was us storing credentials in plain text and not realizing these were default placeholder values. Similarly, the analyzer thought a variable holding a date-time format for a string was actually plain text security credentials. The other kind of error was noting that we may not be sending time out requests with some of our auth0 requests. 

Overall, no critical/high problems were found. Other problems included "Possible hardcoded password: ''" thinking that '' could be a hardcoded password when it was just an empty default or "Possible hardcoded password: '%Y-%m-%d %H:%M:%S'" again mistakenly identifying a date-time format string as a hardcoded password.

## Continuous Integration and Deployment (CI/CD)
### Backend
We use GitHub actions for the CI/CD in the backend repository. There are a total of two **(2)** files responsible for CI and CD:
- [backend_ci.yml](https://github.com/COMP4350-Team2/Backend/blob/5158f66f84867b1eaa143da00eb6c5e252ee542b/.github/workflows/backend_ci.yml)
- [backend_cd.yml](https://github.com/COMP4350-Team2/Backend/blob/5158f66f84867b1eaa143da00eb6c5e252ee542b/.github/workflows/backend_cd.yml)  

These two actions are set to run when there is a **push to main** or if it is triggered manually. If the former method is used, then the CD pipeline waits for the CI to succeed before executing. Otherwise the CD will not run.  

The CI/CD pipeline files can be found in the [.github workflows directory](https://github.com/COMP4350-Team2/Backend/tree/5158f66f84867b1eaa143da00eb6c5e252ee542b/.github/workflows).  
A snapshot of the CI/CD execution can be found under the Actions tab at the top of [this page](https://github.com/COMP4350-Team2/Backend/actions)

### Desktop Native App
The team decided to use Github actions for both CI and CD. 
- [Link to CI yml](https://github.com/COMP4350-Team2/Desktop-NativeApp/blob/7e2025cf1ff3855152cc3a7409dc519dbb2c820f/.github/workflows/desktop_ci.yml) 
- [Link to CD yml](https://github.com/COMP4350-Team2/Desktop-NativeApp/blob/7e2025cf1ff3855152cc3a7409dc519dbb2c820f/.github/workflows/desktop_cd.yml). The CD pipeline for the Desktop Native App unfortunately did not work. Releases are still created and releases can be used by running the source code. See release notes on the specific release for running instructions.  

`CI yml` is run on each **push to main** and `CD yml` is run on each **release**.  
The CI/CD pipeline files can be found in the [.github workflows directory](https://github.com/COMP4350-Team2/Desktop-NativeApp/tree/7e2025cf1ff3855152cc3a7409dc519dbb2c820f/.github/workflows).  
A snapshot of the CI/CD execution can be found under the Actions tab at the top of [this page](https://github.com/COMP4350-Team2/Desktop-NativeApp/actions)

### Mobile Web App
For the Mobile WebApp, the team decided to use Github actions for CI/CD as well. There are a total of two **(2)** files responsible for CI and CD:
- [mobile_ci.yml](https://github.com/COMP4350-Team2/Mobile-Webapp/blob/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows/mobile_ci.yml): This file triggers (our CI) on every push to `main` and ensures the build is successful followed by pushing our Docker image to Dockerhub. 
- [deploy.yml](https://github.com/COMP4350-Team2/Mobile-Webapp/blob/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows/deploy.yml): This file triggers (our CD) on every `release` of the WebApp and ensures that the latest release is deployed to Vercel. **Note**: Vercel does Blue-Green for us!

The CI/CD pipelines can be found in the [.github workflows directory](https://github.com/COMP4350-Team2/Mobile-Webapp/tree/2681ccc32c4f92eac14eb1684b0214e5b138e668/.github/workflows).  
A snapshot of the CI/CD execution can be found under the actions tab at the top of [this page](https://github.com/COMP4350-Team2/Mobile-Webapp/actions)


## Top-tier Option
Our Mobile WebApp deployment was on Vercel, which only allows `https` requests. However, the EC2 instance that was hosting the backend could only accept and return `http` responses.<br>
The team was able to set up Nginx with Certbot to generate SSL certificates automatically and handle the `https` requests. This was, by far, the biggest challenge for the team and getting it to work was nothing short of incredible!

## Thoughts
Although the team is proud of what they were able to accomplish, the teammates still had thoughts on how the project could have been improved in retrospect. Firstly, for the Mobile WebApp, the team would have liked to start off with mockup tools (Figma) and have the design ready in the earlier sprints. This way, the team could have designed the Mobile WebApp component-by-component and with a predetermined layout. Secondly, for the Desktop NativeApp, we would have liked to use Data Binding compatible DSOs which would make UI creation much easier. This would reduce the memory footprint, drastically reduce LOC and make the UI more robust. A dedicated authentication server abstracting away the details of the login/logout would be an improvement. The backend had similarly named DSOs and some inconsistent API naming, both of which could be improved to make development easier. Additionally, we would have liked to develop more helpful features and design the UI in a professional way. More specifically, we would like to provide list sharing and make the UI closely mimic industry standards, making the app more suitable for a professional setting. 

## Other Thoughts
- **Agape**: I believe we could have the requirements and the project rubrics a little more ahead of schedule to know what are the exact requirements for each sprint. Receiving the rubrics later resulted in difficulties to manage the tasks when we discovered we needed more requirements for a sprint. It would also be helpful to have either longer and evenly split sprints. Sprint 3 was much longer than sprints 1 and 2 and hence the workload felt unbalanced between the sprints.
- **Ahmed**: Make the TA’s more available to the students. Highlight the expectations of each sprint more clearly. There were conflicting requirements in the worksheet, rubric and class discussions. Lastly, tightening requirements but reducing the volume of requirements may help students produce more robust and professional products. 
- **Sam**: I believe providing the students with more robust criteria and requirements for each sprint’s deliverables would be helpful. Sometimes it felt a little up in the air. Some sprints we got more than expected and some we got less. 
- **Vaughn**: I feel like the requirement of having two front ends is a little redundant, in my opinion having one front end would allow for more time to develop interesting and creative features. 