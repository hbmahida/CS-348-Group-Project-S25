# CS-348-Group-Project-S25 🏠

A Flask-based web application for managing property listings with PostgreSQL database integration. This project provides a comprehensive platform for searching, filtering, sorting, and managing property listings data.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🌟 Overview

This application is a database-driven web platform built for CS 348 that allows users to manage property listings. It features a Flask backend connected to a PostgreSQL database, providing full CRUD operations and advanced search capabilities for property data.

## ✨ Features

### Core Functionality
- **🔍 Search Listings**: Search properties by name, neighborhood, or other criteria
- **🔧 Filter Listings**: Filter properties by room type, price range, minimum nights, etc.
- **📊 Sort Listings**: Sort results by price, name in ascending or descing order.
- **➕ Add Listing**: Create new property listings
- **🗑️ Remove Listing**: Delete existing property listings
- **✏️ Update Listing**: Modify existing property information
- **🏆 Top 3 Properties**: View the top 3 highest-rated or most popular properties

### Technical Features
- PostgreSQL database integration
- Data validation and error handling
- Sample data management
- RESTful API design
- Responsive web interface

## 🔧 Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.7+** - [Download Python](https://python.org/downloads/)
- **PostgreSQL** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **pgAdmin4** - [Download pgAdmin4](https://www.pgadmin.org/download/) [Not needed if installed with PostgreSQL]
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Code Editor** (VS Code recommended)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hbmahida/CS-348-Group-Project-S25.git
cd CS-348-Group-Project-S25
```

### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🗄️ Database Setup

### 1. Install and Configure PostgreSQL
- Install PostgreSQL with default settings
- Remember your PostgreSQL username and password
- Ensure PostgreSQL service is running
- pgAdmin4 will be installed in this package itself

### 2. Setup pgAdmin4
- Open pgAdmin4
- Use your PostgreSQL credentials to connect

### 3. Create Database
1. In pgAdmin4, right-click on "Databases"
2. Select "Create" → "Database..."
3. Enter database name: `listings_db`
4. Click "Save"

### 4. Configure Database Connection
Ensure your Flask application is configured with the correct database credentials. Check your configuration file `DB_CONFIG.py` for:
- Database host (usually `localhost`)
- Database port (usually `5432`)
- Database name (`listings_db`)
- Username and password

## 🏃‍♂️ Running the Application

### 1. Start the Flask Server
```bash
python3 app.py
```

### 2. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

You should see the application's home page with available features.

## 🔗 API Endpoints

### Data Management Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/view-listings` | Retrieve all listings from the database |
| POST | `/add-sample` | Add all sample listings |
| GET | `/delete-all` | Remove all listings from the database |

### Core Feature Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/view-listings` | Search listings by various criteria |
| GET/POST | `/view-listings` | Filter listings by specific parameters |
| GET/POST | `/view-listings` | Sort listings by different fields |
| POST | `/add-listing` | Add a new listing |
| DELETE | `/delete-listing` | Remove a specific listing |
| PUT | `/update-listing` | Update an existing listing |
| GET | `/` | View top 3 properties in the home page |

## 📖 Usage Guide

### Initial Setup with Sample Data

1. **Add Sample Data**
   - Navigate to `http://127.0.0.1:5000/add-listing`
   - You'll see a confirmation message that sample data has been added

2. **View All Listings**
   - Navigate to `http://127.0.0.1:5000/view-listings`
   - This displays all listings in the database

3. **Clear All Data** (if needed)
   - Navigate to `http://127.0.0.1:5000/delete-all`
   - This removes all listings from the database


###  Production Dataset Generation & Loading

1. Raw Data Source

To download the production dataset, go to https://insideairbnb.com/get-the-data/ and search for Toronto. 

- Download the Detailed Listings data from https://data.insideairbnb.com/canada/on/toronto/2025-06-09/data/listings.csv.gz (File name - listings.csv.gz)
- Download the Reviews.csv file from https://data.insideairbnb.com/canada/on/toronto/2025-06-09/visualisations/reviews.csv (File name - reviews.csv)
- Download the Neighbourhoods.csv file from https://data.insideairbnb.com/canada/on/toronto/2025-06-09/visualisations/neighbourhoods.csv (File name - neighbourhoods.csv)

2. Transformation & Loading Script

We provide a single ingestion module that reads those three CSVs, parses & validates every field, and bulk-loads into all six tables in the correct order:

scripts/data_ingestion.py will:

- Check if Host & Listing tables are empty
- Read prod_data/listings.csv, reviews.csv, neighbourhoods.csv
- Parse dates, prices, booleans, percentages
- Insert into Host, Listing, Neighbourhood, ListingAmenity, Review, Availability using ON CONFLICT to avoid duplicates

All of the features below have been implemented and tested for production dataset.


### Using Core Features

#### 🔍 Search Listings
- Use the search functionality to find properties by name, neighborhood, or other criteria
- Enter search terms in the search box and click "Search"

#### 🔧 Filter Listings
- Apply filters to narrow down results:
  - **Room Type**: Filter by "Entire home/apt", "Private room", "Shared room"
  - **Price Range**: Set minimum and maximum price limits
  - **Minimum Nights**: Filter by minimum stay requirements
  - **Neighbourhood**: Filter by neighbourhood of listings

#### 📊 Sort Listings
- Sort results by:
  - Price (ascending/descending)
  - Name (ascending/descending)

#### ➕ Add New Listing
Fill out the form with:
- Property name (required)
- Neighborhood information
- Room type
- Number of people accomodated
- Number of bedrooms, bathrooms, beds
- Price per night (CAD)
- Minimum - Maximum nights required
- Latitude & Longitude

#### ✏️ Update Listing
- Select a listing to modify
- Update the desired fields
- Save changes
https://data.insideairbnb.com/canada/on/toronto/2025-05-03/data/listings.csv.gz
#### 🗑️ Remove Listing
- Select the listing you want to delete
- Confirm deletion

#### 🏆 View Top Properties
- Access the top 3 properties based on price, rating in the home page

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues
- **Error**: `could not connect to server`
  - **Solution**: Ensure PostgreSQL service is running
  - Check if the port 5432 is available
  - Verify database credentials

#### Import Errors
- **Error**: `ModuleNotFoundError`
  - **Solution**: Ensure all dependencies are installed: `pip install -r requirements.txt`
  - Check if virtual environment is activated

#### Flask App Not Starting
- **Error**: `Address already in use`
  - **Solution**: Kill existing processes on port 5000 or use a different port
  - On Windows: `netstat -ano | findstr :5000`
  - On macOS/Linux: `lsof -ti:5000 | xargs kill -9`


### Getting Help

If you encounter issues:
1. Check the console/terminal for error messages
2. Verify database connection and table existence
3. Ensure all dependencies are properly installed
4. Check if the Flask server is running on the correct port

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 Notes

- This application uses PostgreSQL as the database backend
- All prices are in Canadian Dollars (CAD)
- The application is designed for educational purposes as part of CS 348
- Sample data includes various property types and neighborhoods

## 🔒 Security Considerations

- Ensure database credentials are not exposed in public repositories
- Use environment variables for sensitive configuration
- Validate all user input before database operations
- Implement proper error handling for production use

---

**CS 348 - Introduction to Database Management**  
*Database-driven web application project*
