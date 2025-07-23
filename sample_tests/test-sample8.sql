-- Advanced Feature: Trigger-based Host Notification System
-- Test the trigger by adding a new listing and checking notifications

-- First, let's see current notifications (should be empty initially)
SELECT COUNT(*) as current_notification_count FROM HostNotifications;

-- Insert a test listing to trigger notifications
INSERT INTO Listing (
    listing_id, host_id, name, description, room_type, 
    accommodates, price, minimum_nights, instant_bookable
) VALUES (
    999998, 1, 'Test Trigger Listing', 'Testing the notification trigger', 
    'Entire home/apt', 2, 125.00, 1, true
);

-- Insert corresponding neighborhood data
INSERT INTO Neighbourhood (
    neighbourhood_id, listing_id, name, neighbourhood_group, 
    latitude, longitude
) VALUES (
    999998, 999998, 'Downtown', 'Central Toronto', 43.6532, -79.3832
);

-- Query to show the notifications that were automatically created by the trigger
SELECT 
    hn.notification_id,
    h.host_name,
    hn.notification_type,
    hn.message,
    l.name as related_listing_name,
    l.price as related_listing_price,
    n.name as neighbourhood,
    hn.created_at,
    CASE 
        WHEN hn.is_read = true THEN 'Read'
        ELSE 'Unread'
    END as status
FROM HostNotifications hn
JOIN Host h ON hn.host_id = h.host_id
LEFT JOIN Listing l ON hn.related_listing_id = l.listing_id
LEFT JOIN Neighbourhood n ON l.listing_id = n.listing_id
WHERE hn.related_listing_id = 999998
ORDER BY hn.created_at DESC;

-- Clean up test data
DELETE FROM Neighbourhood WHERE listing_id = 999998;
DELETE FROM Listing WHERE listing_id = 999998;
DELETE FROM HostNotifications WHERE related_listing_id = 999998;
 