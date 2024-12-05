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

Tool:
Load test cases:

Bottlenecks Found:

Goals:

Results:

## Security Analysis
Link to the Security Report

Problems found

Why did we choose that security analysis tool?

How to run the security analysis tool

What are 5 detected problems and discuss what you see

Handle (or mitigate) all Critical and High Priority vulnerabilities in the project


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

CI/CD environment and clickable link to the pipeline.

Provide link to the workflow

Snapshots of the CI/CD execution


## Thoughts
Although the team is proud of what they were able to accomplish, the teammates still had thoughts on how the project could have been improved in retrospect. Firstly, for the Mobile WebApp, the team would have liked to start off with mockup tools (Figma) and have the design ready in the earlier sprints. This way, the team could have designed the Mobile WebApp component-by-component and with a predetermined layout. Secondly, for the Desktop NativeApp, we would have liked to use Data Binding compatible DSOs which would make UI creation much easier. This would reduce the memory footprint, drastically reduce LOC and make the UI more robust. A dedicated authentication server abstracting away the details of the login/logout would be an improvement. The backend had similarly named DSOs and some inconsistent API naming, both of which could be improved to make development easier. Additionally, we would have liked to develop more helpful features and design the UI in a professional way. More specifically, we would like to provide list sharing and make the UI closely mimic industry standards, making the app more suitable for a professional setting. 

## Other Thoughts
- **Sam**: I believe providing the students with more robust criteria and requirements for each sprint’s deliverables would be helpful. Sometimes it felt a little up in the air. Some sprints we got more than expected and some we got less. 
- **Ahmed**: Make the TA’s more available to the students. Highlight the expectations of each sprint more clearly. There were conflicting requirements in the worksheet, rubric and class discussions. Lastly, tightening requirements but reducing the volume of requirements may help students produce more robust and professional products. 
- **Vaughn**: I feel like the requirement of having two front ends is a little redundant, in my opinion having one front end would allow for more time to develop interesting and creative features. 
