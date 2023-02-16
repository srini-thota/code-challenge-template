CREATE TABLE weather_data_stats(
    id integer PRIMARY KEY,
    year int,
    location VARCHAR(100),
    avg_max_temp_celsius VARCHAR(50),
    avg_min_temp_celsius VARCHAR(50),
    total_precipitation_cm VARCHAR(50)
);
