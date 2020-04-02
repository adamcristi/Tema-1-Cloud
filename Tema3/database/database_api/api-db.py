import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import requests

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
notes_ref = db.collection('Notes')

url_logging_function = r"https://europe-west3-tema3-cloud-computing-272819.cloudfunctions.net/logging_database"


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


@app.route('/')
def running():
    return 'Cloud run app is now running!'


@app.route('/notes/add', methods=['POST'])
def add_note():
    try:
        if validate_json(request):
            doc_ref = notes_ref.add(request.json)
            response = {"id": doc_ref[1].id}
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
        requested_note = notes_ref.document(note_id).get()
        response = requested_note.to_dict()
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
        all_notes_data = []
        for note in notes_ref.stream():
            note_data = note.to_dict()
            note_data['id'] = note.id
            all_notes_data.append(note_data)
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_notes_data), 'status_code': str(200)})
        return jsonify(all_notes_data), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
