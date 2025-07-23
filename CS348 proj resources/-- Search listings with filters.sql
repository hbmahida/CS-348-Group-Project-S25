-- Search listings with filters
SELECT l.listing_id, l.name, l.price, l.room_type, n.name as neighborhood,
       AVG(r.rating) as avg_rating, COUNT(r.review_id) as review_count
FROM Listings l
JOIN Neighborhoods n ON l.neighborhood_id = n.neighborhood_id
LEFT JOIN Reviews r ON l.listing_id = r.listing_id
WHERE l.price BETWEEN ? AND ?
  AND l.room_type = ?
  AND n.name = ?
  AND l.availability_365 > 0
GROUP BY l.listing_id, l.name, l.price, l.room_type, n.name
ORDER BY avg_rating DESC, l.price ASC;

-- Find private rooms in Distillery District, $50–$150
SELECT 
  l.listing_id,
  l.name,
  l.price,
  l.room_type,
  n.name           AS neighborhood,
  ROUND(AVG(r.rating),1)      AS avg_rating,
  COUNT(r.review_id)           AS review_count
FROM Listings l
JOIN Neighborhoods n 
  ON l.neighborhood_id = n.neighborhood_id
LEFT JOIN Reviews r 
  ON l.listing_id = r.listing_id
WHERE l.price        BETWEEN 50 AND 150
  AND l.room_type    = 'Private room'
  AND n.name         = 'Distillery District'
  AND l.availability_365 > 0
GROUP BY 
  l.listing_id, l.name, l.price, l.room_type, n.name
ORDER BY 
  avg_rating DESC, l.price ASC;



| listing_id  | name                              |  price | room_type    | neighborhood         | avg_rating | review_count  |
| ----------: | --------------------------------- | -----: | ------------ | ------------------- | ----------: | ------------: |
|         102 | “Cozy Loft in Distillery”         | 120.00 | Private room | Distillery District |         4.8 |            64 |
|          87 | “Historic Carriage House Room”    |  75.00 | Private room | Distillery District |         4.5 |            42 |
|          95 | “Bright Studio by the Distillery” |  95.00 | Private room | Distillery District |         4.3 |            30 |
