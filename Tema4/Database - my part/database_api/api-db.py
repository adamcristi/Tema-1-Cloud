import os
import pyodbc
from flask import Flask, request, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

url_logging_function = r"https://tema4-function-logs-database.azurewebsites.net/api/logs?code=5mnIzMhFmNjOqOr6VgtstJ8JSm0Zgyolyb2Ia9k7KK/CEyVAevMwSQ=="

def initialize_database_connection():
    server = 'tema4-sql-server.database.windows.net'
    database = 'tema4-database'
    username = 'cristi'
    password = 'tema4-sql'
    driver = '{ODBC Driver 17 for SQL Server}'
    return pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database +
                          ';UID=' + username + ';PWD=' + password)


def create_notes_schema():
    cursor = db_connection.cursor()
    sql_query_schema = """IF (NOT EXISTS (SELECT * FROM SYS.SCHEMAS WHERE NAME='Notes'))
                          BEGIN                            
                                exec('CREATE SCHEMA Notes')
                          END"""
    cursor.execute(sql_query_schema)
    cursor.close()


def create_notes_data_table():
    cursor = db_connection.cursor()
    sql_query_table = """IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='Notes' AND TABLE_NAME='Data'))
                         BEGIN                            
                            CREATE TABLE [Notes].[Data]
                               (
                                    note_id INT IDENTITY PRIMARY KEY,
                                    text NVARCHAR(2048) NOT NULL,
                                    text_language NVARCHAR(10) NOT NULL,
                                    translated NVARCHAR(2048) NOT NULL,
                                    translated_language NVARCHAR(10) NOT NULL,
                                    sentiment_magnitude DECIMAL(20,16),
                                    sentiment_score DECIMAL(20,16)
                               )
                         END"""
    cursor.execute(sql_query_table)
    cursor.commit()
    cursor.close()


def validate_json(request_api):
    fields = ['text', 'text_language', 'translated', 'translated_language', 'sentiment']
    if len(request_api.json) != len(fields):
        return False
    try:
        for field in fields:
            data = request_api.json[field]
        return True
    except Exception as e:
        return False


def create_note_in_database(data_keys, data_values):
    cursor = db_connection.cursor()
    columns_insert = ", ".join(data_keys)
    values_insert = ", ".join(['?' for index in range(len(data_values))])
    sql_query_note = "INSERT INTO [Notes].[Data] ({}) VALUES ({});".format(columns_insert, values_insert)
    cursor.execute(sql_query_note, data_values)
    cursor.commit()
    cursor.execute("SELECT IDENT_CURRENT('Notes.Data');")
    return int(cursor.fetchone()[0])


def select_note_from_database(note_id=None):
    cursor = db_connection.cursor()
    if note_id is not None:
        sql_query_note = "SELECT * FROM [Notes].[Data] WHERE note_id={};".format(note_id)
    else:
        sql_query_note = "SELECT * FROM [Notes].[Data];"
    cursor.execute(sql_query_note)
    return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]


def modify_note_data(note_data):
    note_data['sentiment'] = dict()
    if note_data.get('sentiment_magnitude') is not None:
        note_data['sentiment']['magnitude'] = float(note_data.get('sentiment_magnitude'))
    if note_data.get('sentiment_score') is not None:
        note_data['sentiment']['score'] = float(note_data.get('sentiment_score'))
    del note_data['sentiment_magnitude']
    del note_data['sentiment_score']
    return note_data


@app.route('/')
def running():
    return 'Container instance app is now running!'


@app.route('/notes/add', methods=['POST'])
def add_note():
    try:
        if validate_json(request):
            request_keys = []
            request_values = []
            for (key, value) in request.json.items():
                if key != 'sentiment':
                    request_keys.append(key)
                    request_values.append(value)
                else:
                    if request.json['sentiment'].get('magnitude') is not None:
                        request_keys.append('sentiment_magnitude')
                        request_values.append(request.json['sentiment'].get('magnitude'))
                    if request.json['sentiment'].get('score') is not None:
                        request_keys.append('sentiment_score')
                        request_values.append(request.json['sentiment'].get('score'))
            id_note_added = create_note_in_database(data_keys=request_keys, data_values=request_values)
            response = {"id": id_note_added}
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong body of request"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/notes/get/<string:note_id>', methods=['GET'])
def get_requested_note(note_id):
    try:
        requested_note = select_note_from_database(note_id)
        response = modify_note_data(requested_note[0])

        if response is not None:
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong note id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/notes/list', methods=['GET'])
def get_all_notes():
    try:
        all_notes = []
        requested_notes = select_note_from_database()
        for note in requested_notes:
            all_notes.append(modify_note_data(note))
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_notes), 'status_code': str(200)})
        return jsonify(all_notes), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


port = int(os.environ.get('PORT', 80)) #8080 pentru testare locala
if __name__ == '__main__':
    db_connection = initialize_database_connection()
    create_notes_schema()
    create_notes_data_table()
    app.run(threaded=True, host='0.0.0.0', port=port)
