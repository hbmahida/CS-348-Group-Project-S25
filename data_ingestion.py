import pandas as pd
import psycopg2
from psycopg2 import errors, IntegrityError
from db_config import DB_CONFIG
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Get database connection
    """
    return psycopg2.connect(**DB_CONFIG)

def parse_price(price_str):
    """
    Parse price string to float, handling $ and , characters
    """
    if pd.isna(price_str) or price_str == '':
        return None
    # Remove $ and , characters, then convert to float
    clean_price = re.sub(r'[$,]', '', str(price_str))
    try:
        return float(clean_price)
    except ValueError:
        return None

def parse_boolean(value):
    """
    Parse boolean values from CSV
    """
    if pd.isna(value):
        return None
    if isinstance(value, str):
        return value.lower() in ['t', 'true', 'yes', '1']
    return bool(value)

def parse_percentage(value):
    """
    Parse percentage values, removing % sign
    """
    if pd.isna(value) or value == '':
        return None
    if isinstance(value, str) and '%' in value:
        try:
            return int(value.replace('%', ''))
        except ValueError:
            return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def parse_date(date_str):
    """
    Parse date string to date object
    """
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        return pd.to_datetime(date_str).date()
    except:
        return None

def parse_amenities(amenities_str):
    """
    Parse amenities string to list
    """
    if pd.isna(amenities_str) or amenities_str == '':
        return []
    
    # Remove brackets and quotes, then split by comma
    clean_amenities = re.sub(r'[\[\]"]', '', str(amenities_str))
    amenities_list = [amenity.strip() for amenity in clean_amenities.split(',') if amenity.strip()]
    return amenities_list

def is_database_empty():
    """
    Check if database is empty (no hosts or listings)
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if Host table has any records
        cur.execute("SELECT COUNT(*) FROM Host;")
        host_count = cur.fetchone()[0]
        
        # Check if Listing table has any records
        cur.execute("SELECT COUNT(*) FROM Listing;")
        listing_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return host_count == 0 and listing_count == 0
        
    except Exception as e:
        logger.error(f"Error checking database status: {e}")
        return False

def load_hosts_from_csv(csv_file_path, conn):
    """
    Load hosts from listings CSV file
    """
    logger.info("Loading hosts from CSV...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        logger.info(f"Read {len(df)} rows from CSV")
        
        # Extract unique hosts
        host_columns = ['host_id', 'host_name', 'host_since', 'host_location', 'host_about',
                       'host_response_time', 'host_response_rate', 'host_acceptance_rate',
                       'host_is_superhost', 'host_listings_count']
        
        hosts_df = df[host_columns].drop_duplicates(subset=['host_id'])
        hosts_df = hosts_df.dropna(subset=['host_id'])
        
        logger.info(f"Found {len(hosts_df)} unique hosts")
        
        cur = conn.cursor()
        
        for _, row in hosts_df.iterrows():
            try:
                # Parse and validate data
                host_id = int(row['host_id'])
                host_name = row['host_name'] if pd.notna(row['host_name']) else None
                host_since = parse_date(row['host_since'])
                host_location = row['host_location'] if pd.notna(row['host_location']) else None
                host_about = row['host_about'] if pd.notna(row['host_about']) else None
                host_response_time = row['host_response_time'] if pd.notna(row['host_response_time']) else None
                host_response_rate = parse_percentage(row['host_response_rate'])
                host_acceptance_rate = parse_percentage(row['host_acceptance_rate'])
                is_superhost = parse_boolean(row['host_is_superhost'])
                host_listings_count = int(row['host_listings_count']) if pd.notna(row['host_listings_count']) else 0
                
                # Validate constraints
                if host_response_rate is not None and (host_response_rate < 0 or host_response_rate > 100):
                    host_response_rate = None
                if host_acceptance_rate is not None and (host_acceptance_rate < 0 or host_acceptance_rate > 100):
                    host_acceptance_rate = None
                if host_listings_count < 0:
                    host_listings_count = 0
                
                # Insert into database
                cur.execute("""
                    INSERT INTO Host (host_id, host_name, host_since, host_location, host_about,
                                    host_response_time, host_response_rate, host_acceptance_rate,
                                    is_superhost, host_listings_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (host_id) DO NOTHING
                """, (host_id, host_name, host_since, host_location, host_about,
                     host_response_time, host_response_rate, host_acceptance_rate,
                     is_superhost, host_listings_count))
                
            except Exception as e:
                logger.warning(f"Error inserting host {row.get('host_id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        logger.info("Hosts loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading hosts: {e}")
        conn.rollback()
        raise

def load_listings_from_csv(csv_file_path, conn):
    """
    Load listings from CSV file
    """
    logger.info("Loading listings from CSV...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Limit to first 1000 rows for performance
        df = df.head(1000)
        logger.info(f"Processing {len(df)} listings")
        
        cur = conn.cursor()
        
        for _, row in df.iterrows():
            try:
                # Parse and validate listing data
                listing_id = int(row['id'])
                host_id = int(row['host_id']) if pd.notna(row['host_id']) else None
                
                if host_id is None:
                    continue
                
                name = row['name'] if pd.notna(row['name']) else 'Unnamed Listing'
                description = row['description'] if pd.notna(row['description']) else None
                neighbourhood_overview = row['neighborhood_overview'] if pd.notna(row['neighborhood_overview']) else None
                room_type = row['room_type'] if pd.notna(row['room_type']) else None
                
                # Parse numeric fields with validation
                accommodates = int(row['accommodates']) if pd.notna(row['accommodates']) and row['accommodates'] > 0 else 1
                bathrooms = float(row['bathrooms']) if pd.notna(row['bathrooms']) and row['bathrooms'] >= 0 else None
                bathrooms_text = row['bathrooms_text'] if pd.notna(row['bathrooms_text']) else None
                bedrooms = int(row['bedrooms']) if pd.notna(row['bedrooms']) and row['bedrooms'] >= 0 else None
                beds = int(row['beds']) if pd.notna(row['beds']) and row['beds'] >= 0 else None
                
                price = parse_price(row['price'])
                if price is None or price <= 0:
                    price = 50.0  # Default price
                
                minimum_nights = int(row['minimum_nights']) if pd.notna(row['minimum_nights']) and row['minimum_nights'] > 0 else 1
                maximum_nights = int(row['maximum_nights']) if pd.notna(row['maximum_nights']) else None
                instant_bookable = parse_boolean(row['instant_bookable'])
                
                last_scraped = parse_date(row['last_scraped'])
                
                neighbourhood_name = row['neighbourhood_cleansed'] if pd.notna(row['neighbourhood_cleansed']) else 'Unknown'
                neighbourhood_group = row['neighbourhood_group_cleansed'] if pd.notna(row['neighbourhood_group_cleansed']) else None
                
                latitude = float(row['latitude']) if pd.notna(row['latitude']) else None
                longitude = float(row['longitude']) if pd.notna(row['longitude']) else None

                # Coordinates sanitation
                if latitude is not None and (latitude < -90 or latitude > 90):
                    latitude = None
                if longitude is not None and (longitude < -180 or longitude > 180):
                    longitude = None
                
                # Insert listing
                cur.execute("""
                    INSERT INTO Listing (listing_id, host_id, name, description, neighbourhood_overview,
                                       room_type, accommodates, bathrooms, bathrooms_text, bedrooms, beds,
                                       price, minimum_nights, maximum_nights, instant_bookable,
                                       created_date, last_scraped, geopoint)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    ST_SetSRID(
                    ST_MakePoint(%s, %s), 4326
                    )::geography
                    )
                    ON CONFLICT (listing_id) DO NOTHING
                """, (listing_id, host_id, name, description, neighbourhood_overview,
                     room_type, accommodates, bathrooms, bathrooms_text, bedrooms, beds,
                     price, minimum_nights, maximum_nights, instant_bookable,
                     datetime.now().date(), last_scraped, longitude, latitude))
                
                # Get next neighbourhood_id
                cur.execute("SELECT COALESCE(MAX(neighbourhood_id), 0) + 1 FROM Neighbourhood")
                neighbourhood_id = cur.fetchone()[0]
                
                # Insert neighbourhood
                cur.execute("""
                    INSERT INTO Neighbourhood (neighbourhood_id, listing_id, name, neighbourhood_group, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (neighbourhood_id, listing_id, neighbourhood_name, neighbourhood_group,
                     latitude, longitude))
                
                # Insert amenities
                amenities = parse_amenities(row['amenities'])
                for amenity in amenities:
                    if amenity:  # Skip empty amenities
                        cur.execute("""
                            INSERT INTO ListingAmenity (listing_id, amenity)
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING
                        """, (listing_id, amenity))
                
                # Insert review summary (if review data exists)
                if pd.notna(row['review_scores_rating']) and row['review_scores_rating'] > 0:
                    review_date = parse_date(row['last_review'])
                    if review_date is None:
                        review_date = datetime.now().date()
                    
                    rating = float(row['review_scores_rating']) / 2  # Convert from 10-point to 5-point scale
                    accuracy = float(row['review_scores_accuracy']) if pd.notna(row['review_scores_accuracy']) else None
                    location = float(row['review_scores_location']) if pd.notna(row['review_scores_location']) else None
                    number_of_reviews = int(row['number_of_reviews']) if pd.notna(row['number_of_reviews']) else 0
                    
                    # Validate rating constraints
                    if rating < 1 or rating > 5:
                        rating = max(1, min(5, rating))
                    
                    cur.execute("""
                        INSERT INTO Review (listing_id, review_date, rating, accuracy, location, number_of_reviews)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (listing_id, review_date, rating, accuracy, location, number_of_reviews))
                
                # Insert availability data
                availability_30 = int(row['availability_30']) if pd.notna(row['availability_30']) else None
                availability_365 = int(row['availability_365']) if pd.notna(row['availability_365']) else None
                
                if availability_30 is not None or availability_365 is not None:
                    cur.execute("""
                        INSERT INTO Availability (listing_id, date, availability_30, availability_365)
                        VALUES (%s, %s, %s, %s)
                    """, (listing_id, datetime.now().date(), availability_30, availability_365))
                
            except Exception as e:
                logger.warning(f"Error inserting listing {row.get('id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        logger.info("Listings loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading listings: {e}")
        conn.rollback()
        raise

def load_reviews_from_csv(csv_file_path, conn):
    """
    Load reviews from reviews CSV file
    """
    logger.info("Loading reviews from CSV...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file_path)
        
        # Limit to first 5000 rows for performance
        df = df.head(5000)
        logger.info(f"Processing {len(df)} reviews")
        
        cur = conn.cursor()
        
        for _, row in df.iterrows():
            try:
                listing_id = int(row['listing_id'])
                review_date = parse_date(row['date'])
                
                if review_date is None:
                    continue
                
                # Check if listing exists
                cur.execute("SELECT 1 FROM Listing WHERE listing_id = %s", (listing_id,))
                if not cur.fetchone():
                    continue
                
                # Create a basic review with default rating
                cur.execute("""
                    INSERT INTO Review (listing_id, review_date, rating, accuracy, location, number_of_reviews)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (listing_id, review_date, 4.0, 8.0, 8.0, 1))
                
            except Exception as e:
                logger.warning(f"Error inserting review for listing {row.get('listing_id', 'unknown')}: {e}")
                continue
        
        conn.commit()
        logger.info("Reviews loaded successfully")
        
    except Exception as e:
        logger.error(f"Error loading reviews: {e}")
        conn.rollback()

def load_production_data_if_needed():
    """
    Load production data if database is empty
    """
    if not is_database_empty():
        logger.info("Database already contains data, skipping production data load")
        return
    
    logger.info("Database is empty, loading production data...")
    
    try:
        conn = get_db_connection()
        
        # Load data in correct order due to foreign key constraints
        load_hosts_from_csv('prod_data/listings.csv', conn)
        load_listings_from_csv('prod_data/listings.csv', conn)
        
        # Load reviews if file exists
        try:
            load_reviews_from_csv('prod_data/reviews.csv', conn)
        except FileNotFoundError:
            logger.warning("reviews.csv not found, skipping reviews data")
        
        conn.close()
        logger.info("Production data loaded successfully!")
        
    except Exception as e:
        logger.error(f"Error loading production data: {e}")
        raise

if __name__ == "__main__":
    # For testing purposes
    load_production_data_if_needed()