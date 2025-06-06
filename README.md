# College Placement Management System

A web-based application built using Flask and PostgreSQL to streamline college placement activities. This system helps manage student, company, and placement-related data efficiently through role-based dashboards for Admin, Company, and Student users.

## Features

1) User Authentication – Secure login system for Admin, Company, and Student roles.

1) Student Management – Add, edit, and delete student records with key details (USN, CGPA, branch, backlogs, etc.).

1) Company Management – Add companies along with eligibility criteria such as CGPA, branch, and backlog limits.

1) Eligibility Filtering – Automatically show eligible students based on company criteria.

1) Placement Status Update – Mark students as “Placed” and remove them from future eligible lists.

1) Dashboard Views – Company Role-specific dashboards for smooth interaction.

1) Session Handling – Secure session management for each user type.

## Technologies Used
* ### HTML – For web page structure.

* ### CSS – For styling and layout customization.

* ### JavaScript – For interactive elements.

* ### Python – Programming language used for backend development.
  
* ### Flask (Python) – Lightweight web framework for handling server-side logic and routing.

* ### PostgreSQL – Database to manage student and company data.


## How to Use?

1) Clone the repository.

2) Install required packages

   
   ````
   pip install flask psycopg2
    ````
4) Install PostgreSQL
5) Set up the database

      * Create a PostgreSQL database named user_login_page.

      * Update database credentials in Login_Page.py accordingly.

6) Run these Python Files By Order
     * To Create Login Id and Password Database.
       
        ````
          python Create_Table.py
         ````
    * To Enter Data inside Login Id and Password Database.
       
         ````
          python Data Entry.py
        ````
    * To Run the the Program.
       
        ````
        python Login_Page.py
        ````
7) Open your browser and visit
    ````
    http://localhost:5001
    ````

