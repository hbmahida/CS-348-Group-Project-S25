from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "movies-db",
    "user": "postgres",
    "host": "localhost",
    "port": 5432
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Endpoint to get all movies from table.
@app.route('/get-movies')
def get_movies():
		conn = get_db_connection()
		cur = conn.cursor()
            
		cur.execute('SELECT id, title, genre, year FROM movies;')
		rows = cur.fetchall()
  
		cur.close()
		conn.close()

		movies = [
				{'id': row[0], 'title': row[1], 'genre': row[2], 'year': row[3]}
				for row in rows
		]
            
		return jsonify(movies)

# Endpoint to add new sample movies to table.
@app.route('/add-movies')
def insert_dummy_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # Dummy movie data
    dummy_movies = [
        ("Inception", "Sci-Fi", 2010),
        ("The Dark Knight", "Action", 2008),
        ("Interstellar", "Sci-Fi", 2014),
        ("The Godfather", "Crime", 1972),
        ("Parasite", "Thriller", 2019),
        ("Forrest Gump", "Drama", 1994)
    ]

    cur.executemany(
        "INSERT INTO movies (title, genre, year) VALUES (%s, %s, %s);",
        dummy_movies
    )

    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Dummy data inserted into the table."})

# Endpoint to delete all data from the table.
@app.route('/delete-all-movies')
def delete_all_movies():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM movies;")
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "All movies deleted from the table."})

if __name__ == '__main__':
    app.run(debug=True)