#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import os
import psycopg2
import logging
import time

start = time.time()


logging.basicConfig(filename='logs/data_ingestion_pipeline.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO, datefmt='%d-%b-%y %H:%M:%S')


dir_path = "../wx_data/"


logging.info("Connecting to the postgres database")

conn = psycopg2.connect(
    "host=localhost dbname=postgres user=postgres password=Dishitha@6")

logging.info("Connecting to the postgres database completed successfully")


# Make the list of the files
files_list = []

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        files_list.append(dir_path + path)

# print(len(files_list))
# print(files_list)


# testing if the file can be read.
# df = pd.read_csv(files_list[0], sep="\t", header=None)


logging.info("Reading the files in the location {}".format(dir_path))

start_t = time.time()

df_list = []
entries_sum = 0
for file in files_list:
    # print(file)
    logging.info(
        "Reading the file {} in the location {}".format(file, dir_path))
    df = pd.read_csv(file, sep="\t", header=None)
    df.columns = ["Date", "Max-Temp", "Min-Temp", "Precipitation"]
    # print(file.split("/")[1].split(".txt")[0])
    '''
    capturing the location in the data frame
    '''

    file = os.path.basename(file)
    df["Location-ID"] = file.split(".txt")[0]
    entries_sum += len(df)
    df_list.append(df)

logging.info(
    "Completed Reading all the files in the location {}".format(dir_path))
logging.info("Total time elapsed for reading all the files is {}".format(
    time.time()-start_t))

df_final = pd.concat(df_list)


# print(entries_sum)
# print(len(df_final))
# print(df_final["Location-ID"].nunique())

logging.info("Total entries are {}".format(entries_sum))


'''
writing function to connect to db
'''


def connect_to_db():
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=Dishitha@6")
    # cur = conn.cursor()
    return conn


'''
writing function to truncate table
'''


def truncate_table(table_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""TRUNCATE table {};""".format(table_name))
    conn.commit()
    conn.close()


'''
writing function to drop table
'''


def drop_table(table_name):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""DROP table {};""".format(table_name))
    conn.commit()
    conn.close()


# top level flow
# create a table with proper schema
# define the types of all the columns
# ingest the data into the data base
# build the queries asked in the problem statement.


conn = connect_to_db()
cur = conn.cursor()


'''
Dropping table weather_data if exists 

cur.execute("""DROP table weather_data""")
conn.commit()
'''

logging.info("Dropping table weather_data from database")

drop_table("weather_data")

logging.info("Completed Dropping table weather_data from database")
'''
create a weather table with 

id, date, maximum_temp, minimum_temp, precipitation and location fields

'''

logging.info("Creating table weather_data in database")

cur.execute("""
    CREATE TABLE weather_data(
    id integer PRIMARY KEY,
    time_date date,
    maximum_temperature float,
    minimum_temperature float,
    precipitation float,
    location VARCHAR(100)
)
""")

conn.commit()

logging.info("Completed Creating table weather_data in database")


def do_null_check(val):
    if val == -9999:
        return "NULL"
    return float(val)


start_t = time.time()

primary_index = 1

logging.info(
    "Started Ingesting data from populated data_frame to weather_data table")

for row in df_final.iterrows():

    # print(row[1].to_dict())
    max_temp = do_null_check(row[1].to_dict()["Max-Temp"])
    min_temp = do_null_check(row[1].to_dict()["Min-Temp"])
    date = row[1].to_dict()["Date"]
    prec = do_null_check(row[1].to_dict()["Precipitation"])
    location = row[1].to_dict()["Location-ID"]
    insert_query = "INSERT INTO weather_data VALUES ({}, to_date('{}', 'yyyymmdd'), {}, {}, {}, '{}');".format(
        primary_index, date, max_temp, min_temp, prec, location)
    cur.execute(insert_query)
    primary_index += 1
    if primary_index % 100000 == 0:
        logging.info(
            "Added {} records into the weather_data table".format(primary_index))


conn.commit()

logging.info(
    "Completed Ingesting data from populated data_frame to weather_data table")
logging.info("Total {} weather records were ingested into weather_data table".format(
    primary_index-1))
logging.info("Total time elapsed for ingesting all the data is {}".format(
    time.time() - start_t))

'''
aggregation query

execute the query and get the data and commit the changes.
'''

logging.info("Executing aggregation query in the database")


query_agg = """SELECT 
    EXTRACT(YEAR from time_date) AS year, 
    location, 
    AVG(maximum_temperature) AS avg_max_temp_celsius,
    AVG(minimum_temperature) AS avg_min_temp_celsius,
    SUM(precipitation/10) AS total_precipitation_cm
FROM 
    weather_data
GROUP BY 
    EXTRACT(YEAR from time_date), location;
"""


cur.execute(query_agg)

stats_data = cur.fetchall()

conn.commit()

logging.info("Completed Executing aggregation query in the database")

logging.info("Dropping weather_data_stats from database")

cur.execute("""DROP TABLE weather_data_stats;""")

logging.info("Completed Dropping weather_data_stats from database")

'''
create a weather stats table with 

id, year, location, avg_max_temp_celsius, avg_min_temp_celsius and total_precipitation_cm fields

'''

logging.info("Creating weather_data_stats table in database")

# create the table and commit the changes.

cur.execute("""
    CREATE TABLE weather_data_stats(
    id integer PRIMARY KEY,
    year int,
    location VARCHAR(100),
    avg_max_temp_celsius VARCHAR(50),
    avg_min_temp_celsius VARCHAR(50),
    total_precipitation_cm VARCHAR(50)
)
""")

conn.commit()

logging.info("Completed creating weather_data_stats table in database")

logging.info("Started Ingesting data to weather_data_stats table")
# ingest the data into the created data base table and commit the changes
start_t = time.time()

primary_index = 1
for data in stats_data:
    # print(data)
    insert_query = "INSERT INTO weather_data_stats VALUES ({}, {}, '{}', '{}', '{}', '{}');".format(
        primary_index, int(data[0]), data[1], data[2], data[3], data[4])
    # print(insert_query)
    cur.execute(insert_query)
    primary_index += 1

logging.info("Completed Ingesting data to weather_data_stats table")
logging.info("Total {} weather records were ingested into weather_data_stats table".format(
    primary_index-1))
logging.info("Total time elapsed for ingesting all the data is {}".format(
    time.time()-start_t))


conn.commit()

# close the connection

conn.close()
logging.info("Process flow complete")
logging.info(
    "Total time elapsed for the entire process is {}".format(time.time()-start))
