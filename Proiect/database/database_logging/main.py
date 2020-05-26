from flask import jsonify
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime

cred = credentials.Certificate('proiect-ml-cloud-computing-firebase-adminsdk-4edyc-8521b71022.json')
default_app = initialize_app(cred)
db = firestore.client()


def validate_json(request_api):
    fields = ['method', 'route', 'response', 'status_code']
    if len(request_api.json) != len(fields):
        return False
    try:
        for field in fields:
            data = request_api.json[field]
        return True
    except Exception as e:
        return False


# [START functions_logging_database]
def logging_database(request):
    logs_ref = db.collection('Logs')

    if str(request.method) == "POST":
        log_data = dict()
        try:
            if validate_json(request):
                log_data['method'] = request.json['method']
                log_data['route'] = request.json['route']
                log_data['response'] = request.json['response']
                log_data['status_code'] = request.json['status_code']
                log_data['datetime'] = str(datetime.now())
                logs_ref.document().set(log_data)
                return f"Created with success", 200
            else:
                return f"Wrong body of request", 400
        except Exception as e:
            return f"An Error Occured: {e}", 500
    elif str(request.method) == "GET":
        log_method = request.args.get('method')
        log_route = request.args.get('route')
        if log_method and log_route:
            try:
                logs_with_same_method_and_route = logs_ref.where(u'method', u'==', log_method).where(u'route', u'==',
                                                                                                     log_route).stream()
                list_logs_with_same_method_and_route = []
                for log in logs_with_same_method_and_route:
                    log_data = log.to_dict()
                    log_data['id'] = log.id
                    list_logs_with_same_method_and_route.append(log_data)
                if len(list_logs_with_same_method_and_route) != 0:
                    return jsonify(list_logs_with_same_method_and_route), 200
                else:
                    return f"There are no logs with that method and route!", 200
            except Exception as e:
                return f"An Error Occured: {e}", 500
        else:
            if log_method:
                try:
                    logs_with_same_method = logs_ref.where(u'method', u'==', log_method).stream()
                    list_logs_with_same_method = []
                    for log in logs_with_same_method:
                        log_data = log.to_dict()
                        log_data['id'] = log.id
                        list_logs_with_same_method.append(log_data)
                    if len(list_logs_with_same_method) != 0:
                        return jsonify(list_logs_with_same_method), 200
                    else:
                        return f"There are no logs with that method!", 200
                except Exception as e:
                    return f"An Error Occured: {e}", 500
            else:
                if log_route:
                    try:
                        logs_with_same_route = logs_ref.where(u'route', u'==', log_route).stream()
                        list_logs_with_same_route = []
                        for log in logs_with_same_route:
                            log_data = log.to_dict()
                            log_data['id'] = log.id
                            list_logs_with_same_route.append(log_data)
                        if len(list_logs_with_same_route) != 0:
                            return jsonify(list_logs_with_same_route), 200
                        else:
                            return f"There are no logs with that route!", 200
                    except Exception as e:
                        return f"An Error Occured: {e}", 500
                else:
                    try:
                        all_logs = logs_ref.stream()
                        list_all_logs = []
                        for log in all_logs:
                            log_data = log.to_dict()
                            log_data['id'] = log.id
                            list_all_logs.append(log_data)
                        if len(list_all_logs) != 0:
                            return jsonify(list_all_logs), 200
                        else:
                            return f"There are no logs!", 200
                    except Exception as e:
                        return f"An Error Occured: {e}", 500
    else:
        return f"Wrong request method", 400
# [END functions_logging_database]

# Comanda create/update function gcloud functions deploy logging_database --runtime python37 --trigger-http --allow-unauthenticated --region europe-west3

# body example
# {
#  	"method": "POST",
#  	"route": "https://app-li2wmgcweq-ew.a.run.app/notes/get/pykA0E1rnzeD7AI55YzR",
#  	"response": "{'sentiment':{'magnitude':0.5, 'score':-0.5}, 'text':'ceva text', 'text_language':'ro', 'translated':'some text', 'translated_language':'en'}",
#  	"status_code": "200"
# }
