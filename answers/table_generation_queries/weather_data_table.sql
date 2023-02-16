CREATE TABLE weather_data(
    id integer PRIMARY KEY,
    time_date date,
    maximum_temperature float,
    minimum_temperature float,
    precipitation float,
    location VARCHAR(100),
);