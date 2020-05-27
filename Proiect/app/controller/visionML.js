const validator = require('express-validator');
const data = require('../utils/data');
const express = require('express');

const appDB = require('../controller/appDB');

const {AutoMlClient} = require('@google-cloud/automl').v1;
const {PredictionServiceClient} = require('@google-cloud/automl').v1;

class visionML {

    static automl_client = new AutoMlClient();
    static automl_prediction_client = new PredictionServiceClient();

    static create_dataset = async (displayName, classificationType, callback) => {
        let request = {
            parent: visionML.automl_client.locationPath(data.projectID, data.location),
            dataset: {
                displayName: displayName,
                imageClassificationDatasetMetadata: {
                    // classificationType: 'MULTICLASS',
                    classificationType: classificationType,
                }
            }
        };
        const [operation] = await visionML.automl_client.createDataset(request);
        const [response] = await operation.promise();
        callback(response, null);

        // visionML.automl_client.createDataset(request)
        //     .then((response) => {
        //         return response[1];
        //     })
        //     .then(response => {
        //         callback(response, null);
        //     })
        //     .catch(err =>{
        //         callback(null, err);
        //     });
    };

    // const path = 'gs://BUCKET_ID/path_to_training_data.csv';

    static import_dataset = (datasetID, path, callback) => {
        let request = {
            name: visionML.automl_client.datasetPath(data.projectID, data.location, datasetID),
            inputConfig: {
                gcsSource: {
                    inputUris: path.split(','),
                },
            },
        };
        // const [operation] = await visionML.automl_client.importData(request);
        // const [response] = await operation.promise();
        // let astd = 1;
        // callback(response, null);
        visionML.automl_client.importData(request)
            .then(response => {
                return response[0];
            })
            .then(response => {
                callback(response, null);
            })
            .catch(err => {
                callback(null, err);
            });
    };

    static create_model = (datasetID, displayName, callback) => {
        let request = {
            parent: visionML.automl_client.locationPath(data.projectID, data.location),
            model: {
                displayName: displayName,
                datasetId: datasetID,
                imageClassificationModelMetadata: {
                    trainBudgetMilliNodeHours: 24000,
                }
            }
        };

        visionML.automl_client.createModel(request)
            .then(([response]) => {
                callback(response, null);
            })
            .catch(err => {
                callback(null, err);
            });
    };

    static get_model_evaluation = (modelID, callback) => {
        let request = {
            parent: visionML.automl_client.modelPath(data.projectID, data.location, modelID),
            filter: '',
        };

        visionML.automl_client.listModelEvaluations(request)
            .then(response => {
                callback(response, null);
            })
            .catch(err => {
                callback(null, err);
            });
    };

    static predict_model = (content, modelID, callback) => {
        let request = {
            name: visionML.automl_client.modelPath(data.projectID, data.location, modelID),
            payload: {
                image: {
                    imageBytes: content,
                }
            }
        };

        visionML.automl_prediction_client.predict(request)
            .then(([response]) => {
                return response.payload;
            })
            .then(payload => {
                callback(payload, null);
            })
            .catch(err => {
                callback(null, err);
            });
    };

    static delete_model = (modelID, callback) => {
        let request = {
            name: visionML.automl_client.modelPath(data.projectID, data.location, modelID),
        };

        visionML.automl_client.deleteModel(request)
            .then(response => {
                callback(response, null);
            })
            .catch(err => {
                callback(null, err);
            });
    };

    static get_operation_status = async (operation_name) => {
        const request = {
            name: operation_name
        };
        const [response] = await visionML.automl_client.operationsClient.getOperation(request);
        return response;
    };


    static create_dataset_middleware = (req, res, next) => {
        if(req.gs_path_csv !== undefined && req.displayName !== undefined){
            let displayName = req.displayName;
            visionML.create_dataset(displayName, 'MULTICLASS', (response_create, err_create) => {
                if(err_create){
                    res.status(400).send('Failed creating dataset!');
                }
                else{
                    if(response_create === undefined || response_create.name === undefined){
                        res.status(400).send('Failed creating dataset!');
                    }
                    else {
                        req.datasetID = response_create.name.split('/')[response_create.name.split('/').length - 1].split('\n')[0];
                        req.datasetName = response_create.name;
                        next();
                    }
                }
            }).catch(err => {
                res.status(400).send('Failed creating dataset!');
            });
        }
        else{
            res.status(400).send('Failed creating dataset!');
        }
    };

    static import_dataset_middleware = (req, res, next) => {
        let datasetID = req.datasetID;
        let datasetName = req.datasetName;
        let displayName = req.displayName;
        let gs_path_csv = req.gs_path_csv;
        visionML.import_dataset(datasetID, gs_path_csv, (response_import, err_import) => {
            if(err_import){
                res.status(400).send('Failed importing dataset!');
            }
            else{
                const dataset_data = {
                    datasetID: datasetID,
                    displayName: displayName,
                    gs_path_csv: gs_path_csv,
                    operation_name: response_import.name,
                    operation_done: response_import.done
                };
                appDB.db_add('datasets', dataset_data, (response, error) => {
                    if(error || response.status !== 200){
                        res.status(400).send('Failed importing dataset!');
                    }
                    else{
                        res.status(200).send('Finished create and import dataset!');
                    }
                });
            }
        })
    }

}

module.exports = visionML;
