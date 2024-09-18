# Cupboard by Team TeaCup

## Presentation Slides
[Link to slides. CLICK ME!](https://umanitoba-my.sharepoint.com/:p:/r/personal/seoa_myumanitoba_ca/_layouts/15/Doc.aspx?sourcedoc=%7B062B260E-9298-4CC3-BACE-D646A239C5D1%7D&file=Proposal%20Presentation.pptx&action=edit&mobileredirect=true)

## Summary & Vision
**Cupboard** lets you manage your groceries and recipes in a convenient way, improving your experience in the kitchen. Users can keep track of ingredients they have, ingredients they need to buy and any recipes they create with these ingredients. Users can also add others to their household, allowing all members to share ingredient inventory, grocery lists and recipes. Meal planning is made easy; simply add your recipes to your calendar. Meal planning and grocery shopping for a household has never been easier!

## Features & User Stories
### Key Feature 1: Menu Planning 
#### User Stories:
- As a user, I should be able to see and access my calendar.\
    **Acceptance Criteria:**
    - Given that I’m a logged-in user 
    - When I click on my calendar  
    - Then the system will open my personal calendar. 
- As a user, I should be able to add a recipe for any day of the year and be able to see it in my calendar.\
    **Acceptance Criteria:**
    - Given that I’m a logged in user who has their calendar opened. 
    - When I click on any day of the calendar and click the “add recipe” option. 
    - Then I should be able to assign one of my own recipes to that day. 
- As a user, I should be able to add a recipe for breakfast, lunch, dinner, and snacks.\
    **Acceptance Criteria:**
    - Given that I’m a logged in user who has their calendar opened. 
    - When I click on a certain day and click the “add recipe” option. 
    - Then I should have the option to select a tag of “breakfast”, “lunch”, or “dinner” to my recipe. 

### Key Feature 2: Organize ingredients
#### User Stories:
- As a user, I want to have a list of commonly available ingredients I can choose from.\  
- As a user, I want to search ingredients.\
- As a user, I want to be able to set the amounts of ingredients added to my lists.\ 
- As a user, I want to create custom items and add them to my lists.\ 
- As a user, I want to see all the custom items I have previously made.\ 
- As a user, I want to see the ingredients I previously had in my list when I log in.\ 
- As a user, I want to organize ingredients into lists of my choice.\ 
- As a user, I want to have a place to view all my lists.\ 
- As a user, I want to sort ingredients in my list based on name, date added, date opened.\ 
- As a user, I want search results to highlight ingredients that are already added in my list.\ 

### Key Feature 3: Sharing Grocery List 
#### User Stories:
- As a user, I want to add other people to my personal grocery list.\ 
- As a user, I want to view the lists I have joined.\ 
- As a user, I want to make changes to lists that I have joined.\ 
- As a user, I want to control who can view and edit my lists.\

### Key Feature 4: Create/Logging Recipes
#### User Stories:
- As a user, I want to create recipes.\ 
- As a user, I want to add/remove ingredients with amounts to my recipes.\ 
- As a user, I want to adjust the amount of ingredients in my recipes.\ 
- As a user, I want to add pictures to my recipes.\ 
- As a user, I want to add steps to my recipes.\ 
- As a user, I want to view all my recipes.\ 
- As a user, I want to share my recipes with other users.\ 
- As a user, I want to view all my shared recipes.\ 
- As a user, I want to favourite recipes.\ 
- As a user, I want to see which ingredients in a recipe I don’t have in my list.\ 

### Non-functional Feature: Minimize Response Time
We aim to provide a response time of less than 1 second to 100 users concurrently.

## Acceptance Criteria

## Initial Architecture
### Diagram:
![Diagram](/COMP4350_Architecture.jpg)

### Architecture Rationale
Team Teacup decided upon a 3-tier architecture by dividing the codespaces and flow into *UI*, *Logic* and *Data* layers. The 3-tier architecture is familiar to the team and is well-suited for the project. A large part of the project involves create, read, update, and delete (CRUD) operations being done on items in the data layer. This means the 3-tier architecture would be convenient to work with. Although the diagram shows a single instance of the *API Server* in the *Logic* layer, the technology used (*AWS Elastic Beanstalk*) allows automatic scaling in response to a large request volume. This service allows our logic layer to be simplified as shown. Similarly, a relational database management system service (*Microsoft Azure*) is used because it provides automatic *horizontal and vertical scaling* in response to incoming requests. The team will likely use a *horizontal scaling* approach to the database since the team values response time over consistency. That is, users will see *eventual consistency* on their interfaces. User login and authentication will be delegated by the *API Server* to *Auth0*. *Auth0* provides excellent scaling and is compatible with many interfaces and technologies. We chose the two front ends in the *UI* layer to be desktop and mobile since this software is to be used inside and outside the house. 


### Work Division
Team Teacup will use a lot of technologies that are new to the team members. However, all the team members have shown strong enthusiasm towards learning all the new technologies. Therefore, the team decided to have a streamlined workflow where every teammate will get to engage with every component of Cupboard. However, once everyone is comfortable with the technologies, sub-groups of the team might be assigned to different components as needed. The team is also using Linear to keep track of the issues (features, user stories, devtasks, bugs etc.) for Cupboard's multirepo setup and there will be weekly meetings to ensure everyone understands the current state of the project.
