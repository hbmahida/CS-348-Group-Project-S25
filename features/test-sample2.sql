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
WHERE 1=1
  AND n.name            = 'Mission District'
  AND l.room_type       = 'Entire home/apt'
  AND l.price           >= 50
  AND l.price           <= 150
  AND l.minimum_nights  >= 2
GROUP BY
  l.listing_id,
  l.name,
  l.price,
  l.room_type,
  n.name
ORDER BY
  avg_rating DESC NULLS LAST,
  l.price     ASC;
