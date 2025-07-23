-- Analytics Dashboard - Materialized Views and Triggers
-- This file contains advanced SQL features: materialized views and triggers for real-time analytics

-- Drop existing materialized views if they exist
DROP MATERIALIZED VIEW IF EXISTS host_performance_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS neighbourhood_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS price_trends_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS market_overview_analytics CASCADE;
DROP MATERIALIZED VIEW IF EXISTS listing_analytics CASCADE;

-- 1. HOST PERFORMANCE ANALYTICS
-- Materialized view for host performance metrics
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
GROUP BY h.host_id, h.host_name, h.host_since, h.is_superhost, h.host_response_rate, h.host_acceptance_rate;

-- 2. NEIGHBOURHOOD ANALYTICS
-- Materialized view for neighbourhood-wise metrics
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
    -- Price category
    CASE 
        WHEN AVG(l.price) >= 200 THEN 'Premium'
        WHEN AVG(l.price) >= 100 THEN 'High'
        WHEN AVG(l.price) >= 50 THEN 'Medium'
        ELSE 'Budget'
    END as price_category
FROM Neighbourhood n
JOIN Listing l ON n.listing_id = l.listing_id
LEFT JOIN Review r ON l.listing_id = r.listing_id
GROUP BY n.name, n.neighbourhood_group;

-- 3. PRICE TRENDS ANALYTICS
-- Materialized view for price analysis by different dimensions
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
GROUP BY l.room_type;

-- 4. MARKET OVERVIEW ANALYTICS
-- Materialized view for overall market statistics
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
    -- Market composition
    COUNT(CASE WHEN l.room_type = 'Entire home/apt' THEN 1 END) as entire_home_count,
    COUNT(CASE WHEN l.room_type = 'Private room' THEN 1 END) as private_room_count,
    COUNT(CASE WHEN l.room_type = 'Shared room' THEN 1 END) as shared_room_count,
    COUNT(CASE WHEN l.room_type = 'Hotel room' THEN 1 END) as hotel_room_count,
    -- Average metrics by performance
    AVG(CASE WHEN r.rating >= 4.5 THEN l.price END) as avg_price_high_rated,
    AVG(CASE WHEN r.rating < 4.5 THEN l.price END) as avg_price_low_rated
FROM Listing l
LEFT JOIN Host h ON l.host_id = h.host_id
LEFT JOIN Neighbourhood n ON l.listing_id = n.listing_id
LEFT JOIN Review r ON l.listing_id = r.listing_id;

-- 5. LISTING ANALYTICS
-- Materialized view for individual listing insights
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
    -- Performance indicators
    CASE 
        WHEN AVG(r.rating) >= 4.5 THEN 'Top Performer'
        WHEN AVG(r.rating) >= 4.0 THEN 'Good Performer'
        WHEN AVG(r.rating) >= 3.5 THEN 'Average Performer'
        ELSE 'Needs Improvement'
    END as performance_status,
    -- Price competitiveness (compared to neighbourhood average)
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
         n.name, n.neighbourhood_group;

-- Create indexes for better performance
CREATE INDEX idx_host_performance_rating ON host_performance_analytics(avg_rating);
CREATE INDEX idx_host_performance_tier ON host_performance_analytics(performance_tier);
CREATE INDEX idx_neighbourhood_price ON neighbourhood_analytics(avg_price);
CREATE INDEX idx_neighbourhood_rating ON neighbourhood_analytics(avg_rating);
CREATE INDEX idx_price_trends_room_type ON price_trends_analytics(room_type);
CREATE INDEX idx_listing_performance ON listing_analytics(performance_status);

-- ========================
-- TRIGGERS FOR REAL-TIME UPDATES
-- ========================

-- Function to refresh all materialized views
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
$refresh_trigger$ LANGUAGE plpgsql;

-- Triggers for Listing table changes
CREATE OR REPLACE TRIGGER trigger_listing_analytics_refresh
    AFTER INSERT OR UPDATE OR DELETE ON Listing
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_analytics_views();

-- Triggers for Review table changes
CREATE OR REPLACE TRIGGER trigger_review_analytics_refresh
    AFTER INSERT OR UPDATE OR DELETE ON Review
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_analytics_views();

-- Triggers for Host table changes
CREATE OR REPLACE TRIGGER trigger_host_analytics_refresh
    AFTER INSERT OR UPDATE OR DELETE ON Host
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_analytics_views();

-- Triggers for Neighbourhood table changes
CREATE OR REPLACE TRIGGER trigger_neighbourhood_analytics_refresh
    AFTER INSERT OR UPDATE OR DELETE ON Neighbourhood
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_analytics_views();

-- Function to initialize/refresh all materialized views (call this after setup)
CREATE OR REPLACE FUNCTION initialize_analytics_views()
RETURNS void AS $init_views$
BEGIN
    REFRESH MATERIALIZED VIEW host_performance_analytics;
    REFRESH MATERIALIZED VIEW neighbourhood_analytics;
    REFRESH MATERIALIZED VIEW price_trends_analytics;
    REFRESH MATERIALIZED VIEW market_overview_analytics;
    REFRESH MATERIALIZED VIEW listing_analytics;
END;
$init_views$ LANGUAGE plpgsql;

-- Call to initialize views
SELECT initialize_analytics_views(); 