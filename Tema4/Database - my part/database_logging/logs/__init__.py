import logging
import azure.functions as func
import pyodbc
from datetime import datetime
import json


def initialize_database_connection():
    server = 'tema4-sql-server.database.windows.net'
    database = 'tema4-database'
    username = 'cristi'
    password = 'tema4-sql'
    driver = '{ODBC Driver 17 for SQL Server}'
    return pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database +
                          ';UID=' + username + ';PWD=' + password)


def create_logs_schema(db_connection):
    cursor = db_connection.cursor()
    sql_query_schema = """IF (NOT EXISTS (SELECT * FROM SYS.SCHEMAS WHERE NAME='Notes'))
                          BEGIN                            
                                exec('CREATE SCHEMA Notes')
                          END"""
    cursor.execute(sql_query_schema)


def create_logs_data_table(db_connection):
    cursor = db_connection.cursor()
    sql_query_table = """IF (NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='Notes' AND TABLE_NAME='Logs'))
                         BEGIN                            
                            CREATE TABLE [Notes].[Logs]
                               (
                                    log_id INT IDENTITY PRIMARY KEY,
                                    method NVARCHAR(10) NOT NULL,
                                    route NVARCHAR(2048) NOT NULL,
                                    status_code INT NOT NULL,
                                    response NVARCHAR(4000) NOT NULL,
                                    datetime DATETIME
                               )
                         END"""
    cursor.execute(sql_query_table)
    cursor.commit()


def validate_json(request_api):
    fields = ['method', 'route', 'response', 'status_code']
    if len(request_api.get_json()) != len(fields):
        return False
    try:
        for field in fields:
            data = request_api.get_json()[field]
        return True
    except Exception as e:
        return False


def create_log_in_database(db_connection, data_keys, data_values):
    cursor = db_connection.cursor()
    columns_insert = ", ".join(data_keys)
    values_insert = ", ".join(['?' for index in range(len(data_values))])
    sql_query_log = "INSERT INTO [Notes].[Logs] ({}) VALUES ({});".format(columns_insert, values_insert)
    cursor.execute(sql_query_log, data_values)
    cursor.commit()


def select_log_from_database(db_connection, log_method=None, log_route=None):
    cursor = db_connection.cursor()
    if log_method is not None and log_route is not None:
        sql_query_log = "SELECT * FROM [Notes].[Logs] WHERE method={} AND route={};".format("'" + log_method + "'",
                                                                                            "'" + log_route + "'")
    elif log_method is not None:
        sql_query_log = "SELECT * FROM [Notes].[Logs] WHERE method={};".format("'" + log_method + "'")
    elif log_route is not None:
        sql_query_log = "SELECT * FROM [Notes].[Logs] WHERE route={};".format("'" + log_route + "'")
    else:
        sql_query_log = "SELECT * FROM [Notes].[Logs];"
    cursor.execute(sql_query_log)
    return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a {} request.'.format(str(req.method)))
    db_connection = initialize_database_connection()
    create_logs_schema(db_connection)
    create_logs_data_table(db_connection)

    if str(req.method) == "POST":
        try:
            if validate_json(req):
                request_body = req.get_json()
                request_keys = list(request_body.keys())
                request_values = list(request_body.values())
                request_keys.append('datetime')
                request_values.append(datetime.now())
                create_log_in_database(db_connection, request_keys, request_values)
                return func.HttpResponse(f"Created with success", status_code=200)
            else:
                return func.HttpResponse(f"Wrong body of request", status_code=400)
        except Exception as e:
            return func.HttpResponse(f"An Error Occured: {e}", status_code=500)
    elif str(req.method) == "GET":
        log_method = req.params.get('method')
        log_route = req.params.get('route')
        try:
            response = select_log_from_database(db_connection, log_method, log_route)
            if len(response) != 0:
                return func.HttpResponse(json.dumps(response, indent=4, sort_keys=True, default=str),
                                         mimetype="application/json", status_code=200)
            else:
                if log_method or log_route:
                    return func.HttpResponse(f"There are no logs with that method and/or route!", status_code=200)
                else:
                    return func.HttpResponse(f"There are no logs!", status_code=200)
        except Exception as e:
            return func.HttpResponse(f"An Error Occured: {e}", status_code=500)
