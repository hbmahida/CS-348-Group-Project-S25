from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

DB_CONFIG = {
    "dbname": "listings_db",
    "user": "postgres",
    "password": "your_password_goes_here_if_any",
    "host": "localhost",
    "port": 5432
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Endpoint to get all listings from table.
@app.route('/get-listings')
def get_listings():
		conn = get_db_connection()
		cur = conn.cursor()

		cur.execute(
            """
            SELECT id, name, neighbourhood, room_type, price, minimum_nights, number_of_reviews, availability_365
            FROM listings
            ORDER BY id;
            """
            )
		rows = cur.fetchall()

		cur.close()
		conn.close()

		listings = [
				{
                    'id': row[0],
                    'name': row[1],
                    'neighbourhood': row[2],
                    'room_type': row[3],
                    'minimum_nights': row[4],
                    'number_of_reviews': row[5],
                    'availability_365': row[6],
                }
				for row in rows
		]

		return jsonify(listings)

# Endpoint to add new sample listings to table.
@app.route('/add-listings')
def insert_dummy_data():
    conn = get_db_connection()
    cur = conn.cursor()

    # Dummy listings data
    dummy_listings = [
        (
            "Cozy Downtown Condo",
            "Waterfront Communities–The Island",
            "Entire home/apt",
            145.00,
            2,
            38,
            212,
        ),
        (
            "Private Room near UofT",
            "Kensington-Chinatown",
            "Private room",
            68.00,
            1,
            120,
            300,
        ),
        (
            "Modern Loft w/ CN-Tower View",
            "Niagara",
            "Entire home/apt",
            210.00,
            2,
            64,
            150,
        ),
        (
            "Budget Basement Studio",
            "Dovercourt-Wallace Emerson-Junction",
            "Entire home/apt",
            55.00,
            3,
            11,
            365,
        ),
        (
            "Annex Heritage Home Room",
            "Annex",
            "Private room",
            75.00,
            2,
            77,
            180,
        ),
        (
            "Queen West Artsy Flat",
            "Trinity-Bellwoods",
            "Entire home/apt",
            185.00,
            2,
            95,
            220,
        ),
        (
            "Spacious North York House",
            "Willowdale East",
            "Entire home/apt",
            299.00,
            4,
            33,
            120,
        ),
        (
            "Harbourfront 1-BR w/ Balcony",
            "Waterfront Communities–The Island",
            "Entire home/apt",
            189.00,
            2,
            58,
            250,
        ),
        (
            "Little Italy Sun-filled Room",
            "Palmerston–Little Italy",
            "Private room",
            82.00,
            1,
            88,
            330,
        ),
        (
            "Leslieville Coach-House Loft",
            "South Riverdale",
            "Entire home/apt",
            160.00,
            2,
            44,
            200,
        ),
    ]

    insert_sql = """
        INSERT INTO listings
        (name, neighbourhood, room_type, price,
         minimum_nights, number_of_reviews, availability_365)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.executemany(insert_sql, dummy_listings)

    return jsonify({"message": "Dummy data inserted into the table."})

# Endpoint to delete all data from the table.
@app.route('/delete-all-listings')
def delete_all_listings():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM listings;")

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "All listings deleted from the table."})

if __name__ == '__main__':
    app.run(debug=True)