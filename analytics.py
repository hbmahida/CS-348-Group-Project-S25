"""
Analytics module for the Airbnb Listings Manager
Handles database operations for the analytics dashboard using materialized views
"""

import psycopg2
from db_config import DB_CONFIG
from typing import Dict, List, Any

def get_db_connection():
    """
    Get database connection
    """
    return psycopg2.connect(**DB_CONFIG)

def init_analytics_views():
    """
    Initialize analytics materialized views and triggers
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Drop existing views if they exist
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS host_performance_analytics CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS neighbourhood_analytics CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS price_trends_analytics CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS market_overview_analytics CASCADE")
        cur.execute("DROP MATERIALIZED VIEW IF EXISTS listing_analytics CASCADE")
        
        # Create host performance analytics view
        cur.execute("""
            CREATE MATERIALIZED VIEW host_performance_analytics AS
            SELECT 
                h.host_id,
                h.host_name,
                h.host_since,
                h.is_superhost,
                h.host_response_rate,
                h.host_acceptance_rate,
                COUNT(l.listing_id) as total_listings,
                AVG(l.price) as avg_listing_price,
                AVG(r.rating) as avg_rating,
                COUNT(r.review_id) as total_reviews,
                SUM(CASE WHEN l.instant_bookable = true THEN 1 ELSE 0 END) as instant_bookable_count,
                AVG(l.accommodates) as avg_accommodates,
                CASE 
                    WHEN AVG(r.rating) >= 4.5 AND COUNT(r.review_id) >= 10 THEN 'Excellent'
                    WHEN AVG(r.rating) >= 4.0 AND COUNT(r.review_id) >= 5 THEN 'Very Good'
                    WHEN AVG(r.rating) >= 3.5 THEN 'Good'
                    WHEN AVG(r.rating) >= 3.0 THEN 'Fair'
                    ELSE 'Poor'
                END as performance_tier
            FROM Host h
            LEFT JOIN Listing l ON h.host_id = l.host_id
            LEFT JOIN Review r ON l.listing_id = r.listing_id
            GROUP BY h.host_id, h.host_name, h.host_since, h.is_superhost, h.host_response_rate, h.host_acceptance_rate
        """)
        
        # Create neighbourhood analytics view
        cur.execute("""
            CREATE MATERIALIZED VIEW neighbourhood_analytics AS
            SELECT 
                n.name as neighbourhood_name,
                n.neighbourhood_group,
                COUNT(DISTINCT l.listing_id) as total_listings,
                AVG(l.price) as avg_price,
                MIN(l.price) as min_price,
                MAX(l.price) as max_price,
                AVG(r.rating) as avg_rating,
                COUNT(r.review_id) as total_reviews,
                AVG(l.accommodates) as avg_accommodates,
                AVG(l.minimum_nights) as avg_minimum_nights,
                COUNT(DISTINCT l.room_type) as room_type_variety,
                SUM(CASE WHEN l.instant_bookable = true THEN 1 ELSE 0 END) as instant_bookable_count,
                AVG(l.bedrooms) as avg_bedrooms,
                AVG(l.bathrooms) as avg_bathrooms,
                CASE 
                    WHEN AVG(l.price) >= 200 THEN 'Premium'
                    WHEN AVG(l.price) >= 100 THEN 'High'
                    WHEN AVG(l.price) >= 50 THEN 'Medium'
                    ELSE 'Budget'
                END as price_category
            FROM Neighbourhood n
            JOIN Listing l ON n.listing_id = l.listing_id
            LEFT JOIN Review r ON l.listing_id = r.listing_id
            GROUP BY n.name, n.neighbourhood_group
        """)
        
        # Create price trends analytics view
        cur.execute("""
            CREATE MATERIALIZED VIEW price_trends_analytics AS
            SELECT 
                l.room_type,
                AVG(l.price) as avg_price,
                COUNT(l.listing_id) as listing_count,
                MIN(l.price) as min_price,
                MAX(l.price) as max_price,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY l.price) as median_price,
                AVG(l.accommodates) as avg_accommodates,
                AVG(r.rating) as avg_rating,
                COUNT(r.review_id) as total_reviews,
                AVG(l.minimum_nights) as avg_minimum_nights,
                SUM(CASE WHEN l.instant_bookable = true THEN 1 ELSE 0 END) as instant_bookable_count
            FROM Listing l
            LEFT JOIN Review r ON l.listing_id = r.listing_id
            GROUP BY l.room_type
        """)
        
        # Create market overview analytics view
        cur.execute("""
            CREATE MATERIALIZED VIEW market_overview_analytics AS
            SELECT 
                COUNT(DISTINCT l.listing_id) as total_listings,
                COUNT(DISTINCT h.host_id) as total_hosts,
                COUNT(DISTINCT n.name) as total_neighbourhoods,
                AVG(l.price) as overall_avg_price,
                MIN(l.price) as min_price,
                MAX(l.price) as max_price,
                AVG(r.rating) as overall_avg_rating,
                COUNT(r.review_id) as total_reviews,
                AVG(l.accommodates) as avg_accommodates,
                SUM(CASE WHEN l.instant_bookable = true THEN 1 ELSE 0 END) as instant_bookable_count,
                SUM(CASE WHEN h.is_superhost = true THEN 1 ELSE 0 END) as superhost_count,
                COUNT(CASE WHEN l.room_type = 'Entire home/apt' THEN 1 END) as entire_home_count,
                COUNT(CASE WHEN l.room_type = 'Private room' THEN 1 END) as private_room_count,
                COUNT(CASE WHEN l.room_type = 'Shared room' THEN 1 END) as shared_room_count,
                COUNT(CASE WHEN l.room_type = 'Hotel room' THEN 1 END) as hotel_room_count,
                AVG(CASE WHEN r.rating >= 4.5 THEN l.price END) as avg_price_high_rated,
                AVG(CASE WHEN r.rating < 4.5 THEN l.price END) as avg_price_low_rated
            FROM Listing l
            LEFT JOIN Host h ON l.host_id = h.host_id
            LEFT JOIN Neighbourhood n ON l.listing_id = n.listing_id
            LEFT JOIN Review r ON l.listing_id = r.listing_id
        """)
        
        # Create listing analytics view
        cur.execute("""
            CREATE MATERIALIZED VIEW listing_analytics AS
            SELECT 
                l.listing_id,
                l.name as listing_name,
                l.price,
                l.room_type,
                l.accommodates,
                l.bedrooms,
                l.bathrooms,
                l.minimum_nights,
                l.instant_bookable,
                h.host_name,
                h.is_superhost,
                n.name as neighbourhood_name,
                n.neighbourhood_group,
                AVG(r.rating) as avg_rating,
                COUNT(r.review_id) as review_count,
                AVG(r.accuracy) as avg_accuracy,
                AVG(r.location) as avg_location_score,
                CASE 
                    WHEN AVG(r.rating) >= 4.5 THEN 'Top Performer'
                    WHEN AVG(r.rating) >= 4.0 THEN 'Good Performer'
                    WHEN AVG(r.rating) >= 3.5 THEN 'Average Performer'
                    ELSE 'Needs Improvement'
                END as performance_status,
                CASE 
                    WHEN l.price > (SELECT AVG(l2.price) FROM Listing l2 JOIN Neighbourhood n2 ON l2.listing_id = n2.listing_id WHERE n2.name = n.name) * 1.2 THEN 'Above Market'
                    WHEN l.price < (SELECT AVG(l2.price) FROM Listing l2 JOIN Neighbourhood n2 ON l2.listing_id = n2.listing_id WHERE n2.name = n.name) * 0.8 THEN 'Below Market'
                    ELSE 'Market Rate'
                END as price_competitiveness
            FROM Listing l
            JOIN Host h ON l.host_id = h.host_id
            JOIN Neighbourhood n ON l.listing_id = n.listing_id
            LEFT JOIN Review r ON l.listing_id = r.listing_id
            GROUP BY l.listing_id, l.name, l.price, l.room_type, l.accommodates, l.bedrooms, 
                     l.bathrooms, l.minimum_nights, l.instant_bookable, h.host_name, h.is_superhost, 
                     n.name, n.neighbourhood_group
        """)
        
        # Create indexes
        cur.execute("CREATE INDEX idx_host_performance_rating ON host_performance_analytics(avg_rating)")
        cur.execute("CREATE INDEX idx_host_performance_tier ON host_performance_analytics(performance_tier)")
        cur.execute("CREATE INDEX idx_neighbourhood_price ON neighbourhood_analytics(avg_price)")
        cur.execute("CREATE INDEX idx_neighbourhood_rating ON neighbourhood_analytics(avg_rating)")
        cur.execute("CREATE INDEX idx_price_trends_room_type ON price_trends_analytics(room_type)")
        cur.execute("CREATE INDEX idx_listing_performance ON listing_analytics(performance_status)")
        
        # Create refresh function
        cur.execute("""
            CREATE OR REPLACE FUNCTION refresh_analytics_views()
            RETURNS TRIGGER AS $refresh_trigger$
            BEGIN
                REFRESH MATERIALIZED VIEW host_performance_analytics;
                REFRESH MATERIALIZED VIEW neighbourhood_analytics;
                REFRESH MATERIALIZED VIEW price_trends_analytics;
                REFRESH MATERIALIZED VIEW market_overview_analytics;
                REFRESH MATERIALIZED VIEW listing_analytics;
                RETURN NULL;
            END;
            $refresh_trigger$ LANGUAGE plpgsql
        """)
        
        # Create initialize function
        cur.execute("""
            CREATE OR REPLACE FUNCTION initialize_analytics_views()
            RETURNS void AS $init_views$
            BEGIN
                REFRESH MATERIALIZED VIEW host_performance_analytics;
                REFRESH MATERIALIZED VIEW neighbourhood_analytics;
                REFRESH MATERIALIZED VIEW price_trends_analytics;
                REFRESH MATERIALIZED VIEW market_overview_analytics;
                REFRESH MATERIALIZED VIEW listing_analytics;
            END;
            $init_views$ LANGUAGE plpgsql
        """)
        
        # Create triggers
        cur.execute("DROP TRIGGER IF EXISTS trigger_listing_analytics_refresh ON Listing")
        cur.execute("DROP TRIGGER IF EXISTS trigger_review_analytics_refresh ON Review")
        cur.execute("DROP TRIGGER IF EXISTS trigger_host_analytics_refresh ON Host")
        cur.execute("DROP TRIGGER IF EXISTS trigger_neighbourhood_analytics_refresh ON Neighbourhood")
        
        cur.execute("""
            CREATE TRIGGER trigger_listing_analytics_refresh
                AFTER INSERT OR UPDATE OR DELETE ON Listing
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_analytics_views()
        """)
        
        cur.execute("""
            CREATE TRIGGER trigger_review_analytics_refresh
                AFTER INSERT OR UPDATE OR DELETE ON Review
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_analytics_views()
        """)
        
        cur.execute("""
            CREATE TRIGGER trigger_host_analytics_refresh
                AFTER INSERT OR UPDATE OR DELETE ON Host
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_analytics_views()
        """)
        
        cur.execute("""
            CREATE TRIGGER trigger_neighbourhood_analytics_refresh
                AFTER INSERT OR UPDATE OR DELETE ON Neighbourhood
                FOR EACH STATEMENT
                EXECUTE FUNCTION refresh_analytics_views()
        """)
        
        # Initialize the materialized views
        cur.execute("SELECT initialize_analytics_views()")
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"Error initializing analytics views: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def get_market_overview() -> Dict[str, Any]:
    """
    Get overall market statistics
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM market_overview_analytics")
        row = cur.fetchone()
        
        if row:
            return {
                'total_listings': int(row[0]) if row[0] else 0,
                'total_hosts': int(row[1]) if row[1] else 0,
                'total_neighbourhoods': int(row[2]) if row[2] else 0,
                'overall_avg_price': float(row[3]) if row[3] else 0.0,
                'min_price': float(row[4]) if row[4] else 0.0,
                'max_price': float(row[5]) if row[5] else 0.0,
                'overall_avg_rating': float(row[6]) if row[6] else 0.0,
                'total_reviews': int(row[7]) if row[7] else 0,
                'avg_accommodates': float(row[8]) if row[8] else 0.0,
                'instant_bookable_count': int(row[9]) if row[9] else 0,
                'superhost_count': int(row[10]) if row[10] else 0,
                'entire_home_count': int(row[11]) if row[11] else 0,
                'private_room_count': int(row[12]) if row[12] else 0,
                'shared_room_count': int(row[13]) if row[13] else 0,
                'hotel_room_count': int(row[14]) if row[14] else 0,
                'avg_price_high_rated': float(row[15]) if row[15] else 0.0,
                'avg_price_low_rated': float(row[16]) if row[16] else 0.0
            }
        else:
            return {}
            
    except Exception as e:
        print(f"Error getting market overview: {e}")
        return {}
    finally:
        cur.close()
        conn.close()

def get_host_performance(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top performing hosts
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM host_performance_analytics 
            ORDER BY avg_rating DESC NULLS LAST, total_reviews DESC 
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        hosts = []
        
        for row in rows:
            hosts.append({
                'host_id': int(row[0]),
                'host_name': row[1] or 'N/A',
                'host_since': row[2],
                'is_superhost': bool(row[3]) if row[3] is not None else False,
                'host_response_rate': int(row[4]) if row[4] else 0,
                'host_acceptance_rate': int(row[5]) if row[5] else 0,
                'total_listings': int(row[6]) if row[6] else 0,
                'avg_listing_price': float(row[7]) if row[7] else 0.0,
                'avg_rating': float(row[8]) if row[8] else 0.0,
                'total_reviews': int(row[9]) if row[9] else 0,
                'instant_bookable_count': int(row[10]) if row[10] else 0,
                'avg_accommodates': float(row[11]) if row[11] else 0.0,
                'performance_tier': row[12] or 'N/A'
            })
        
        return hosts
        
    except Exception as e:
        print(f"Error getting host performance: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_neighbourhood_analytics(limit: int = 15) -> List[Dict[str, Any]]:
    """
    Get neighbourhood analytics
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM neighbourhood_analytics 
            ORDER BY avg_rating DESC NULLS LAST, total_listings DESC 
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        neighbourhoods = []
        
        for row in rows:
            neighbourhoods.append({
                'neighbourhood_name': row[0] or 'N/A',
                'neighbourhood_group': row[1] or 'N/A',
                'total_listings': int(row[2]) if row[2] else 0,
                'avg_price': float(row[3]) if row[3] else 0.0,
                'min_price': float(row[4]) if row[4] else 0.0,
                'max_price': float(row[5]) if row[5] else 0.0,
                'avg_rating': float(row[6]) if row[6] else 0.0,
                'total_reviews': int(row[7]) if row[7] else 0,
                'avg_accommodates': float(row[8]) if row[8] else 0.0,
                'avg_minimum_nights': float(row[9]) if row[9] else 0.0,
                'room_type_variety': int(row[10]) if row[10] else 0,
                'instant_bookable_count': int(row[11]) if row[11] else 0,
                'avg_bedrooms': float(row[12]) if row[12] else 0.0,
                'avg_bathrooms': float(row[13]) if row[13] else 0.0,
                'price_category': row[14] or 'N/A'
            })
        
        return neighbourhoods
        
    except Exception as e:
        print(f"Error getting neighbourhood analytics: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_price_trends() -> List[Dict[str, Any]]:
    """
    Get price trends by room type
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM price_trends_analytics 
            ORDER BY avg_price DESC
        """)
        
        rows = cur.fetchall()
        trends = []
        
        for row in rows:
            trends.append({
                'room_type': row[0] or 'N/A',
                'avg_price': float(row[1]) if row[1] else 0.0,
                'listing_count': int(row[2]) if row[2] else 0,
                'min_price': float(row[3]) if row[3] else 0.0,
                'max_price': float(row[4]) if row[4] else 0.0,
                'median_price': float(row[5]) if row[5] else 0.0,
                'avg_accommodates': float(row[6]) if row[6] else 0.0,
                'avg_rating': float(row[7]) if row[7] else 0.0,
                'total_reviews': int(row[8]) if row[8] else 0,
                'avg_minimum_nights': float(row[9]) if row[9] else 0.0,
                'instant_bookable_count': int(row[10]) if row[10] else 0
            })
        
        return trends
        
    except Exception as e:
        print(f"Error getting price trends: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def get_top_listings(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get top performing listings
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            SELECT * FROM listing_analytics 
            WHERE performance_status IN ('Top Performer', 'Good Performer')
            ORDER BY avg_rating DESC NULLS LAST, review_count DESC 
            LIMIT %s
        """, (limit,))
        
        rows = cur.fetchall()
        listings = []
        
        for row in rows:
            listings.append({
                'listing_id': int(row[0]),
                'listing_name': row[1] or 'N/A',
                'price': float(row[2]) if row[2] else 0.0,
                'room_type': row[3] or 'N/A',
                'accommodates': int(row[4]) if row[4] else 0,
                'bedrooms': int(row[5]) if row[5] else 0,
                'bathrooms': float(row[6]) if row[6] else 0.0,
                'minimum_nights': int(row[7]) if row[7] else 0,
                'instant_bookable': bool(row[8]) if row[8] is not None else False,
                'host_name': row[9] or 'N/A',
                'is_superhost': bool(row[10]) if row[10] is not None else False,
                'neighbourhood_name': row[11] or 'N/A',
                'neighbourhood_group': row[12] or 'N/A',
                'avg_rating': float(row[13]) if row[13] else 0.0,
                'review_count': int(row[14]) if row[14] else 0,
                'avg_accuracy': float(row[15]) if row[15] else 0.0,
                'avg_location_score': float(row[16]) if row[16] else 0.0,
                'performance_status': row[17] or 'N/A',
                'price_competitiveness': row[18] or 'N/A'
            })
        
        return listings
        
    except Exception as e:
        print(f"Error getting top listings: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def refresh_analytics_views():
    """
    Manually refresh all materialized views
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if the function exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pg_proc 
                WHERE proname = 'initialize_analytics_views'
            )
        """)
        function_exists = cur.fetchone()[0]
        
        if function_exists:
            cur.execute("SELECT initialize_analytics_views()")
            conn.commit()
            return True
        else:
            # If function doesn't exist, return false to indicate failure
            print("Analytics views not found, please restart the application to initialize them.")
            return False
    except Exception as e:
        conn.rollback()
        print(f"Error refreshing analytics views: {e}")
        return False
    finally:
        cur.close()
        conn.close() 