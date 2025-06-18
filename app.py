from flask import Flask, flash, redirect, render_template, request, url_for
import psycopg2
from psycopg2 import errors, IntegrityError
from db_config import DB_CONFIG
from datetime import date
import os

app = Flask(__name__)

# Secret key for session/flash support (set this to a secure random value)
app.secret_key = os.urandom(24)

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Initializes the database schema from data.sql.
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

# Route for homepage.
@app.route('/')
def home():
    return render_template('home.html')

# Route to add sample data to the listings database.
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

# Route for viewing the listings filtered by 
@app.route('/view-listings')
def view_listings():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Read all params
    search = request.args.get('search', type=str)
    neighbourhood = request.args.get('neighbourhood', type=str)
    room_type     = request.args.get('room_type',    type=str)
    price_min     = request.args.get('price_min',    type=float)
    price_max     = request.args.get('price_max',    type=float)
    min_nights    = request.args.get('min_nights',   type=int)
    sort_by     = request.args.get('sort_by',      type=str)  # 'price' | 'name' | ''
    sort_order  = request.args.get('sort_order',   type=str)

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

    group_by = """
      GROUP BY
        l.listing_id, l.name, l.price, l.room_type, n.name
    """

    where_clauses = []
    params = []

    # 3a. Search listing name and neighbourhood based on pattern entered by user.
    if search:
        wildcard = f"%{search}%"
        where_clauses.append("(l.name ILIKE %s OR n.name ILIKE %s)")
        params.extend([wildcard, wildcard])

    # 3b. Apply filters (if provided)
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

    # 4. Stitching the query together.
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    base_query += group_by

    if sort_by == 'price':
        direction = 'ASC' if sort_order == 'asc' else 'DESC'
        base_query += f"\n  ORDER BY l.price {direction}"
    elif sort_by == 'name':
        direction = 'ASC' if sort_order == 'asc' else 'DESC'
        base_query += f"\n  ORDER BY l.name {direction}"
    else:
       # default ordering
        base_query += """
        ORDER BY avg_rating DESC NULLS LAST,
        l.price ASC
        """
    base_query += ";" # End of query

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
        'min_nights':    min_nights    or '',
        'sort_by':       sort_by       or '',
        'sort_order':    sort_order    or ''
      }
    )

# Route to add listings from users (currently an admin user)
@app.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        # 1. read form data
        listing_id        = request.form.get('listing_id', type=int)
        host_id           = request.form.get('host_id', type=int)
        name              = request.form.get('name')
        description       = request.form.get('description')
        neighbourhood_overview = request.form.get('neighbourhood_overview')
        room_type         = request.form.get('room_type')
        accommodates      = request.form.get('accommodates', type=int)
        bathrooms         = request.form.get('bathrooms', type=float)
        bathrooms_text    = request.form.get('bathrooms_text')
        bedrooms          = request.form.get('bedrooms', type=int)
        beds              = request.form.get('beds', type=int)
        price             = request.form.get('price', type=float)
        minimum_nights    = request.form.get('minimum_nights', type=int)
        maximum_nights    = request.form.get('maximum_nights', type=int)
        instant_bookable  = bool(request.form.get('instant_bookable'))
        created_date      = date.today()
        last_scraped      = date.today()
        neighbourhood_id  = 0
        neighbourhood_name = request.form.get('neighbourhood_name')
        neighbourhood_group = request.form.get('neighbourhood_group')
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        # 2. Check for duplicate listing_id
        cur.execute('SELECT 1 FROM Listing WHERE listing_id = %s;', (listing_id,))
        if cur.fetchone():
            flash(f'Error: Listing ID {listing_id} already exists.', 'error')
        else:
            # 3. insert into Listing
            try:
                cur.execute(
                    '''INSERT INTO Listing (
                         listing_id, host_id, name, description,
                         neighbourhood_overview, room_type, accommodates,
                         bathrooms, bathrooms_text, bedrooms, beds,
                         price, minimum_nights, maximum_nights,
                         instant_bookable, created_date, last_scraped)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                               %s, %s, %s, %s, %s, %s, %s)''',
                    (listing_id, host_id, name, description,
                     neighbourhood_overview, room_type, accommodates,
                     bathrooms, bathrooms_text, bedrooms, beds,
                     price, minimum_nights, maximum_nights,
                     instant_bookable, created_date, last_scraped)
                )
                cur.execute(
                    'SELECT COALESCE(MAX(neighbourhood_id), 0) + 1 FROM Neighbourhood;'
                )
                neighbourhood_id = cur.fetchone()[0]
                cur.execute(
                    '''INSERT INTO Neighbourhood (
                        neighbourhood_id, listing_id, name, neighbourhood_group,
                        latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s)''',
                    (neighbourhood_id, listing_id, neighbourhood_name, neighbourhood_group,
                    latitude or None, longitude or None)
                )
                conn.commit()
                flash('Listing created successfully!', 'success')
                conn.close()
                return redirect(url_for('view_listings'))
            except IntegrityError as e:
                import traceback
                traceback.print_exc()
                flash(f"Error: {e.pgerror}", 'error')
                conn.rollback()
                conn.close()
                return redirect(url_for('add_listing'))

    # fetch hosts for dropdown
    cur.execute('SELECT host_id, host_name FROM Host ORDER BY host_name;')
    hosts = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('add_listing.html', hosts=hosts)

# Route to delete a particular listing.
@app.route('/delete-listing', methods=['GET', 'POST'])
def delete_listing():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        listing_id = request.form.get('listing_id', type=int)
        
        # attempt to delete
        cur.execute('SELECT 1 FROM Listing WHERE listing_id = %s;', (listing_id,))
        if not cur.fetchone():
            flash(f'Listing ID {listing_id} not found.', 'error')
        else:
            cur.execute('DELETE FROM Listing WHERE listing_id = %s;', (listing_id,))
            conn.commit()
            flash(f'Listing ID {listing_id} deleted successfully.', 'success')
        cur.close()
        conn.close()
        return redirect(url_for('delete_listing'))

    # GET: render form
    cur.close()
    conn.close()
    return render_template('delete_listing.html')

# Route to remove the loaded sample data from the database.
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