SELECT 
    EXTRACT(YEAR from time_date) AS year, 
    location, 
    AVG(maximum_temperature) AS avg_max_temp_celsius,
    AVG(minimum_temperature) AS avg_min_temp_celsius,
    SUM(precipitation/10) AS total_precipitation_cm
FROM 
    weather_data
GROUP BY 
    EXTRACT(YEAR from time_date), location;