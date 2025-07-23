-- Debug queries for Brokerage Firm Network Analysis

-- 1. Check basic referral relationships
SELECT h.host_id, h.host_name, h.referred_by, r.host_name as referrer_name
FROM Host h
LEFT JOIN Host r ON h.referred_by = r.host_id
ORDER BY h.host_id;

-- 2. Test recursive query for Host 1 (simplified)
WITH RECURSIVE referral_network AS (
    SELECT host_id, host_name, referred_by, 0 as level
    FROM Host WHERE host_id = 1
    UNION ALL
    SELECT h.host_id, h.host_name, h.referred_by, rn.level + 1
    FROM Host h
    JOIN referral_network rn ON h.referred_by = rn.host_id
    WHERE rn.level < 5
)
SELECT level, host_id, host_name, referred_by
FROM referral_network
ORDER BY level, host_id;

-- 3. Check revenue calculations
SELECT h.host_id, h.host_name, 
       COUNT(l.listing_id) as total_listings,
       COALESCE(SUM(l.price), 0) as total_daily_revenue,
       COALESCE(SUM(l.price * 30), 0) as total_monthly_revenue
FROM Host h
LEFT JOIN Listing l ON h.host_id = l.host_id
GROUP BY h.host_id, h.host_name
ORDER BY h.host_id;

-- 4. Test full recursive query with revenue (Host 1)
WITH RECURSIVE referral_network AS (
    SELECT h.host_id, h.host_name, h.referred_by, 0 as network_level,
           CAST(h.host_name AS VARCHAR(500)) as referral_path
    FROM Host h WHERE h.host_id = 1
    UNION ALL
    SELECT h.host_id, h.host_name, h.referred_by, rn.network_level + 1,
           CAST(rn.referral_path || ' -> ' || h.host_name AS VARCHAR(500))
    FROM Host h
    JOIN referral_network rn ON h.referred_by = rn.host_id
    WHERE rn.network_level < 5
)
SELECT rn.network_level, rn.host_id, rn.host_name, rn.referral_path,
       COUNT(l.listing_id) as total_listings,
       COALESCE(SUM(l.price * 30), 0) as monthly_revenue
FROM referral_network rn
LEFT JOIN Listing l ON rn.host_id = l.host_id
GROUP BY rn.network_level, rn.host_id, rn.host_name, rn.referral_path
ORDER BY rn.network_level, rn.host_id;

-- 5. Check for potential circular references
WITH RECURSIVE circular_check AS (
    SELECT host_id, referred_by, ARRAY[host_id] as path, 0 as depth
    FROM Host WHERE referred_by IS NOT NULL
    UNION ALL
    SELECT h.host_id, h.referred_by, cc.path || h.host_id, cc.depth + 1
    FROM Host h
    JOIN circular_check cc ON h.host_id = cc.referred_by
    WHERE h.host_id != ALL(cc.path) AND cc.depth < 10
)
SELECT * FROM circular_check WHERE host_id = ANY(path[2:array_length(path,1)]); 