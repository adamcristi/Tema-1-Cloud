const validator = require('express-validator');
const utils = require('../utils/index');
const data = require('../utils/data');
const express = require('express');
const https = require('https');
const appDB = require('../controller/appDB');
const visionML = require('../controller/visionML');


class datasetManager {

    static datasets_get_all_fn = [
        (req, res, next) => {
            appDB.db_get_all('datasets', (datasets, err) => {
                if(err){
                    datasets = undefined;
                }

                res.render('datasets', {datasets: datasets});
            });
        }
    ]

}

module.exports = datasetManager;