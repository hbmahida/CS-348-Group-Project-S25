-- Fetch top 3 listings in a selected neighbourhood
SELECT
    l.listing_id,
    l.name,
    l.price,
    n.name AS neighbourhood,
    COALESCE(AVG(r.rating), 0) AS avg_rating
    FROM Listing l
    JOIN Neighbourhood n ON n.listing_id = l.listing_id
    LEFT JOIN Review r ON r.listing_id = l.listing_id
    GROUP BY l.listing_id, l.name, l.price, n.name
    ORDER BY avg_rating DESC, l.price ASC
    LIMIT 3;