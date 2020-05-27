import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import requests

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate('proiect-ml-cloud-computing-firebase-adminsdk-4edyc-8521b71022.json')
default_app = initialize_app(cred)
db = firestore.client()
buckets_ref = db.collection('Buckets')
datasets_ref = db.collection('Datasets')
models_ref = db.collection('Models')
predictions_ref = db.collection('Predictions')

url_logging_function = r"https://us-central1-proiect-ml-cloud-computing.cloudfunctions.net/logging_database"


@app.route('/')
def running():
    return 'Cloud run app is now running!'


########################################################################################################################
# Buckets #

@app.route('/buckets/add', methods=['POST'])
def add_bucket():
    try:
        doc_ref = buckets_ref.add(request.json)
        response = {"id": doc_ref[1].id}
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(200)})
        return jsonify(response), 200
    except Exception as e:
        response = f"An Error Occurred: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/buckets/get/<string:bucket_id>', methods=['GET'])
def get_requested_bucket(bucket_id):
    try:
        requested_bucket = buckets_ref.document(bucket_id).get()
        response = requested_bucket.to_dict()
        if response is not None:
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong bucket id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/buckets/list', methods=['GET'])
def get_all_buckets():
    try:
        all_buckets_data = []
        for bucket in buckets_ref.stream():
            bucket_data = bucket.to_dict()
            bucket_data['id'] = bucket.id
            all_buckets_data.append(bucket_data)
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_buckets_data), 'status_code': str(200)})
        return jsonify(all_buckets_data), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/buckets/update/<string:bucket_id>', methods=['PUT', 'PATCH'])
def update_requested_bucket(bucket_id):
    try:
        requested_bucket = buckets_ref.document(bucket_id).get()
        response = requested_bucket.to_dict()
        if response is not None:
            for field in request.json:
                response[field] = request.json[field]
            buckets_ref.document(bucket_id).update(response)
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong bucket id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


########################################################################################################################
# Datasets #

@app.route('/datasets/add', methods=['POST'])
def add_dataset():
    try:
        doc_ref = datasets_ref.add(request.json)
        response = {"id": doc_ref[1].id}
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(200)})
        return jsonify(response), 200
    except Exception as e:
        response = f"An Error Occurred: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/datasets/get/<string:dataset_id>', methods=['GET'])
def get_requested_dataset(dataset_id):
    try:
        requested_dataset = datasets_ref.document(dataset_id).get()
        response = requested_dataset.to_dict()
        if response is not None:
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong dataset id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/datasets/list', methods=['GET'])
def get_all_datasets():
    try:
        all_datasets_data = []
        for dataset in datasets_ref.stream():
            dataset_data = dataset.to_dict()
            dataset_data['id'] = dataset.id
            all_datasets_data.append(dataset_data)
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_datasets_data), 'status_code': str(200)})
        return jsonify(all_datasets_data), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/datasets/update/<string:dataset_id>', methods=['PUT', 'PATCH'])
def update_requested_dataset(dataset_id):
    try:
        requested_dataset = datasets_ref.document(dataset_id).get()
        response = requested_dataset.to_dict()
        if response is not None:
            for field in request.json:
                response[field] = request.json[field]
            datasets_ref.document(dataset_id).update(response)
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong dataset id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


########################################################################################################################
# Models #

@app.route('/models/add', methods=['POST'])
def add_model():
    try:
        doc_ref = models_ref.add(request.json)
        response = {"id": doc_ref[1].id}
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(200)})
        return jsonify(response), 200
    except Exception as e:
        response = f"An Error Occurred: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/models/get/<string:model_id>', methods=['GET'])
def get_requested_model(model_id):
    try:
        requested_model = models_ref.document(model_id).get()
        response = requested_model.to_dict()
        if response is not None:
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong model id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/models/list', methods=['GET'])
def get_all_models():
    try:
        all_models_data = []
        for model in models_ref.stream():
            model_data = model.to_dict()
            model_data['id'] = model.id
            all_models_data.append(model_data)
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_models_data), 'status_code': str(200)})
        return jsonify(all_models_data), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/models/update/<string:model_id>', methods=['PUT', 'PATCH'])
def update_requested_model(model_id):
    try:
        requested_model = models_ref.document(model_id).get()
        response = requested_model.to_dict()
        if response is not None:
            for field in request.json:
                response[field] = request.json[field]
            models_ref.document(model_id).update(response)
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong model id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


########################################################################################################################
# Predictions #

@app.route('/predictions/add', methods=['POST'])
def add_prediction():
    try:
        doc_ref = predictions_ref.add(request.json)
        response = {"id": doc_ref[1].id}
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(200)})
        return jsonify(response), 200
    except Exception as e:
        response = f"An Error Occurred: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/predictions/get/<string:prediction_id>', methods=['GET'])
def get_requested_prediction(prediction_id):
    try:
        requested_prediction = predictions_ref.document(prediction_id).get()
        response = requested_prediction.to_dict()
        if response is not None:
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong prediction id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/predictions/list', methods=['GET'])
def get_all_predictions():
    try:
        all_predictions_data = []
        for prediction in predictions_ref.stream():
            prediction_data = prediction.to_dict()
            prediction_data['id'] = prediction.id
            all_predictions_data.append(prediction_data)
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(all_predictions_data), 'status_code': str(200)})
        return jsonify(all_predictions_data), 200
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


@app.route('/predictions/update/<string:prediction_id>', methods=['PUT', 'PATCH'])
def update_requested_prediction(prediction_id):
    try:
        requested_prediction = predictions_ref.document(prediction_id).get()
        response = requested_prediction.to_dict()
        if response is not None:
            for field in request.json:
                response[field] = request.json[field]
            predictions_ref.document(prediction_id).update(response)
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(200)})
            return jsonify(response), 200
        else:
            response = f"Wrong prediction id given!"
            requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                      'response': str(response), 'status_code': str(400)})
            return response, 400
    except Exception as e:
        response = f"An Error Occured: {e}"
        requests.post(url_logging_function, json={'method': str(request.method), 'route': str(request.url_rule),
                                                  'response': str(response), 'status_code': str(500)})
        return response, 500


########################################################################################################################

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
