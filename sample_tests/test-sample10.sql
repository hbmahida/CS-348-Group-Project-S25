-- Advanced Feature: Host Details and Revenue Calculation Validation
-- Test comprehensive host information, listing details, and revenue calculations

-- Test 1: Get detailed information for Host 1 (John Smith) including all listings
SELECT h.host_id, h.host_name, h.host_since, h.host_location, h.is_superhost, 
       h.host_response_rate, h.host_acceptance_rate, h.referred_by,
       r.host_name as referrer_name
FROM Host h
LEFT JOIN Host r ON h.referred_by = r.host_id
WHERE h.host_id = 1;

-- Test 2: Get all listings for Host 1 with detailed information
SELECT l.listing_id, l.name, l.room_type, l.accommodates, l.price,
       l.minimum_nights, l.instant_bookable, l.created_date,
       n.name as neighbourhood_name, n.neighbourhood_group,
       COALESCE(AVG(r.rating), 0) as avg_rating,
       COUNT(r.review_id) as review_count,
       COALESCE(SUM(r.number_of_reviews), 0) as total_reviews,
       (l.price * 30) as monthly_revenue
FROM Listing l
LEFT JOIN Neighbourhood n ON l.listing_id = n.listing_id
LEFT JOIN Review r ON l.listing_id = r.listing_id
WHERE l.host_id = 1
GROUP BY l.listing_id, l.name, l.room_type, l.accommodates, l.price,
         l.minimum_nights, l.instant_bookable, l.created_date,
         n.name, n.neighbourhood_group
ORDER BY l.created_date DESC;

-- Test 3: Calculate performance metrics for Host 1
SELECT 
    COUNT(l.listing_id) as total_listings,
    COALESCE(SUM(l.price), 0) as total_daily_revenue,
    COALESCE(SUM(l.price * 30), 0) as total_monthly_revenue,
    COALESCE(AVG(l.price), 0) as avg_price,
    COALESCE(AVG(r.rating), 0) as avg_rating,
    COALESCE(SUM(r.number_of_reviews), 0) as total_reviews
FROM Listing l
LEFT JOIN Review r ON l.listing_id = r.listing_id
WHERE l.host_id = 1;

-- Test 4: Get amenities for Host 1's listings
SELECT l.listing_id, l.name, la.amenity
FROM Listing l
JOIN ListingAmenity la ON l.listing_id = la.listing_id
WHERE l.host_id = 1
ORDER BY l.listing_id, la.amenity;

-- Test 5: Validate revenue calculations across all hosts
SELECT h.host_id, h.host_name,
       COUNT(l.listing_id) as listing_count,
       COALESCE(SUM(l.price), 0) as daily_revenue,
       COALESCE(SUM(l.price * 30), 0) as monthly_revenue
FROM Host h
LEFT JOIN Listing l ON h.host_id = l.host_id
GROUP BY h.host_id, h.host_name
ORDER BY monthly_revenue DESC;

-- Test 6: Network position for Host 2 (Maria Garcia) - should show referral chain
WITH RECURSIVE find_network_root AS (
    -- Find root by going up the chain
    SELECT host_id, host_name, referred_by, 0 as steps_up
    FROM Host WHERE host_id = 2
    
    UNION ALL
    
    SELECT h.host_id, h.host_name, h.referred_by, f.steps_up + 1
    FROM Host h
    JOIN find_network_root f ON h.host_id = f.referred_by
    WHERE f.steps_up < 10
),
network_from_root AS (
    -- Now traverse down from root
    SELECT h.host_id, h.host_name, h.referred_by, 0 as level,
           CAST(h.host_name AS VARCHAR(500)) as path
    FROM Host h 
    WHERE h.referred_by IS NULL 
      AND h.host_id IN (SELECT host_id FROM find_network_root WHERE referred_by IS NULL)
    
    UNION ALL
    
    SELECT h.host_id, h.host_name, h.referred_by, n.level + 1,
           CAST(n.path || ' → ' || h.host_name AS VARCHAR(500))
    FROM Host h
    JOIN network_from_root n ON h.referred_by = n.host_id
    WHERE n.level < 10
)
SELECT level, path
FROM network_from_root
WHERE host_id = 2; 