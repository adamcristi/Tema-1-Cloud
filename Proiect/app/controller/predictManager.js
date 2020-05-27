const validator = require('express-validator');
const utils = require('../utils/index');
const data = require('../utils/data');
const express = require('express');
const https = require('https');
const appDB = require('../controller/appDB');
const visionML = require('../controller/visionML');

const multer = require('multer');

const upload = multer({
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 2 * 1024 * 1024
    }
});

class predictManager {

    static predict_get_fn = [
        (req, res, next) => {
            appDB.db_get_all('models', (models, err) => {
                if(err){
                    models = undefined;
                }
                res.render('predict', {models: models});
            });
        }
    ];

    static predict_fn = [
        upload.single('prediction_file'),
        validator.body('modelId', 'Model name required!').isLength({min: 1}),
        (req, res, next) =>{
            let errors = validator.validationResult(req);
            if(!errors.isEmpty()) {
                appDB.db_get_all('models', (models, err) => {
                    if(err){
                        models = undefined;
                    }
                    res.render('predict', {models: models, errors: errors.array()});
                });
            }
            else if(req.body === undefined ||
                req.body.modelId === undefined ||
                req.file === undefined ||
                req.file.buffer === undefined){
                res.status(400).send('No file uploaded!');
            }
            else{
                let modelID = req.body.modelId;
                let content = req.file.buffer;
                visionML.predict_model(content, modelID, (response, err) => {
                    let _predictions = response;
                    let predictions = [];
                    if(_predictions === null || _predictions === undefined || !Array.isArray(_predictions)) {
                        predictions = undefined;
                        res.render('predict_result', {predictions: predictions});
                    }
                    else {
                        _predictions.forEach((prediction) => {
                            predictions.push({
                                className: prediction.displayName,
                                score: prediction.classification.score
                            });
                        });
                        res.render('predict_result', {predictions: predictions});
                    }
                });
            }
        }
    ];

}

module.exports = predictManager;