-- HOST table (5 unique hosts)
INSERT INTO Host (host_id, host_name, host_since, host_location, host_about, host_response_time, host_response_rate, host_acceptance_rate, is_superhost, host_listings_count) VALUES
(1, 'John Smith', '2020-01-15', 'New York, NY', 'Friendly host with 5 years of experience. Love meeting new people!', 'within an hour', 95, 88, TRUE, 3),
(2, 'Maria Garcia', '2019-06-20', 'Los Angeles, CA', 'Welcome to my cozy home! I enjoy cooking and sharing local tips.', 'within a few hours', 78, 92, FALSE, 2),
(3, 'David Chen', '2021-03-10', 'San Francisco, CA', 'Tech professional turned host. Clean, modern spaces available.', 'within an hour', 100, 95, TRUE, 1),
(4, 'Sarah Johnson', '2018-11-05', 'Miami, FL', 'Beach lover and yoga instructor. Peaceful retreats await you.', 'within a day', 65, 75, FALSE, 2),
(5, 'Michael Brown', '2022-08-18', 'Austin, TX', 'Music enthusiast with unique properties in the heart of Austin.', 'within a few hours', 89, 84, FALSE, 1);

-- LISTING table (9 unique listings)
INSERT INTO Listing (listing_id, host_id, name, description, neighbourhood_overview, room_type, accommodates, bathrooms, bathrooms_text, bedrooms, beds, price, minimum_nights, maximum_nights, instant_bookable, created_date, last_scraped) VALUES
(101, 1, 'Cozy Manhattan Studio', 'Modern studio apartment in the heart of NYC with amazing city views.', 'Vibrant neighbourhood with great restaurants and easy subway access.', 'Entire home/apt', 2, 1.0, '1 bath', 0, 1, 150.00, 2, 30, TRUE, '2020-02-01', '2025-06-10'),
(102, 1, 'Brooklyn Loft Experience', 'Spacious loft with exposed brick walls and industrial charm.', 'Hip Brooklyn neighbourhood with artisanal coffee shops and galleries.', 'Entire home/apt', 4, 2.0, '2 baths', 2, 2, 200.00, 3, 60, FALSE, '2020-03-15', '2025-06-09'),
(103, 1, 'Central Park View Room', 'Private room with stunning Central Park views.', 'Upper West Side with easy access to museums and parks.', 'Private room', 1, 0.5, 'Half-bath', 1, 1, 95.00, 1, 14, TRUE, '2020-05-20', '2025-06-08'),
(104, 2, 'Hollywood Hills Retreat', 'Luxury home with pool and panoramic city views.', 'Exclusive Hollywood Hills area with celebrity neighbors.', 'Entire home/apt', 6, 3.0, '3 full baths', 3, 4, 350.00, 7, 90, FALSE, '2019-07-01', '2025-06-07'),
(105, 2, 'Venice Beach Bungalow', 'Charming beach house just steps from the ocean.', 'Bohemian Venice with street art, boardwalk, and beach culture.', 'Entire home/apt', 3, 1.5, '1.5 baths', 2, 2, 180.00, 2, 45, TRUE, '2019-09-12', '2025-06-06'),
(106, 3, 'Tech Hub Apartment', 'Modern apartment in SOMA with high-speed internet and workspace.', 'Heart of San Francisco tech scene with startup culture.', 'Entire home/apt', 2, 1.0, '1 bathroom', 1, 1, 220.00, 1, 28, TRUE, '2021-04-05', '2025-06-05'),
(107, 4, 'South Beach Penthouse', 'Luxury penthouse with ocean views and rooftop access.', 'Art Deco district with nightlife, dining, and beach access.', 'Entire home/apt', 8, 4.0, '4 full bathrooms', 4, 6, 500.00, 5, 120, FALSE, '2018-12-10', '2025-06-04'),
(108, 4, 'Coral Gables Villa', 'Mediterranean-style villa with private garden and pool.', 'Upscale Coral Gables with historic architecture and fine dining.', 'Entire home/apt', 5, 2.5, '2.5 baths', 3, 3, 280.00, 3, 75, FALSE, '2019-01-20', '2025-06-03'),
(109, 5, 'Music District Loft', 'Industrial loft in the heart of Austins live music scene.', 'East Austin with live music venues, food trucks, and local culture.', 'Entire home/apt', 4, 2.0, '2 bathrooms', 2, 3, 165.00, 2, 21, TRUE, '2022-09-01', '2025-06-02'),
(110, 5, 'Goldrej Loft', 'Something somethihng', 'East Austin with live music venues, food trucks, and local culture.', 'Entire home/apt', 4, 2.0, '2 bathrooms', 2, 3, 240.00, 2, 21, TRUE, '2022-09-01', '2025-06-02');

-- NEIGHBOURHOOD table (9 records - one for each listing)
INSERT INTO Neighbourhood (neighbourhood_id, listing_id, name, neighbourhood_group, latitude, longitude) VALUES
(1, 101, 'Midtown Manhattan', 'Manhattan', 40.7589, -73.9851),
(2, 102, 'Williamsburg', 'Brooklyn', 40.7081, -73.9571),
(3, 103, 'Upper West Side', 'Manhattan', 40.7873, -73.9759),
(4, 104, 'Hollywood Hills', 'Hollywood', 34.1341, -118.3215),
(5, 105, 'Venice', 'West LA', 34.0195, -118.4912),
(6, 106, 'SOMA', 'San Francisco', 37.7749, -122.4094),
(7, 107, 'South Beach', 'Miami Beach', 25.7907, -80.1300),
(8, 108, 'Coral Gables', 'Miami-Dade', 25.7454, -80.2534),
(9, 109, 'East Austin', 'Austin', 30.2672, -97.7431),
(10, 110, 'East Austin', 'Austin', 30.2672, -97.7431);

-- LISTING_AMENITY table (covering various amenities across listings)
INSERT INTO ListingAmenity (listing_id, amenity) VALUES
-- Listing 101 amenities
(101, 'WiFi'),
(101, 'Air conditioning'),
(101, 'Kitchen'),
(101, 'Elevator'),
-- Listing 102 amenities
(102, 'WiFi'),
(102, 'Washer'),
(102, 'Dryer'),
(102, 'Balcony'),
(102, 'Workspace'),
-- Listing 103 amenities
(103, 'WiFi'),
(103, 'Central heating'),
(103, 'Shared kitchen'),
-- Listing 104 amenities
(104, 'WiFi'),
(104, 'Pool'),
(104, 'Hot tub'),
(104, 'Parking'),
(104, 'Mountain view'),
-- Listing 105 amenities
(105, 'WiFi'),
(105, 'Beach access'),
(105, 'Bike'),
(105, 'BBQ grill'),
-- Listing 106 amenities
(106, 'WiFi'),
(106, 'Workspace'),
(106, 'Gym'),
(106, 'Concierge'),
-- Listing 107 amenities
(107, 'WiFi'),
(107, 'Pool'),
(107, 'Ocean view'),
(107, 'Doorman'),
(107, 'Valet parking'),
-- Listing 108 amenities
(108, 'WiFi'),
(108, 'Pool'),
(108, 'Garden'),
(108, 'Parking'),
(108, 'Pet friendly'),
-- Listing 109 amenities
(109, 'WiFi'),
(109, 'Sound system'),
(109, 'Workspace'),
(109, 'Parking');

-- REVIEW table (15 unique reviews across different listings)
INSERT INTO Review (listing_id, review_date, rating, accuracy, location, number_of_reviews) VALUES
(101, '2025-05-15', 4.8, 9.2, 9.8, 45),
(101, '2025-04-20', 4.5, 8.8, 9.5, 46),
(102, '2025-05-10', 4.9, 9.5, 8.7, 23),
(103, '2025-06-01', 4.2, 8.5, 9.9, 67),
(103, '2025-05-25', 4.6, 9.0, 9.7, 68),
(104, '2025-04-15', 5.0, 9.8, 8.9, 12),
(105, '2025-05-30', 4.7, 9.1, 9.4, 34),
(105, '2025-05-05', 4.4, 8.7, 9.2, 35),
(106, '2025-06-05', 4.9, 9.6, 8.8, 18),
(107, '2025-04-28', 4.8, 9.3, 9.6, 8),
(107, '2025-03-20', 5.0, 9.9, 9.8, 9),
(108, '2025-05-18', 4.6, 9.0, 9.1, 21),
(109, '2025-06-08', 4.3, 8.6, 8.5, 29),
(109, '2025-05-12', 4.7, 9.2, 8.8, 30),
(109, '2025-04-30', 4.5, 8.9, 8.7, 31);

-- AVAILABILITY table (15 records showing different availability patterns)
INSERT INTO Availability (listing_id, date, availability_30, availability_365) VALUES
(101, '2025-06-29', 25, 300),
(101, '2025-07-01', 20, 280),
(102, '2025-06-20', 30, 365),
(103, '2025-06-19', 15, 200),
(103, '2025-08-01', 28, 320),
(104, '2025-06-25', 10, 150),
(105, '2025-06-21', 22, 250),
(105, '2025-07-15', 18, 240),
(106, '2025-07-14', 29, 350),
(107, '2025-07-30', 5, 120),
(107, '2025-07-20', 8, 100),
(108, '2025-10-16', 27, 290),
(109, '2025-10-22', 21, 260),
(109, '2025-07-10', 19, 230),
(109, '2025-08-05', 24, 275);