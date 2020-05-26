const validator = require('express-validator');
const utils = require('../utils/index');
const data = require('../utils/data');
const express = require('express');
const https = require('https');
const appDB = require('../controller/appDB');
const visionML = require('../controller/visionML');


class modelManager {

    static model_get_all_fn = [
        (req, res, next) => {
            appDB.db_get_all('models', (models, err) => {
                if(err){
                    models = undefined;
                }
                res.render('models', {models: models});
            });
        }
    ];

    static model_create_get_fn = [
        (req, res, next) => {
            appDB.db_get_all('datasets', (datasets, err) => {
                if(err){
                    datasets = undefined;
                }
                res.render('create_model', {datasets: datasets});
            });
        }
    ];

    static model_create_fn = [
        validator.body('name', 'Model name required!').isLength({min: 1}),
        validator.body('datasetId', 'Dataset Name required!').isLength({min: 1}),
        (req, res, next) => {
            let errors = validator.validationResult(req);
            if(!errors.isEmpty()){
                appDB.db_get_all('datasets', (datasets, err) => {
                    if(err){
                        datasets = undefined;
                    }
                    res.render('create_model', {datasets: datasets, errors: errors.array()});
                });
            }
            else if(req.body === undefined || req.body.name === undefined || req.body.datasetId === undefined){
                res.status(400).send('Invalid request!');
            }
            else{
                let modelName = req.body.name;
                let datasetId = req.body.datasetId;
                visionML.create_model(datasetId, modelName, (response, error) => {
                    if(error){
                        res.status(400).send('Failed creating model!');
                        if(error.code === 8) {
                            res.status(400).send('Running out of rate quota for AutoML image classification concurrent model creation.');
                        }
                    }
                    else{
                        const model_data = {
                            modelID: '', /*none yet*/
                            datasetID: datasetId,
                            modelName: modelName,
                            operation_name: response.name,
                            operation_done: response.done
                        };
                        appDB.db_add('models', model_data, (response, err)=> {
                            if(err || response.status !== 200){
                                res.status(400).send('Failed creating model!');
                            }
                            else{
                                res.status(200).send('Created model ' + modelName + ' !');
                            }
                        });
                    }
                })
            }
        }
    ];

}

module.exports = modelManager;