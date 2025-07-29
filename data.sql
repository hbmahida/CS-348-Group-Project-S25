DROP TABLE IF EXISTS HostNotifications   CASCADE;
DROP TABLE IF EXISTS ListingAmenity CASCADE;
DROP TABLE IF EXISTS Availability       CASCADE;
DROP TABLE IF EXISTS Review             CASCADE;
DROP TABLE IF EXISTS Listing            CASCADE;
DROP TABLE IF EXISTS Neighbourhood       CASCADE;
DROP TABLE IF EXISTS Host               CASCADE;

CREATE EXTENSION IF NOT EXISTS PostGIS;

-- HOST (strong entity)
CREATE TABLE Host (
  host_id            INTEGER       PRIMARY KEY,
  host_name          VARCHAR(255),
  host_since         DATE,
  host_location      VARCHAR(255),
  host_about         TEXT,
  host_response_time VARCHAR(50),
  host_response_rate INTEGER      CHECK (host_response_rate >= 0 AND host_response_rate <= 100),
  host_acceptance_rate INTEGER    CHECK (host_acceptance_rate >= 0 AND host_acceptance_rate <= 100),
  is_superhost       BOOLEAN,
  host_listings_count INTEGER      CHECK (host_listings_count >= 0),
  referred_by        INTEGER       REFERENCES Host(host_id)
);

-- LISTING (strong entity)
CREATE TABLE Listing (
  listing_id        INTEGER      PRIMARY KEY,
  host_id           INTEGER      NOT NULL,
  name              VARCHAR(500) NOT NULL,
  description       TEXT,
  neighbourhood_overview TEXT,
  room_type         VARCHAR(100),
  accommodates      INTEGER      CHECK (accommodates > 0),
  bathrooms         DECIMAL(3,1) CHECK (bathrooms >= 0),
  bathrooms_text    VARCHAR(50),
  bedrooms          INTEGER      CHECK (bedrooms >= 0),
  beds              INTEGER      CHECK (beds >= 0),
  price             DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  minimum_nights    INTEGER      DEFAULT 1 CHECK (minimum_nights > 0),
  maximum_nights    INTEGER,
  instant_bookable  BOOLEAN,
  created_date      DATE         DEFAULT CURRENT_DATE,
  last_scraped      DATE,
  geopoint          geography(Point, 4326),
  -- 4326 indicates to PostGIS that the data should be treated as coordinates on WGS 84 which is the standard for specifying locations in terms of latitude and longitude. 

  FOREIGN KEY (host_id) REFERENCES Host(host_id) ON DELETE CASCADE
);

-- NEIGHBOURHOOD (weak entity)
CREATE TABLE Neighbourhood (
  neighbourhood_id  INTEGER      PRIMARY KEY,
  listing_id        INTEGER      NOT NULL,
  name              VARCHAR(255),
  neighbourhood_group VARCHAR(255),
  latitude          DECIMAL(10,8),
  longitude         DECIMAL(11,8),

  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);

-- LISTING_AMENITY (table for multi-valued attribute amenities)
CREATE TABLE ListingAmenity (
  listing_id INTEGER NOT NULL,
  amenity    VARCHAR(255) NOT NULL,

  PRIMARY KEY (listing_id, amenity),
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);

-- REVIEW (weak entity)
CREATE TABLE Review (
  review_id     SERIAL,
  listing_id    INTEGER      NOT NULL,
  review_date   DATE,
  rating        DECIMAL(3,2) NOT NULL CHECK (rating BETWEEN 1 AND 5),
  accuracy      DECIMAL(3,2) CHECK (accuracy BETWEEN 1 AND 10),
  location      DECIMAL(3,2) CHECK (location BETWEEN 1 AND 10),
  number_of_reviews INTEGER   CHECK (number_of_reviews >= 0),

  PRIMARY KEY(listing_id, review_id),
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);

-- AVAILABILITY (weak entity)
CREATE TABLE Availability (
  availability_id SERIAL,
  listing_id      INTEGER      NOT NULL,
  date            DATE         NOT NULL CHECK (date >= CURRENT_DATE),
  availability_30 INTEGER,
  availability_365 INTEGER,

  PRIMARY KEY(listing_id, availability_id),
  FOREIGN KEY (listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);

-- HOST NOTIFICATIONS (for trigger-based notification system)
CREATE TABLE HostNotifications (
  notification_id SERIAL PRIMARY KEY,
  host_id INTEGER NOT NULL,
  message TEXT NOT NULL,
  notification_type VARCHAR(50) NOT NULL,
  related_listing_id INTEGER,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_read BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (host_id) REFERENCES Host(host_id) ON DELETE CASCADE,
  FOREIGN KEY (related_listing_id) REFERENCES Listing(listing_id) ON DELETE CASCADE
);

-- ADDITIONAL CONSTRAINTS
ALTER TABLE Neighbourhood
ADD CONSTRAINT valid_latitude CHECK (latitude BETWEEN -90 AND 90),
ADD CONSTRAINT valid_longitude CHECK (longitude BETWEEN -180 AND 180);


-- Indexes for Basic Features
CREATE UNIQUE INDEX idx_neighbourhood_listing_id ON Neighbourhood(listing_id);
CREATE INDEX idx_review_listing_id ON Review(listing_id);
CREATE INDEX idx_listing_room_type ON Listing(room_type);
CREATE INDEX idx_listing_accommodates ON Listing(accommodates);
CREATE INDEX idx_host_superhost ON Host(is_superhost);
CREATE INDEX idx_host_listings_count ON Host(host_listings_count);

-- Indexes and Optimization for Advanced Features
CREATE INDEX idx_listing_geopoint ON Listing USING GIST (geopoint);
-- GiST spatial index is created on geopoint column instead of traditional B-tree since B-tree indexes cannot index spatial data but GiST indexes support PostGIS geography type and allows us to perform distance/spatial searches.

-- TRIGGER FUNCTION: Notify neighborhood hosts when new listing is added
CREATE OR REPLACE FUNCTION notify_neighborhood_hosts()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert notifications for other hosts in the same neighborhood
    INSERT INTO HostNotifications (host_id, message, notification_type, related_listing_id)
    SELECT DISTINCT h.host_id,
           'New listing "' || NEW.name || '" added in ' || n.name || ' at $' || NEW.price || '/night. Monitor your pricing!',
           'NEW_COMPETITION',
           NEW.listing_id
    FROM Host h
    JOIN Listing l ON h.host_id = l.host_id  
    JOIN Neighbourhood n_existing ON l.listing_id = n_existing.listing_id
    JOIN Neighbourhood n ON NEW.listing_id = n.listing_id
    WHERE n_existing.name = n.name
      AND h.host_id != NEW.host_id;
    
    -- Also create a confirmation notification for the listing owner
    INSERT INTO HostNotifications (host_id, message, notification_type, related_listing_id)
    VALUES (NEW.host_id, 
            'Your listing "' || NEW.name || '" has been successfully added to the system',
            'LISTING_ADDED',
            NEW.listing_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- CREATE TRIGGER: Automatically notify hosts when new listing is inserted
CREATE TRIGGER new_listing_notification
    AFTER INSERT ON Listing
    FOR EACH ROW
    EXECUTE FUNCTION notify_neighborhood_hosts();

-- Indexes for Advanced Feature 1: Trigger-Based Host Notification System
-- These indexes optimize the trigger function queries that join multiple tables

-- Index on Neighbourhood name for fast neighborhood lookups in trigger
CREATE INDEX idx_neighbourhood_name ON Neighbourhood(name);

-- Index on Listing host_id for fast host-based filtering in trigger
CREATE INDEX idx_listing_host_id ON Listing(host_id);

-- Index on HostNotifications for efficient notification queries
CREATE INDEX idx_hostnotifications_host_id ON HostNotifications(host_id);
CREATE INDEX idx_hostnotifications_created_at ON HostNotifications(created_at);
CREATE INDEX idx_hostnotifications_type ON HostNotifications(notification_type);

-- Indexes for Feature 2: Recursive Brokerage Firm Network Analysis
-- These indexes optimize the recursive CTE queries that traverse referral relationships

-- Index on Host referred_by for fast recursive traversal
CREATE INDEX idx_host_referred_by ON Host(referred_by);

-- Index on Host host_id for fast lookups in recursive queries
CREATE INDEX idx_host_host_id ON Host(host_id);

-- Composite index on Host for referral network queries
CREATE INDEX idx_host_referral_network ON Host(referred_by, host_id, host_name);

-- Index on Listing price for fast revenue calculations
CREATE INDEX idx_listing_price ON Listing(price);

-- Index on Listing host_id for fast host-listing joins
CREATE INDEX idx_listing_host_id_price ON Listing(host_id, price);