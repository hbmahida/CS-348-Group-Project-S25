UPDATE Listing
SET
  name   = 'George Brown Housing - Updated',
  price  = 120.00
WHERE listing_id = 124;

UPDATE Neighbourhood
SET
  neighbourhood_group = 'Brooklyn--North'
WHERE listing_id = 124;