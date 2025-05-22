# CS-348-Group-Project-S25
## Setup 🔧
- Clone the GitHub repo.
- Enter the following command into the VSCode terminal: `pip install -r requirements.txt`.
- Have PostgreSQL installed on your local machine with default installation settings.
- Download pgAdmin4 and connect that to the PostgreSQL database.
- Create a database titled `listings_db`.
- Click on the Query Tool and create a relation (table) called `listings` in that database using the following command:
```SQL
CREATE TABLE listings (
    id                SERIAL        PRIMARY KEY,
    name              TEXT          NOT NULL,
    neighbourhood     TEXT,
    room_type         TEXT,
    price             NUMERIC(7,2),      -- CAD $
    minimum_nights    INT,
    number_of_reviews INT,
    availability_365  INT
);
```
- Run the Flask server using the following command: `python app.py`.
- Enter the following URL in your browser: `http://127.0.0.1:5000`.

## Steps to add the sample data
- Hit the endpoint `/add-reviews`.
- A message confirming that the data has been added will be displayed on the screen.

## Steps to get the sample data
- Hit the endpoint `/get-reviews`.
- A message containing all the movies in the relation will be displayed on the screen.

## Steps to remove all sample data
- Hit the endpoint `/delete-all-reviews`.
- A message confirming that the data has been removed will be displayed on the screen.
