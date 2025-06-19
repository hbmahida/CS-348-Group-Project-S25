DROP TABLE IF EXISTS ListingAmenity CASCADE;
DROP TABLE IF EXISTS Availability       CASCADE;
DROP TABLE IF EXISTS Review             CASCADE;
DROP TABLE IF EXISTS Listing            CASCADE;
DROP TABLE IF EXISTS Neighbourhood       CASCADE;
DROP TABLE IF EXISTS Host               CASCADE;

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
  host_listings_count INTEGER      CHECK (host_listings_count >= 0)
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

-- ADDITIONAL CONSTRAINTS
ALTER TABLE Neighbourhood
ADD CONSTRAINT valid_latitude CHECK (latitude BETWEEN -90 AND 90),
ADD CONSTRAINT valid_longitude CHECK (longitude BETWEEN -180 AND 180);