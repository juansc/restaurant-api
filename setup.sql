CREATE DATABASE IF NOT EXISTS restaurant CHARACTER SET UTF8;
CREATE USER IF NOT EXISTS restaurant@'%' IDENTIFIED BY 'restaurant';
GRANT ALL PRIVILEGES ON restaurant.* to restaurant@'%';
GRANT ALL PRIVILEGES ON test_restaurant.* TO restaurant@'%';
FLUSH PRIVILEGES;
