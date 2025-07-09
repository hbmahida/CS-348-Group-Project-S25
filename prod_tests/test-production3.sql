INSERT INTO Listing (
  listing_id,
  host_id,
  name,
  description,
  neighbourhood_overview,
  room_type,
  accommodates,
  bathrooms,
  bathrooms_text,
  bedrooms,
  beds,
  price,
  minimum_nights,
  maximum_nights,
  instant_bookable,
  created_date,
  last_scraped
)
VALUES (
  124,1565,'George Brown Housing','Brief Description of the property','Good neighbourhood','Private Room',2,2,'2 bath',3,3,240,3,5,True,(DATE '2025-07-08'),(DATE '2025-07-08')  
);

INSERT INTO Neighbourhood (
  neighbourhood_id,
  listing_id,
  name,
  neighbourhood_group,
  latitude,
  longitude
)
VALUES (
  (SELECT COALESCE(MAX(neighbourhood_id), 0) + 1 FROM Neighbourhood),124,'Church Hills','Toronto',43.6532,79.3832
);