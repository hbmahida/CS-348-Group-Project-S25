# CS-348-Group-Project-S25
## Setup 🔧
- Clone the GitHub repo.
- Enter the following command into the VSCode terminal: `pip install -r requirements.txt`.
- Have PostgreSQL installed on your local machine with default installation settings.
- Download pgAdmin4 and connect that to the PostgreSQL database.
- Create a database titled 'movies-db'.
- Click on the Query Tool and create a relation (table) called 'movies' in that database using the following command:
```SQL
CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    genre TEXT,
    year INT
);
```
- Run the Flask server using the following command: `python app.py`.
- Enter the following URL in your browser: `http://127.0.0.1:5000`.

## Steps to add the sample data
- Hit the endpoint `/add-movies`.
- A message confirming that the data has been added will be displayed on the screen.

## Steps to get the sample data
- Hit the endpoint `/get-movies`.
- A message containing all the movies in the relation will be displayed on the screen.

## Steps to remove all sample data
- Hit the endpoint `/delete-all-movies`.
- A message confirming that the data has been removed will be displayed on the screen.