import http.server
from http.server import HTTPServer
import sqlite3
import json
import re

PORT = 8080


def create_connection(db_filename):
    conn = None
    try:
        conn = sqlite3.connect(db_filename)
        conn.row_factory = sqlite3.Row
    except sqlite3.Error as err:
        print("Error while connecting to sqlite database: ".format(err))

    return conn


def create_tables(conn):
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        description text,
                                        begin_date text,
                                        end_date text
                                    ); """
    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL,
                                    description text,
                                    priority integer,
                                    status text,
                                    begin_date text,
                                    end_date text,
                                    project_id integer NOT NULL,
                                    FOREIGN KEY (project_id) REFERENCES projects (id)
                                 ); """

    try:
        cursor = conn.cursor()
        cursor.execute(sql_create_projects_table)
        cursor.execute(sql_create_tasks_table)
        cursor.close()
    except sqlite3.Error as err:
        print("Error while creating the tables: ".format(err))


def execute_read_query(sql_query):
    record = None
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql_query)
        record = [dict(row) for row in cursor.fetchall()]
        cursor.close()
    except sqlite3.Error as err:
        print("Error while executing query: ".format(err))

    return record


def execute_create_query(sql_query, sql_data):
    row_id = None
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql_query, sql_data)
        row_id = cursor.lastrowid
        cursor.close()
        db_connection.commit()
    except sqlite3.Error as err:
        print("Error while executing query: ".format(err))
        row_id = -1

    return row_id


def execute_update_query(sql_query, sql_data):
    try:
        cursor = db_connection.cursor()
        cursor.execute(sql_query, sql_data)
        cursor.close()
        db_connection.commit()
    except sqlite3.Error as err:
        print("Error while executing query: ".format(err))
        return False

    return True


def execute_delete_query(sql_query, sql_data=None):
    try:
        cursor = db_connection.cursor()
        if sql_data is not None:
            cursor.execute(sql_query, sql_data)
        else:
            cursor.execute(sql_query)
        cursor.close()
        db_connection.commit()
    except sqlite3.Error as err:
        print("Error while executing query: ".format(err))
        return False

    return True


class Handler(http.server.SimpleHTTPRequestHandler):
    def send_data(self, status_code, data_response, location_header=None):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        if location_header is not None:
            self.send_header("Location", location_header)
        self.end_headers()
        self.wfile.write(json.dumps(data_response).encode())

    def verify_project_body(self, body_data):
        projects_table_columns = ['name', 'description', 'begin_date', 'end_date']
        for key in body_data.keys():
            if key not in projects_table_columns:
                return False
            elif list(body_data.keys()).count(key) > 1:
                return False
        return True

    def verify_task_body(self, body_data):
        tasks_table_columns = ['name', 'description', 'priority', 'status', 'begin_date', 'end_date', 'project_id']
        for key in body_data.keys():
            if key not in tasks_table_columns:
                return False
            elif list(body_data.keys()).count(key) > 1:
                return False
        return True

    # GET
    def do_GET(self):
        print(self.path)
        if self.path == '/':
            response = {"Error": "No route is present!"}
            self.send_data(status_code=400, data_response=response)

        # /projects
        elif re.fullmatch(r"/projects", self.path):
            read_query = """ SELECT * FROM projects; """
            data_read_query = execute_read_query(sql_query=read_query)

            if data_read_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_read_query) == 0:
                response = {"Error": "Projects not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                self.send_data(status_code=200, data_response=data_read_query)

        # /projects/{project_id}
        elif re.fullmatch(r"/projects/(\d+)", self.path):
            id_project = int(re.search("(\d+)", self.path).group(1))
            read_query = """ SELECT * FROM projects
                        WHERE id = {}; """.format(id_project)
            data_read_query = execute_read_query(sql_query=read_query)

            if data_read_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_read_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                self.send_data(status_code=200, data_response=data_read_query[0])

        # /projects/{project_id}/tasks
        elif re.fullmatch(r"/projects/(\d+)/tasks", self.path):
            id_project = int(re.search(r"(\d+)", self.path).group(1))

            verification_query = """ SELECT * FROM projects
                                     WHERE id = {}; """.format(id_project)
            data_verification_query = execute_read_query(verification_query)
            if data_verification_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_verification_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                read_query = """ SELECT * FROM tasks
                                 WHERE project_id = {}; """.format(id_project)
                data_read_query = execute_read_query(sql_query=read_query)

                if data_read_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_read_query) == 0:
                    response = {"Error": "Tasks not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    self.send_data(status_code=200, data_response=data_read_query)

        # /projects/{project_id}/tasks/{task_id}
        elif re.fullmatch(r"/projects/(\d+)/tasks/(\d+)", self.path):
            searched_values = re.search(r"(\d+)/tasks/(\d+)", self.path)
            id_project = int(searched_values.group(1))
            id_task = int(searched_values.group(2))

            verification_query = """ SELECT * FROM projects
                                        WHERE id = {}; """.format(id_project)
            data_verification_query = execute_read_query(verification_query)
            if data_verification_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_verification_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                read_query = """ SELECT * FROM tasks
                                 WHERE project_id = {} AND id = {}; """.format(id_project, id_task)
                data_read_query = execute_read_query(sql_query=read_query)

                if data_read_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_read_query) == 0:
                    response = {"Error": "Task with that id related to that project not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    self.send_data(status_code=200, data_response=data_read_query[0])

        else:
            response = {"Error": "Server could not answer to the given route!"}
            self.send_data(status_code=400, data_response=response)

    # POST
    def do_POST(self):
        print(self.path)
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data_body = json.loads(body.decode())

        if self.path == '/':
            response = {"Error": "No route is present!"}
            self.send_data(status_code=400, data_response=response)

        # /projects
        elif re.fullmatch(r"/projects", self.path):
            if 'name' not in data_body.keys() or not self.verify_project_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                verification_query = """ SELECT * FROM projects
                                         WHERE name = {}; """.format("'" + data_body.get('name') + "'")
                data_verification_query = execute_read_query(verification_query)
                if data_verification_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_query) != 0:
                    response = {"Error": "A project with that name already exists!"}
                    self.send_data(status_code=403, data_response=response)
                else:
                    insert_query = ''' INSERT INTO projects({}) 
                                        VALUES({}) '''.format(','.join([key for key in data_body.keys()]),
                                                              ','.join(["?" for key in data_body]))
                    data_insert_query = tuple(value for value in data_body.values())
                    # print(insert_query)
                    # print(data_insert_query)

                    id_project_added = execute_create_query(sql_query=insert_query, sql_data=data_insert_query)
                    # print(id_project_added)

                    if id_project_added == -1:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        retrieve_query = """ SELECT * FROM projects
                                             WHERE id = {}; """.format(id_project_added)
                        data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                        if data_retrieve_query is None:
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            self.send_data(status_code=201, data_response=data_retrieve_query[0],
                                           location_header=r"http://localhost:8080/projects/{}".format(
                                               str(id_project_added)))

        # /projects/{project_id}/tasks
        elif re.fullmatch(r"/projects/(\d+)/tasks", self.path):
            if 'name' not in data_body.keys() or not self.verify_task_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                id_project = int(re.search(r"(\d+)", self.path).group(1))
                verification_project_query = """ SELECT * FROM projects
                                                 WHERE id = {}; """.format(id_project)
                data_verification_project_query = execute_read_query(verification_project_query)
                if data_verification_project_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_project_query) == 0:
                    response = {"Error": "Project with that id not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    verification_task_query = """ SELECT * FROM tasks
                                                  WHERE name = {}; """.format("'" + data_body.get('name') + "'")
                    data_verification_task_query = execute_read_query(verification_task_query)
                    if data_verification_task_query is None:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    elif len(data_verification_task_query) != 0:
                        response = {"Error": "A task with that name already exists!"}
                        self.send_data(status_code=403, data_response=response)
                    else:
                        data_body['project_id'] = id_project
                        insert_query = ''' INSERT INTO tasks({}) 
                                           VALUES({}) '''.format(','.join([key for key in data_body.keys()]),
                                                                 ','.join(["?" for key in data_body]))
                        data_insert_query = tuple(value for value in data_body.values())
                        # print(insert_query)
                        # print(data_insert_query)

                        id_task_added = execute_create_query(sql_query=insert_query, sql_data=data_insert_query)
                        # print(id_task_added)

                        if id_task_added == -1:
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            retrieve_query = """ SELECT * FROM tasks
                                                 WHERE id = {}; """.format(id_task_added)
                            data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                            if data_retrieve_query is None:
                                response = {"Error": "Server error when trying to process the query!"}
                                self.send_data(status_code=500, data_response=response)
                            else:
                                self.send_data(status_code=201, data_response=data_retrieve_query[0],
                                               location_header=r"http://localhost:8080/projects/{}/tasks/{}".format(
                                                   str(id_project), str(id_task_added)))

        else:
            response = {"Error": "Server could not answer to the given route!"}
            self.send_data(status_code=400, data_response=response)

    # PUT
    def do_PUT(self):
        print(self.path)
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data_body = json.loads(body.decode())

        if self.path == '/':
            response = {"Error": "No route is present!"}
            self.send_data(status_code=400, data_response=response)

        # /projects/{project_id}
        elif re.fullmatch(r"/projects/(\d+)", self.path):
            if len(data_body) != 4 or not self.verify_project_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                id_project = int(re.search(r"(\d+)", self.path).group(1))
                verification_query = """ SELECT * FROM projects
                                         WHERE id = {}; """.format(id_project)
                data_verification_query = execute_read_query(verification_query)
                if data_verification_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_query) == 0:
                    response = {"Error": "Project with that id not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    update_query = '''UPDATE projects
                                        SET {}
                                        WHERE id = ?'''.format(',\n'.join([key + " = ? " for key in data_body.keys()]))
                    data_body['id'] = id_project
                    data_update_query = tuple(value for value in data_body.values())
                    # print(update_query)
                    # print(data_update_query)

                    if not execute_update_query(sql_query=update_query, sql_data=data_update_query):
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        retrieve_query = """ SELECT * FROM projects
                                             WHERE id = {}; """.format(id_project)
                        data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                        if data_retrieve_query is None:
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            self.send_data(status_code=200, data_response=data_retrieve_query[0],
                                           location_header=r"http://localhost:8080/projects/{}".format(
                                               str(id_project)))

        # /projects/{project_id}/tasks/{task_id}
        elif re.fullmatch(r"/projects/(\d+)/tasks/(\d+)", self.path):
            if len(data_body) != 7 or not self.verify_task_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                searched_values = re.search(r"(\d+)/tasks/(\d+)", self.path)
                id_project = int(searched_values.group(1))
                id_task = int(searched_values.group(2))
                verification_project_query = """ SELECT * FROM projects
                                                    WHERE id = {}; """.format(id_project)
                data_verification_project_query = execute_read_query(verification_project_query)
                if data_verification_project_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_project_query) == 0:
                    response = {"Error": "Project with that id not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    verification_task_query = """ SELECT * FROM tasks
                                                    WHERE id = {} AND project_id = {}; """.format(id_task, id_project)
                    data_verification_task_query = execute_read_query(verification_task_query)
                    if data_verification_task_query is None:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    elif len(data_verification_task_query) == 0:
                        response = {"Error": "Task with that id related to that project not found!"}
                        self.send_data(status_code=404, data_response=response)
                    else:
                        update_query = '''UPDATE tasks
                                        SET {}
                                        WHERE id = ?'''.format(',\n'.join([key + " = ? " for key in data_body.keys()]))
                        data_body['id'] = id_task
                        data_update_query = tuple(value for value in data_body.values())
                        # print(update_query)
                        # print(data_update_query)

                        if not execute_update_query(sql_query=update_query, sql_data=data_update_query):
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            retrieve_query = """ SELECT * FROM tasks
                                                        WHERE id = {}; """.format(id_task)
                            data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                            if data_retrieve_query is None:
                                response = {"Error": "Server error when trying to process the query!"}
                                self.send_data(status_code=500, data_response=response)
                            else:
                                self.send_data(status_code=200, data_response=data_retrieve_query[0],
                                               location_header=r"http://localhost:8080/projects/{}/tasks/{}".format(
                                                   str(id_project), str(id_task)))

        else:
            response = {"Error": "Server could not answer to the given route!"}
            self.send_data(status_code=400, data_response=response)

    # PATCH
    def do_PATCH(self):
        print(self.path)
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data_body = json.loads(body.decode())

        if self.path == '/':
            response = {"Error": "No route is present!"}
            self.send_data(status_code=400, data_response=response)

        # /projects/{project_id}
        elif re.fullmatch(r"/projects/(\d+)", self.path):
            if not self.verify_project_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                id_project = int(re.search(r"(\d+)", self.path).group(1))
                verification_query = """ SELECT * FROM projects
                                            WHERE id = {}; """.format(id_project)
                data_verification_query = execute_read_query(verification_query)
                if data_verification_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_query) == 0:
                    response = {"Error": "Project with that id not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    update_query = '''UPDATE projects
                                        SET {}
                                        WHERE id = ?'''.format(',\n'.join([key + " = ? " for key in data_body.keys()]))
                    data_body['id'] = id_project
                    data_update_query = tuple(value for value in data_body.values())
                    # print(update_query)
                    # print(data_update_query)

                    if not execute_update_query(sql_query=update_query, sql_data=data_update_query):
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        retrieve_query = """ SELECT * FROM projects
                                                WHERE id = {}; """.format(id_project)
                        data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                        if data_retrieve_query is None:
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            self.send_data(status_code=200, data_response=data_retrieve_query[0],
                                           location_header=r"http://localhost:8080/projects/{}".format(
                                               str(id_project)))

        # /projects/{project_id}/tasks/{task_id}
        elif re.fullmatch(r"/projects/(\d+)/tasks/(\d+)", self.path):
            if not self.verify_task_body(data_body):
                response = {"Error": "Server received incomplete or wrong body!"}
                self.send_data(status_code=400, data_response=response)
            else:
                searched_values = re.search(r"(\d+)/tasks/(\d+)", self.path)
                id_project = int(searched_values.group(1))
                id_task = int(searched_values.group(2))
                verification_project_query = """ SELECT * FROM projects
                                                    WHERE id = {}; """.format(id_project)
                data_verification_project_query = execute_read_query(verification_project_query)
                if data_verification_project_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_project_query) == 0:
                    response = {"Error": "Project with that id not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    verification_task_query = """ SELECT * FROM tasks
                                                    WHERE id = {} AND project_id = {}; """.format(id_task, id_project)
                    data_verification_task_query = execute_read_query(verification_task_query)
                    if data_verification_task_query is None:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    elif len(data_verification_task_query) == 0:
                        response = {"Error": "Task with that id related to that project not found!"}
                        self.send_data(status_code=404, data_response=response)
                    else:
                        update_query = '''UPDATE tasks
                                        SET {}
                                        WHERE id = ?'''.format(',\n'.join([key + " = ? " for key in data_body.keys()]))
                        data_body['id'] = id_task
                        data_update_query = tuple(value for value in data_body.values())
                        # print(update_query)
                        # print(data_update_query)

                        if not execute_update_query(sql_query=update_query, sql_data=data_update_query):
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            retrieve_query = """ SELECT * FROM tasks
                                                    WHERE id = {}; """.format(id_task)
                            data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                            if data_retrieve_query is None:
                                response = {"Error": "Server error when trying to process the query!"}
                                self.send_data(status_code=500, data_response=response)
                            else:
                                self.send_data(status_code=200, data_response=data_retrieve_query[0],
                                               location_header=r"http://localhost:8080/projects/{}/tasks/{}".format(
                                                   str(id_project), str(id_task)))

        else:
            response = {"Error": "Server could not answer to the given route!"}
            self.send_data(status_code=400, data_response=response)

    # DELETE
    def do_DELETE(self):
        print(self.path)
        if self.path == '/':
            response = {"Error": "No route is present!"}
            self.send_data(status_code=400, data_response=response)

        # /projects
        elif re.fullmatch(r"/projects", self.path):
            delete_query = """ DELETE FROM projects; """
            delete_tasks_query = '''DELETE FROM tasks; '''
            if not execute_delete_query(sql_query=delete_query) or not execute_delete_query(
                    sql_query=delete_tasks_query):
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            else:
                retrieve_query = """ SELECT * FROM projects"""
                data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                if data_retrieve_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                else:
                    self.send_data(status_code=200, data_response=data_retrieve_query)

        # /projects/{project_id}
        elif re.fullmatch(r"/projects/(\d+)", self.path):
            id_project = int(re.search("(\d+)", self.path).group(1))
            verification_query = """ SELECT * FROM projects
                                     WHERE id = {}; """.format(id_project)
            data_verification_query = execute_read_query(sql_query=verification_query)
            if data_verification_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_verification_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                delete_query = '''DELETE FROM projects WHERE id = ?'''
                delete_tasks_query = '''DELETE FROM tasks WHERE project_id = ?'''
                data_delete_query = tuple([id_project])
                # print(delete_query)
                # print(data_delete_query)

                if not execute_update_query(sql_query=delete_query, sql_data=data_delete_query) or \
                        not execute_delete_query(sql_query=delete_tasks_query, sql_data=data_delete_query):
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                else:
                    retrieve_query = """ SELECT * FROM projects """
                    data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                    if data_retrieve_query is None:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        self.send_data(status_code=200, data_response=data_retrieve_query)


        # /projects/{project_id}/tasks
        elif re.fullmatch(r"/projects/(\d+)/tasks", self.path):
            id_project = int(re.search(r"(\d+)", self.path).group(1))
            verification_query = """ SELECT * FROM projects
                                     WHERE id = {}; """.format(id_project)
            data_verification_query = execute_read_query(sql_query=verification_query)
            if data_verification_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_verification_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                delete_query = """ DELETE FROM tasks WHERE project_id = ?; """
                data_delete_query = tuple([id_project])
                # print(delete_query)
                # print(data_delete_query)

                if not execute_delete_query(sql_query=delete_query, sql_data=data_delete_query):
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                else:
                    retrieve_query = """ SELECT * FROM tasks
                                         WHERE project_id={}""".format(id_project)
                    data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                    if data_retrieve_query is None:
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        self.send_data(status_code=200, data_response=data_retrieve_query)

        # /projects/{project_id}/tasks/{task_id}
        elif re.fullmatch(r"/projects/(\d+)/tasks/(\d+)", self.path):
            searched_values = re.search(r"(\d+)/tasks/(\d+)", self.path)
            id_project = int(searched_values.group(1))
            id_task = int(searched_values.group(2))
            verification_project_query = """ SELECT * FROM projects
                                                WHERE id = {}; """.format(id_project)
            data_verification_project_query = execute_read_query(verification_project_query)
            if data_verification_project_query is None:
                response = {"Error": "Server error when trying to process the query!"}
                self.send_data(status_code=500, data_response=response)
            elif len(data_verification_project_query) == 0:
                response = {"Error": "Project with that id not found!"}
                self.send_data(status_code=404, data_response=response)
            else:
                verification_task_query = """ SELECT * FROM tasks
                                                WHERE id = {} AND project_id = {}; """.format(id_task, id_project)
                data_verification_task_query = execute_read_query(verification_task_query)
                if data_verification_task_query is None:
                    response = {"Error": "Server error when trying to process the query!"}
                    self.send_data(status_code=500, data_response=response)
                elif len(data_verification_task_query) == 0:
                    response = {"Error": "Task with that id related to that project not found!"}
                    self.send_data(status_code=404, data_response=response)
                else:
                    delete_query = """ DELETE FROM tasks WHERE project_id = ? AND id = ?; """
                    data_delete_query = tuple([id_project, id_task])
                    # print(delete_query)
                    # print(data_delete_query)

                    if not execute_delete_query(sql_query=delete_query, sql_data=data_delete_query):
                        response = {"Error": "Server error when trying to process the query!"}
                        self.send_data(status_code=500, data_response=response)
                    else:
                        retrieve_query = """ SELECT * FROM tasks
                                                WHERE project_id={}""".format(id_project)
                        data_retrieve_query = execute_read_query(sql_query=retrieve_query)
                        if data_retrieve_query is None:
                            response = {"Error": "Server error when trying to process the query!"}
                            self.send_data(status_code=500, data_response=response)
                        else:
                            self.send_data(status_code=200, data_response=data_retrieve_query)

        else:
            response = {"Error": "Server could not answer to the given route!"}
            self.send_data(status_code=400, data_response=response)


if __name__ == "__main__":
    db_connection = create_connection('database.sqlite3')
    create_tables(conn=db_connection)

    with HTTPServer(('localhost', PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()

    db_connection.close()
