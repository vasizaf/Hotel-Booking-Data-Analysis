CREATE DATABASE Hotel_booking_analysis;
USE Hotel_booking_analysis;

CREATE TABLE basic_statistics (
    hotel VARCHAR(50) PRIMARY KEY,
    mean_total_nights FLOAT,
    mean_weekend_nights FLOAT,
    mean_week_nights FLOAT,
    cancellation_rate FLOAT
);

CREATE TABLE monthly_distribution (
  cur_year INT,
  cur_month VARCHAR(20),
  total_bookings INT,
  PRIMARY KEY (cur_year, cur_month)
);

CREATE TABLE seasonal_distribution (
  cur_year INT,
  season VARCHAR(10),
  total_bookings INT,
  PRIMARY KEY (cur_year, season)
);

CREATE TABLE room_type_distribution (
    room_type VARCHAR(1) PRIMARY KEY,
    counter INT
);

CREATE TABLE customer_types (
    cust_type VARCHAR(50) PRIMARY KEY,
    counter INT
);

CREATE TABLE booking_trends (
    arrival_date_year INT,
    arrival_date_month VARCHAR(20),
    num_bookings INT,
    PRIMARY KEY (arrival_date_year, arrival_date_month)
);

CREATE TABLE seasonality (
    hotel VARCHAR(50),
    season VARCHAR(10),
    cancelled INT,
    not_cancelled INT,
    PRIMARY KEY (hotel, season)
);

SELECT * FROM room_type_distribution;