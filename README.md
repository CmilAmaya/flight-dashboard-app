# Flight Dashboard App
This project is an application that processes attached PDF documents and images containing flight information and extracts relevant data. The extracted data is stored in a PostgreSQL table hosted on AWS RDS. The application features a dynamic dashboard using Streamlit, which allows users to view and interact with the flight information and dashboards.

## Features
- **Data Extraction**: Reads and extracts flight information from both PDF documents and images.
- **Data Storage**: Stores extracted flight data in a PostgreSQL database hosted on AWS RDS.
- **Dynamic Dashboard**: Provides an interactive interface with visualizations and dashboards using Streamlit.

## Project Stucture
![Project Stucture](https://github.com/CmilAmaya/flight-dashboard-app/blob/main/png.png)
- **flight-dashboard-app/** is the root directory of the project.
- **data/** contains data files such as `Aerolineas.xlsx` and `airport_codes.json`.
- **env/** is the Python virtual environment.
- **src/** contains the source code of the project.
- **.env** is a file for environment variables.
- **README.md** is the main documentation file.
- **requirements.txt** lists the project dependencies.
## Deployment Instructions

To deploy this project locally, follow these steps:

### 1. Clone the Repository

First, clone the repository to your local machine.

### 2. Set Up the Virtual Environment

Create and activate a virtual environment for Python.

### 3. Install Dependencies

Install the project dependencies using `pip`.

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add the necessary environment variables. 

### 5. Run the Database Migrations

Ensure your database is up-to-date by running the necessary migrations. In this project, you may need to run migrations using SQLAlchemy. Ensure you have the correct database setup and run.

### 6. Start the Application

Once everything is set up, you can start the Streamlit application to view the dashboards:

```bash
streamlit run src/dashboard.py
