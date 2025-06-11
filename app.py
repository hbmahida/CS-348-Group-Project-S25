from flask import Flask, render_template, request
import psycopg2
from psycopg2 import errors, IntegrityError
from db_config import DB_CONFIG

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Initialize database schema from data.sql
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    with open('data.sql', 'r') as f:
        ddl_script = f.read()
    statements = [s.strip() for s in ddl_script.split(';') if s.strip()]
    for stmt in statements:
        cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add-sample')
def add_sample():
    conn = get_db_connection()
    cur = conn.cursor()
    message = "Sample data inserted successfully."

    try:
        with open('sample.sql', 'r') as f:
            sql_script = f.read()

        for stmt in sql_script.split(';'):
            stmt = stmt.strip()
            if not stmt:
                continue
            cur.execute(stmt + ';')

        conn.commit()

    except IntegrityError as e:
        conn.rollback()
        # If it's a duplicate‐key error, let the user know the data was already added
        if isinstance(e, errors.UniqueViolation):
            message = "Sample data has already been added."
        else:
            message = f"Error inserting sample data: {e.pgerror}"
    finally:
        cur.close()
        conn.close()

    return render_template('add_sample.html', message=message)

@app.route('/view-listings')
def view_listings():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Read filter params
    neighbourhood = request.args.get('neighbourhood', type=str)
    room_type     = request.args.get('room_type',    type=str)
    price_min     = request.args.get('price_min',    type=float)
    price_max     = request.args.get('price_max',    type=float)
    min_nights    = request.args.get('min_nights',   type=int)

    # 2. Build base query (join on Neighbourhood.listing_id)
    base_query = """
    SELECT
      l.listing_id,
      l.name,
      l.price,
      l.room_type,
      n.name           AS neighbourhood,
      AVG(r.rating)    AS avg_rating,
      COUNT(r.review_id) AS review_count
    FROM Listing l
    JOIN Neighbourhood n
      ON n.listing_id = l.listing_id
    LEFT JOIN Review r
      ON r.listing_id = l.listing_id
    """
    where_clauses = []
    params = []

    # 3. Apply filters only if provided
    if neighbourhood:
        where_clauses.append("n.name = %s")
        params.append(neighbourhood)
    if room_type:
        where_clauses.append("l.room_type = %s")
        params.append(room_type)
    if price_min is not None:
        where_clauses.append("l.price >= %s")
        params.append(price_min)
    if price_max is not None:
        where_clauses.append("l.price <= %s")
        params.append(price_max)
    if min_nights is not None:
        where_clauses.append("l.minimum_nights >= %s")
        params.append(min_nights)

    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)

    # 4. Finalize with grouping & ordering
    base_query += """
      GROUP BY
        l.listing_id, l.name, l.price, l.room_type, n.name
      ORDER BY
        avg_rating DESC NULLS LAST,
        l.price ASC;
    """

    # 5. Execute and fetch
    cur.execute(base_query, params)
    rows = cur.fetchall()
    listings = [
        {
          'listing_id':   r[0],
          'name':         r[1],
          'price':        float(r[2]),
          'room_type':    r[3],
          'neighbourhood':r[4],
          'avg_rating':   round(float(r[5]), 2) if r[5] is not None else None,
          'review_count': int(r[6])
        }
        for r in rows
    ]

    # 6. Fetch distinct options for your filter dropdowns
    cur.execute("SELECT DISTINCT name FROM Neighbourhood ORDER BY name;")
    neighbourhoods = [n[0] for n in cur.fetchall()]

    cur.execute("SELECT DISTINCT room_type FROM Listing WHERE room_type IS NOT NULL ORDER BY room_type;")
    room_types = [rt[0] for rt in cur.fetchall()]

    cur.close()
    conn.close()

    # 7. Render with everything the template needs
    return render_template(
      'view_listings.html',
      listings=listings,
      neighbourhoods=neighbourhoods,
      room_types=room_types,
      current_filters={
        'neighbourhood': neighbourhood or '',
        'room_type':     room_type     or '',
        'price_min':     price_min     or '',
        'price_max':     price_max     or '',
        'min_nights':    min_nights    or ''
      }
    )

@app.route('/delete-all')
def delete_all():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM listing;")
    cur.execute("DELETE FROM host;")
    conn.commit()
    cur.close()
    conn.close()

    return render_template('delete_all.html')

if __name__ == '__main__':
    # Ensure the schema is created before handling requests
    init_db()
    app.run(debug=True)