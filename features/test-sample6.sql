SELECT listing_id, name, price, avg_rating, neighbourhood
FROM (
  SELECT
    l.listing_id,
    l.name,
    l.price,
    n.name AS neighbourhood,
    COALESCE(AVG(r.rating), 0) AS avg_rating,
    RANK() OVER (
      PARTITION BY n.name
      ORDER BY AVG(r.rating) DESC, l.price ASC
    ) AS rank
  FROM Listing l
  JOIN Neighbourhood n ON n.listing_id = l.listing_id
  LEFT JOIN Review r ON r.listing_id = l.listing_id
  WHERE n.name = 'Downtown Toronto'
  GROUP BY l.listing_id, l.name, l.price, n.name
) ranked
WHERE rank <= 3
ORDER BY avg_rating DESC, price ASC;