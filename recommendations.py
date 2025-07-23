import logging
from typing import List, Dict, Optional, Tuple
from db_config import DB_CONFIG
import psycopg2
import math

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

class RecommendationEngine:
    """
    Modular recommendation engine using recursive SQL and similarity scoring
    """
    
    def __init__(self):
        self.similarity_weights = {
            'price': 0.3,
            'location': 0.25,
            'amenity': 0.25,
            'host': 0.1,
            'rating': 0.1
        }

    def get_listing_recommendations(self, listing_id: int, max_results: int = 10, 
                                 similarity_threshold: float = 0.6) -> List[Dict]:
        """
        Get recommendations for a listing using recursive similarity analysis
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # First, get the base listing details
            base_listing = self._get_listing_details(cursor, listing_id)
            if not base_listing:
                return []
            
            # Execute recursive recommendation query
            recommendations = self._execute_recursive_recommendation_query(
                cursor, listing_id, max_results, similarity_threshold
            )
            
            print(f"Found {len(recommendations)} potential recommendations")
            
            # Calculate detailed similarity scores
            scored_recommendations = []
            for rec in recommendations:
                if rec['listing_id'] != listing_id:  # Don't recommend the same listing
                    try:
                        score_details = self._calculate_detailed_similarity(
                            cursor, base_listing, rec
                        )
                        rec.update(score_details)
                        scored_recommendations.append(rec)
                    except Exception as e:
                        import traceback
                        print(f"Error calculating similarity for listing {rec['listing_id']}: {e}")
                        print(f"Traceback: {traceback.format_exc()}")
                        continue
            
            # Sort by similarity score
            scored_recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            cursor.close()
            conn.close()
            
            return scored_recommendations[:max_results]
            
        except Exception as e:
            import traceback
            logging.error(f"Error getting recommendations: {e}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return []

    def _get_listing_details(self, cursor, listing_id: int) -> Optional[Dict]:
        """Get detailed information about a listing"""
        query = """
            SELECT 
                l.listing_id, l.name, l.price, l.room_type, l.accommodates,
                l.bathrooms, l.bedrooms, l.beds, l.host_id,
                h.host_name, h.is_superhost, h.host_response_rate,
                n.name as neighbourhood_name, n.latitude, n.longitude,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(r.review_id) as review_count
            FROM listing l
            LEFT JOIN host h ON l.host_id = h.host_id
            LEFT JOIN neighbourhood n ON l.listing_id = n.listing_id
            LEFT JOIN review r ON l.listing_id = r.listing_id
            WHERE l.listing_id = %s
            GROUP BY l.listing_id, h.host_id, n.neighbourhood_id
        """
        
        cursor.execute(query, (listing_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            listing = dict(zip(columns, result))
            
            # Get amenities
            cursor.execute(
                "SELECT amenity FROM listingamenity WHERE listing_id = %s",
                (listing_id,)
            )
            amenities = [row[0] for row in cursor.fetchall()]
            listing['amenities'] = amenities
            
            return listing
        
        return None

    def _execute_recursive_recommendation_query(self, cursor, listing_id: int, 
                                              max_results: int, threshold: float) -> List[Dict]:
        """Execute the recursive CTE query for finding similar listings"""
        
        # First, get the base listing details to use for filtering
        cursor.execute("SELECT room_type, price FROM listing WHERE listing_id = %s", (listing_id,))
        base_result = cursor.fetchone()
        if not base_result:
            return []
        
        # Convert to float to handle Decimal types from PostgreSQL
        base_room_type, base_price = base_result
        base_price = float(base_price)
        
        # Simplified recursive query without aggregates
        recursive_query = """
            WITH RECURSIVE listing_similarity_tree AS (
                -- Base case: Start with the selected listing
                SELECT 
                    l.listing_id as source_listing_id,
                    l.listing_id as recommended_listing_id,
                    1.0 as similarity_score,
                    0 as depth_level,
                    ARRAY[l.listing_id] as path
                FROM listing l
                WHERE l.listing_id = %s
                
                UNION ALL
                
                -- Recursive case: Find similar listings
                SELECT 
                    lst.source_listing_id,
                    l2.listing_id as recommended_listing_id,
                    0.8 as similarity_score,  -- Placeholder, will be calculated properly
                    lst.depth_level + 1,
                    lst.path || l2.listing_id
                FROM listing_similarity_tree lst
                JOIN listing l2 ON l2.listing_id != lst.recommended_listing_id
                WHERE lst.depth_level < 2  -- Max 2 levels deep
                  AND NOT l2.listing_id = ANY(lst.path)  -- Avoid cycles
                  AND l2.room_type = %s  -- Same room type
                  AND ABS(l2.price - %s) <= %s  -- Price within range
            )
            SELECT DISTINCT recommended_listing_id as listing_id
            FROM listing_similarity_tree
            WHERE depth_level > 0  -- Exclude the source listing
            LIMIT %s
        """
        
        # Use a reasonable price range, but ensure it's not too restrictive
        price_range = max(base_price * 0.5, 50.0) if base_price > 0 else 1000.0  # At least $50 range
        # Parameters: listing_id, room_type, base_price, price_range, limit
        params = (listing_id, base_room_type, base_price, price_range, max_results * 3)
        print(f"Executing recursive query with params: {params}")
        cursor.execute(recursive_query, params)
        listing_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Recursive query found {len(listing_ids)} listing IDs")
        print(f"Base room type: {base_room_type}, Base price: {base_price}, Price range: {price_range}")
        
        if not listing_ids:
            return []
        
        # Now get full details for these listings including aggregated review data
        placeholders = ','.join(['%s'] * len(listing_ids))
        detail_query = f"""
            SELECT 
                l.listing_id,
                l.name,
                l.price,
                l.room_type,
                l.accommodates,
                l.bathrooms,
                l.bedrooms,
                l.beds,
                l.host_id,
                h.host_name,
                h.is_superhost,
                h.host_response_rate,
                n.name as neighbourhood_name,
                n.latitude,
                n.longitude,
                COALESCE(AVG(r.rating), 0) as avg_rating,
                COUNT(r.review_id) as review_count
            FROM listing l
            LEFT JOIN host h ON l.host_id = h.host_id
            LEFT JOIN neighbourhood n ON l.listing_id = n.listing_id
            LEFT JOIN review r ON l.listing_id = r.listing_id
            WHERE l.listing_id IN ({placeholders})
            GROUP BY l.listing_id, h.host_id, n.neighbourhood_id
            ORDER BY l.name
        """
        
        cursor.execute(detail_query, listing_ids)
        results = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in results]

    def _calculate_detailed_similarity(self, cursor, base_listing: Dict, 
                                     candidate_listing: Dict) -> Dict:
        """Calculate detailed similarity score between two listings"""
        
        # Price similarity (inverse of price difference, normalized)
        # Convert to float to handle Decimal types from PostgreSQL
        base_price = float(base_listing['price'])
        candidate_price = float(candidate_listing['price'])
        price_diff = abs(base_price - candidate_price)
        max_price = max(base_price, candidate_price)
        price_similarity = 1.0 - (price_diff / max_price) if max_price > 0 else 1.0
        
        # Location similarity (using geographic distance)
        location_similarity = self._calculate_location_similarity(
            base_listing, candidate_listing
        )
        
        # Amenity similarity
        amenity_similarity = self._calculate_amenity_similarity(
            cursor, base_listing['listing_id'], candidate_listing['listing_id']
        )
        
        # Host similarity
        host_similarity = self._calculate_host_similarity(base_listing, candidate_listing)
        
        # Rating similarity
        rating_similarity = self._calculate_rating_similarity(base_listing, candidate_listing)
        
        # Calculate weighted final score - ensure all values are float
        final_score = (
            float(price_similarity) * self.similarity_weights['price'] +
            float(location_similarity) * self.similarity_weights['location'] +
            float(amenity_similarity) * self.similarity_weights['amenity'] +
            float(host_similarity) * self.similarity_weights['host'] +
            float(rating_similarity) * self.similarity_weights['rating']
        )
        
        return {
            'similarity_score': round(float(final_score), 3),
            'price_similarity': round(float(price_similarity), 3),
            'location_similarity': round(float(location_similarity), 3),
            'amenity_similarity': round(float(amenity_similarity), 3),
            'host_similarity': round(float(host_similarity), 3),
            'rating_similarity': round(float(rating_similarity), 3)
        }

    def _calculate_location_similarity(self, base_listing: Dict, candidate_listing: Dict) -> float:
        """Calculate similarity based on geographic distance"""
        try:
            if not all([base_listing.get('latitude'), base_listing.get('longitude'),
                       candidate_listing.get('latitude'), candidate_listing.get('longitude')]):
                return 0.5  # Default similarity if location data is missing
            
            # Haversine formula for distance calculation
            # Convert to float to handle Decimal types from PostgreSQL
            lat1, lon1 = math.radians(float(base_listing['latitude'])), math.radians(float(base_listing['longitude']))
            lat2, lon2 = math.radians(float(candidate_listing['latitude'])), math.radians(float(candidate_listing['longitude']))
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance_km = 6371 * c  # Earth's radius in kilometers
            
            # Convert distance to similarity score (closer = more similar)
            # Assume max useful distance is 50km
            similarity = max(0, 1 - (distance_km / 50))
            return similarity
            
        except Exception:
            return 0.5

    def _calculate_amenity_similarity(self, cursor, listing1_id: int, listing2_id: int) -> float:
        """Calculate similarity based on shared amenities"""
        try:
            # Get amenities for both listings
            cursor.execute(
                "SELECT amenity FROM listingamenity WHERE listing_id IN (%s, %s)",
                (listing1_id, listing2_id)
            )
            
            amenities_1 = set()
            amenities_2 = set()
            
            cursor.execute("SELECT amenity FROM listingamenity WHERE listing_id = %s", (listing1_id,))
            amenities_1 = set(row[0] for row in cursor.fetchall())
            
            cursor.execute("SELECT amenity FROM listingamenity WHERE listing_id = %s", (listing2_id,))
            amenities_2 = set(row[0] for row in cursor.fetchall())
            
            if not amenities_1 and not amenities_2:
                return 1.0  # Both have no amenities
            
            if not amenities_1 or not amenities_2:
                return 0.0  # One has amenities, other doesn't
            
            # Jaccard similarity
            intersection = len(amenities_1 & amenities_2)
            union = len(amenities_1 | amenities_2)
            
            return float(intersection) / float(union) if union > 0 else 0.0
            
        except Exception:
            return 0.5

    def _calculate_host_similarity(self, base_listing: Dict, candidate_listing: Dict) -> float:
        """Calculate similarity based on host characteristics"""
        try:
            score = 0.0
            
            # Same host = perfect similarity
            if base_listing['host_id'] == candidate_listing['host_id']:
                return 1.0
            
            # Superhost status
            if base_listing.get('is_superhost') == candidate_listing.get('is_superhost'):
                score += 0.5
            
            # Response rate similarity
            if base_listing.get('host_response_rate') and candidate_listing.get('host_response_rate'):
                # Convert to float to handle Decimal types from PostgreSQL
                rate1 = float(base_listing['host_response_rate'])
                rate2 = float(candidate_listing['host_response_rate'])
                rate_diff = abs(rate1 - rate2)
                score += 0.5 * (1 - rate_diff / 100)
            
            return min(score, 1.0)
            
        except Exception:
            return 0.5

    def _calculate_rating_similarity(self, base_listing: Dict, candidate_listing: Dict) -> float:
        """Calculate similarity based on ratings"""
        try:
            # Convert to float to handle Decimal types from PostgreSQL
            rating1 = float(base_listing.get('avg_rating', 0))
            rating2 = float(candidate_listing.get('avg_rating', 0))
            
            if rating1 == 0 and rating2 == 0:
                return 1.0  # Both have no ratings
            
            if rating1 == 0 or rating2 == 0:
                return 0.5  # One has ratings, other doesn't
            
            # Rating difference similarity
            rating_diff = abs(rating1 - rating2)
            return 1.0 - (rating_diff / 5.0)  # Normalize by max possible rating difference
            
        except Exception:
            return 0.5

    def update_similarity_weights(self, weights: Dict[str, float]) -> bool:
        """Update similarity calculation weights"""
        try:
            # Validate weights sum to 1.0
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                return False
            
            self.similarity_weights.update(weights)
            return True
            
        except Exception:
            return False

    def get_listing_details_for_comparison(self, listing_id: int) -> Optional[Dict]:
        """Get detailed listing information for comparison display"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            listing = self._get_listing_details(cursor, listing_id)
            
            cursor.close()
            conn.close()
            
            return listing
            
        except Exception as e:
            logging.error(f"Error getting listing details: {e}")
            return None

    def search_listings(self, query: str, limit: int = 20) -> List[Dict]:
        """Search listings by name or description"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            search_query = """
                SELECT 
                    l.listing_id, l.name, l.price, l.room_type, 
                    l.accommodates, n.name as neighbourhood_name,
                    COALESCE(AVG(r.rating), 0) as avg_rating,
                    COUNT(r.review_id) as review_count
                FROM listing l
                LEFT JOIN neighbourhood n ON l.listing_id = n.listing_id
                LEFT JOIN review r ON l.listing_id = r.listing_id
                WHERE l.name ILIKE %s OR l.description ILIKE %s
                GROUP BY l.listing_id, n.neighbourhood_id
                ORDER BY l.name
                LIMIT %s
            """
            
            search_term = f"%{query}%"
            cursor.execute(search_query, (search_term, search_term, limit))
            results = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            listings = [dict(zip(columns, row)) for row in results]
            
            cursor.close()
            conn.close()
            
            return listings
            
        except Exception as e:
            logging.error(f"Error searching listings: {e}")
            return []


# Global instance
recommendation_engine = RecommendationEngine() 