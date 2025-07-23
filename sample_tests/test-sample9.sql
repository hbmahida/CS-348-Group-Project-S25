-- Advanced Feature: Host Referral Network Analysis using Recursive Queries
-- Test the recursive CTE to analyze referral networks

-- Test 1: Basic referral network traversal for Host 1 (John Smith)
-- This should show the complete referral network starting from John Smith
WITH RECURSIVE referral_network AS (
    -- Base case: Find the root host (John Smith)
    SELECT 
        h.host_id,
        h.host_name,
        h.referred_by,
        h.host_since,
        h.is_superhost,
        h.host_listings_count,
        0 as network_level,
        CAST(h.host_name AS VARCHAR(500)) as referral_path
    FROM Host h
    WHERE h.host_id = 1
    
    UNION ALL
    
    -- Recursive case: Find all hosts referred by previous level
    SELECT 
        h.host_id,
        h.host_name,
        h.referred_by,
        h.host_since,
        h.is_superhost,
        h.host_listings_count,
        rn.network_level + 1,
        CAST(rn.referral_path || ' -> ' || h.host_name AS VARCHAR(500))
    FROM Host h
    JOIN referral_network rn ON h.referred_by = rn.host_id
    WHERE rn.network_level < 5
)
SELECT 
    rn.network_level,
    rn.host_id,
    rn.host_name,
    rn.referral_path,
    rn.host_since,
    rn.is_superhost,
    rn.host_listings_count,
    COALESCE(AVG(l.price), 0) as avg_listing_price,
    COUNT(l.listing_id) as total_listings,
    COALESCE(AVG(r.rating), 0) as avg_rating,
    COUNT(r.review_id) as total_reviews
FROM referral_network rn
LEFT JOIN Listing l ON rn.host_id = l.host_id
LEFT JOIN Review r ON l.listing_id = r.listing_id
GROUP BY rn.network_level, rn.host_id, rn.host_name, rn.referral_path, 
         rn.host_since, rn.is_superhost, rn.host_listings_count
ORDER BY rn.network_level, rn.host_id;

-- Test 2: Network performance summary for Host 1's network
WITH RECURSIVE referral_network AS (
    SELECT h.host_id, h.host_name, h.referred_by, 0 as network_level
    FROM Host h WHERE h.host_id = 1
    UNION ALL
    SELECT h.host_id, h.host_name, h.referred_by, rn.network_level + 1
    FROM Host h
    JOIN referral_network rn ON h.referred_by = rn.host_id
    WHERE rn.network_level < 5
)
SELECT 
    COUNT(*) as total_network_hosts,
    MAX(network_level) as max_network_depth,
    COALESCE(SUM(l.price * 30), 0) as estimated_monthly_network_revenue,
    COALESCE(AVG(r.rating), 0) as network_avg_rating,
    COUNT(DISTINCT CASE WHEN h.is_superhost THEN h.host_id END) as superhost_count,
    COUNT(DISTINCT l.listing_id) as total_network_listings
FROM referral_network rn
JOIN Host h ON rn.host_id = h.host_id
LEFT JOIN Listing l ON h.host_id = l.host_id
LEFT JOIN Review r ON l.listing_id = r.listing_id;

-- Test 3: Verify referral relationships exist
SELECT 
    h.host_id,
    h.host_name,
    h.referred_by,
    r.host_name as referrer_name
FROM Host h
LEFT JOIN Host r ON h.referred_by = r.host_id
ORDER BY h.host_id; 