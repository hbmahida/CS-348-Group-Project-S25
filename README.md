# CS-348-Group-Project-S25 🏠

A Flask-based web application for managing property listings with PostgreSQL database integration. This project provides a comprehensive platform for searching, filtering, sorting, and managing property listings data and a lot more.

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

This application is a database-driven web platform built for CS 348 that allows users to manage property listings. It features a Flask backend connected to a PostgreSQL database, providing full CRUD operations and advanced capabilities for property data.

## ✨ Features

### Basic Functionality
- Search Listings: Search properties by name, neighborhood, or other criteria
- Filter Listings: Filter properties by room type, price range, minimum nights, etc.
- Sort Listings: Sort results by price, name in ascending or descing order.
- Add Listing: Create new property listings
- Remove Listing: Delete existing property listings
- Update Listing: Modify existing property information
- Top 3 Properties: View the top 3 highest-rated or most popular properties

### Advanced Functionality
- Geospatial Queries: Finds all the listings within x km of the user’s selected location.
- Brokerage Firm Analysis: Model referral hierarchies, show chains of referrals and calculate revenue contributions.
- Trigger based Host Notification System: Alerts the hosts in a neighborhood when a new listing is added via real-time notifications.
- Intelligent Recommendation System: Suggests similar listings based on multi-factor similarity weights (price, location, host, amenities, etc.)
- Interactive Data Analytics Dashboard: Provides real-time insights on fast, dynamic updates on pricing trends, host performance, and neighbourhood performance.


### Technical Features
- PostgreSQL database integration
- Geospatial Quering using `postgis` for listing location
- Data validation and error handling
- Sample/Production data management
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

### Basic Feature Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/view-listings` | Search listings by various criteria |
| GET/POST | `/view-listings` | Filter listings by specific parameters |
| GET/POST | `/view-listings` | Sort listings by different fields |
| POST | `/add-listing` | Add a new listing |
| DELETE | `/delete-listing` | Remove a specific listing |
| PUT | `/update-listing` | Update an existing listing |
| GET | `/` | View top 3 properties in the home page |

### Advanced Feature Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/view-listings` | Search listings by Geospatial Queries |
| GET/POST | `/referral-network` | Brokerage Firm Network Analysis |
| GET/POST | `/notifications` | Trigger based host notification system |
| GET/PUT | `/recommendations` | Intelligent recommendation system |
| GET | `/analytics` | Interactive Data Analytics Dashboard |

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


### Using Basic Features

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


## Using Advanced Features

### Geospatial Queries
- Click the “📍 Listings Near Me” button to open the modal.
- Choose a preset landmark (e.g. “Toronto downtown”, “CN Tower”, “Waterfront”) to automatically fill in the latitude and longitude inputs.
- Or manually enter your coordinates in the Latitude and Longitude fields.
- Specify your search radius in km.
- Click the “Show Nearby” button to submit the inputs or click the “Clear” button to reset the inputs and return to the listings page.
- Once the location and radius is submitted, the interactive map below the listings table will display all listings within that area.

### Brokerage firm network analysis
- Users access the "Brokerage Firm Network" tab in the navigation menu.
- A dropdown allows selection of a brokerage head.
- The system displays a hierarchical table showing the complete referral chain.
- Each agent row shows their level, referral path, listings count, and revenue contribution (%).
- A summary section shows total network revenue and agent count.
- Users can click "Details" to view individual agent's listings.

### Trigger based host notification system
- Users can add new listings through the "Add Listing" page
- When a listing is added, the database automatically triggers notifications
- Users can view all notifications on the "Host Notifications" page
- Users can mark notifications as read by clicking the "Mark as Read" button
- The system shows both "LISTING_ADDED" (confirmation) and "NEW_COMPETITION" (alert) notifications

### Intelligent recommendation system
- Click on ‘Recommendations’ in the sidebar.
- Search for a listing (e.g., “Downtown”) and select it.
- Instantly, you’ll see a ranked list of similar listings below.
- Use sliders to adjust the weight of each criteria:
   - Price
   - Location
   - Amenities
   - Host quality
   - Rating

 ### Interactive Data Analytics Dashboard
- Click on the ‘Analytics Dashboard’ from the sidebar.
- You’ll see options like:
   - Host Performance
   - Price Trends
   - Neighborhood Analytics
- Select a category and instantly view four responsive, interactive charts powered by Plotly:
   - Pie charts for performance tiers,
   - Bar charts for top hosts,
   - Scatter plots comparing price to rating,
   - Histograms of review counts.


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
- The application is designed for educational purposes as part of CS 348 taught at the University of Waterloo.
- Production data includes various property types and neighborhoods extracted from actual airbnb production dataset.

## 🔒 Security Considerations

- Ensure database credentials are not exposed in public repositories
- Use environment variables for sensitive configuration
- Validate all user input before database operations
- Implement proper error handling for production use

---

**CS 348 - Introduction to Database Management**  
*Database-driven web application project*
