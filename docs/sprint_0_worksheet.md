# Cupboard by Team TeaCup

## Presentation Slides
[Link to slides. CLICK ME!](https://umanitoba-my.sharepoint.com/:p:/r/personal/seoa_myumanitoba_ca/_layouts/15/Doc.aspx?sourcedoc=%7B062B260E-9298-4CC3-BACE-D646A239C5D1%7D&file=Proposal%20Presentation.pptx&action=edit&mobileredirect=true)

## Summary & Vision
**Cupboard** lets you manage your groceries and recipes in a convenient way, improving your experience in the kitchen. Users can keep track of ingredients they have, ingredients they need to buy and any recipes they create with these ingredients. Users can also add others to their household, allowing all members to share ingredient inventory, grocery lists and recipes. Meal planning is made easy; simply add your recipes to your calendar. Meal planning and grocery shopping for a household has never been easier!

## Features & User Stories
### Key Feature 1: Menu Planning 
#### User Stories:
- ***As a user, I should be able to see and access my calendar.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged-in user 
    - When I click on my calendar  
    - Then the system will open my personal calendar. 
- ***As a user, I should be able to add a recipe for any day of the year and be able to see it in my calendar.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user who has their calendar opened. 
    - When I click on any day of the calendar and click the “add recipe” option 
    - Then I should be able to assign one of my own recipes to that day. 
- ***As a user, I should be able to add a recipe for breakfast, lunch, dinner, and snacks.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user who has their calendar opened 
    - When I click on a certain day and click the “add recipe” option
    - Then I should have the option to select a tag of “breakfast”, “lunch”, or “dinner” to my recipe. 

### Key Feature 2: Organize ingredients
#### User Stories:
- ***As a user, I want to have a list of commonly available ingredients I can choose from.***<br /> 
**Acceptance Criteria:**
    - Given that I’m a logged in user and on my profile  
    - When I am on my profile, I should be able to see my list of ingredients available 
    - Upon clicking on my list, I should be able to click the “add ingredient” button 
    - Then, I should be presented with a list of commonly available ingredients that I can add to my own list. 
- ***As a user, I want to search ingredients.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user and on my profile 
    - I should be able to see a list of my own ingredients that I can open 
    - When I click the “add ingredients” button upon opening my list 
    - Then I should be presented with a list of commonly available ingredients that I can search through using a search bar. 
- ***As a user, I want to be able to set the amounts of ingredients added to my lists.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user who is trying to add an ingredient to my list 
    - When I add a new ingredient to my list  
    - Then, I should be able to edit the amount of ingredient before adding it to my list.  
- ***As a user, I want to create custom items and add them to my lists.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user with my list of ingredients open  
    - When I click “add ingredient”   
    - Then I should be able to add a custom ingredient by clicking the “add custom ingredient” option that lets me write the name and image of the ingredient.  
- ***As a user, I want to see all the custom items I have previously made.***<br />
**Acceptance Criteria:**
    - Given I’m a logged in user  
    - When I click my own profile    
    - Then I should be able to see a “my custom ingredients” section that shows me all the custom ingredients I’ve created. 
- ***As a user, I want to see the ingredients I previously had in my list when I log in.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged-out user
    - When I enter my details correctly and get logged in    
    - Then, the app should keep my previous ingredients list.  
- ***As a user, I want to organize ingredients into lists of my choice.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user
    - When I click on my profile and click the “make new list” button    
    - Then I should be able to make a custom list where I can add ingredients. 
- ***As a user, I want to have a place to view all my lists.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user 
    - When I click on my profile and click “view my lists”   
    - Then I should be able to see all my lists with all the ingredients in them.  
- ***As a user, I want to sort ingredients in my list based on name or date added.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user 
    - When I click on my custom lists and choose a list of ingredients    
    - Then, I should be able to sort the list alphabetically or by date.  
- ***As a user, I want search results to highlight ingredients that are already added in my list.***<br /> 
**Acceptance Criteria:**
    - Given that I’m a logged in user with one of my lists open  
    - When I try to add a new ingredient by searching/scrolling through the ingredients    
    - Then, the ingredients already present in my list should be highlighted.  

### Key Feature 3: Sharing Grocery List 
#### User Stories:
- ***As a user, I want to add other people to my personal grocery list.***<br />
**Acceptance Criteria:**
    - Given that I’m in a role of a registered user   
    - When I open the “share” page     
    - Then the system gives me text box to input either another users’ username or phone number 
    - Once the username/phone number field is filled, I can press the invite button to send an invitation 
- ***As a user, I want to view the lists I have joined.***<br />
**Acceptance Criteria:**
    - Given that I’m in a role of a registered user    
    - When I open the “my lists” page      
    - Then the system shows me a list of lists that created/joined 
- ***As a user, I want to make changes to lists that I have joined.***<br /> 
**Acceptance Criteria:**
    - Given that I’m in a role of a registered user   
    - When I open the “my lists” page     
    - Then the system shows me a list of lists that created/joined  
    - I then select which list I want to make changes to 
    - Which brings up a detailed view of my list, with items and their quantities 
    - From which I can add/remove quantity of a product by either typing in an associated field or press +/- symbols to change the value 
    - And I am also offered the option to fill in a search field with the name of an item I want to add 
    - Which when the apply button is selected, brings up a list of relevant items and the aforementioned add/remove quantity change options 
- ***As a user, I want to control who can view and edit my lists.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user who has lists   
    - When I share a list with another user       
    - Then, I want to be able to select which lists they can view and/or edit   

### Key Feature 4: Create/Logging Recipes
#### User Stories:
- ***As a user, I want to create recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I click the Recipes section of my profile and click “add custom recipe”       
    - Then I should be able to create my own custom recipe and give it a name. 
- ***As a user, I want to add/remove ingredients with amounts to my recipes.***<br /> 
**Acceptance Criteria:**
    - Given that I’m a logged in user   
    - When I click on the Recipes section of my profile and create a new custom recipe       
    - Then I should be able to click the “add ingredient” button which lets me choose from a list of ingredients and lets me enter the amount. 
- ***As a user, I want to adjust the amount of ingredients in my recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I open one of my custom recipes and click it     
    - Then I should be able to edit the amount of each ingredient in my recipe. 
- ***As a user, I want to add pictures to my recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user   
    - When I open my custom recipes and click on a recipe   
    - Then I should be able to assign a picture to my recipe by uploading it through my device. 
- ***As a user, I want to add steps to my recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user   
    - When I open my list of recipes and click on “add recipe”     
    - Then, I should be able to click the “add step” button and enter text instructions that should be sequential in the same order as my entering. 
- ***As a user, I want to view all my recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I click on my own profile and click on my recipes   
    - Then I should be able to view a list of all my recipes. 
- ***As a user, I want to share my recipes with other users.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When i click on my recipes on my profile and click on a certain recipe  
    - Then I should be given a “share” option that lets me send the recipe to another user of the app.
- ***As a user, I want to view all my shared recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I click on my recipes on my profile  
    - Then, I should be able to see a checkbox called “shared” that filters all my recipes by whether they’ve been shared or not. 
- ***As a user, I want to favourite recipes.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I click on a recipe on my profile  
    - Then, I should be able to add that recipe to my “favourites” list by clicking a button so I can view it in a “favourite recipes” list. 
- ***As a user, I want to see which ingredients in a recipe I don’t have in my list.***<br />
**Acceptance Criteria:**
    - Given that I’m a logged in user  
    - When I open a recipe on my profile
    - Then, I should be able to see an indicator shows me which ingredients in the recipe are not in my ingredient list so that I can go buy those ingredients. 

### Non-functional Feature: Minimize Response Time
We aim to provide a response time of less than 1 second to 100 users concurrently.

## Initial Architecture
### Diagram:
![Diagram](/docs/COMP4350_Architecture.jpg)

### Architecture Rationale
Team Teacup decided upon a 3-tier architecture by dividing the codespaces and flow into *UI*, *Logic* and *Data* layers. The 3-tier architecture is familiar to the team and is well-suited for the project. A large part of the project involves create, read, update, and delete (CRUD) operations being done on items in the data layer. This means the 3-tier architecture would be convenient to work with. Although the diagram shows a single instance of the *API Server* in the *Logic* layer, the technology used (*AWS Elastic Beanstalk*) allows automatic scaling in response to a large request volume. This service allows our logic layer to be simplified as shown. Similarly, a relational database management system service (*Microsoft Azure*) is used because it provides automatic *horizontal and vertical scaling* in response to incoming requests. The team will likely use a *horizontal scaling* approach to the database since the team values response time over consistency. That is, users will see *eventual consistency* on their interfaces. User login and authentication will be delegated by the *API Server* to *Auth0*. *Auth0* provides excellent scaling and is compatible with many interfaces and technologies. We chose the two front ends in the *UI* layer to be desktop and mobile since this software is to be used inside and outside the house. 


## Work Division
Team Teacup will use a lot of technologies that are new to the team members. However, all the team members have shown strong enthusiasm towards learning all the new technologies. Therefore, the team decided to have a streamlined workflow where every teammate will get to engage with every component of Cupboard. However, once everyone is comfortable with the technologies, sub-groups of the team might be assigned to different components as needed. The team is also using Linear to keep track of the issues (features, user stories, devtasks, bugs etc.) for Cupboard's multirepo setup and there will be weekly meetings to ensure everyone understands the current state of the project.
