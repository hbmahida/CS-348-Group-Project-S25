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
WHERE
  (l.name ILIKE '%Downtown%'
   OR n.name ILIKE '%Downtown%')
GROUP BY
  l.listing_id,
  l.name,
  l.price,
  l.room_type,
  n.name
ORDER BY
  avg_rating DESC NULLS LAST,
  l.price     ASC
LIMIT 20
;