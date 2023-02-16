from datetime import datetime
from flask import Flask, request, jsonify
import psycopg2
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)


SWAGGER_URL = '/api/docs'
API_URL = '/swagger.yml'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "My API"
    }
)

app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)


def connect_to_db():
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=Dishitha@6")
    # cur = conn.cursor()
    return conn


@app.route('/swagger.yml')
def swagger_yaml():
    return app.send_static_file('swagger.yml')

# Define an example endpoint


@app.route('/api/weather', methods=['POST'])
def weather_data():
    '''
    this function fetches the weather data for parameters location and date from table weather_data. 
    '''

    location = str(request.args.get('location'))
    date = str(request.args.get('date'))

    '''
    date data format check
    '''
    # print(request)
    # print(date, location)
    # print(type(date))

    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError:
        return jsonify({'message': "Specify date in YYYYMMDD format only", 'is_success': "False", 'data': []})

    if location == "" and location is None:
        return jsonify({'message': "Specify location name", 'is_success': "False", 'data': []})
    else:
        conn = connect_to_db()
        cur = conn.cursor()
        query = """select * from weather_data where location='{}' and time_date='{}'""".format(
            location, date)
        print(query)
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        result = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify({'message': "Data Successfully fetched", 'is_success': "True", 'data': result})

    return jsonify({'message': "date and location parameters are not passed", 'is_success': "False", 'data': []})


@app.route('/api/weather/stats', methods=['POST'])
def weather_stats_data():
    '''
    this function fetches the weather statistics data for parameters location and year from table weather_stats_data. 
    '''

    location = str(request.args.get('location'))
    year = str(request.args.get('year'))

    '''
    year data numerical check
    '''

    # print(year, location)
    # print(type(year))
    # print(jsonify(request))

    if len(year) != 4 or not year.isdigit():
       return jsonify({'message': "Specify proper year", 'is_success': "False", 'data': []})
    elif location == "" or location is None:
        return jsonify({'message': "Specify location name", 'is_success': "False", 'data': []})
    else:
        conn = connect_to_db()
        cur = conn.cursor()
        query = """select * from weather_data_stats where location='{}' and year='{}'""".format(
            location, year)
        print(query)
        cur.execute(query)
        columns = [i[0] for i in cur.description]
        result = [dict(zip(columns, row)) for row in cur.fetchall()]
        return jsonify({'message': "Data Successfully fetched", 'is_success': "True", 'data': result})

    return jsonify({'message': "year and location parameters are not passed", 'is_success': "False", 'data': []})


if __name__ == '__main__':
    app.run(debug=True)
