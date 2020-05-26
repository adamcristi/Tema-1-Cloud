const validator = require('express-validator');
const data = require('../utils/data');
const express = require('express');

const {Storage} = require('@google-cloud/storage');

class storageML {

    static client = new Storage();

    static upload_files_middleware = (req, res, next) => {
        try {
            if (!req.body || req.body.name === undefined || req.body.name === "") {
                res.status(400).send('No name given!');
            } else if (!req.files || req.files === {}) {
                res.status(400).send('No files uploaded.');
            } else if (req.files.samples === undefined || req.files.samples.length === 0) {
                res.status(400).send('No files uploaded.');
            } else if (req.files.csv_file === undefined || req.files.csv_file === 0) {
                res.status(400).send('No csv_file uploaded.');
            } else {
                const bucket = storageML.client.bucket(data.bucketID);
                let datasetName = req.body.name;
                let promises = [];

                let gs_abs_path_samples = "gs://" + data.bucketID + '/' + datasetName + '/' + 'samples/';
                let gs_abs_path_csv = "gs://" + data.bucketID + '/' + datasetName + '/' + 'csv/';
                let abs_path_samples = datasetName + '/' + 'samples/';
                let abs_path_csv = datasetName + '/' + 'csv/';

                let parsed_csv_file = {
                    data: null,
                    gs_path: gs_abs_path_csv + datasetName + '.csv',
                    path: abs_path_csv + datasetName + '.csv',
                    name: datasetName + '.csv'
                };

                let samples = req.files.samples;
                let csv = req.files.csv_file[0];
                let csv_strs = csv.buffer.toString();
                let csv_paths = csv_strs.split('\n');

                let new_paths = [];

                for (let idx in csv_paths) {
                    let p = csv_paths[idx];
                    let tags = p.split(',', 2)[1];
                    let new_p = (p.split(',', 2)[0]).split('/');
                    let sample_name = new_p[new_p.length - 1];
                    sample_name = gs_abs_path_samples + sample_name + ',' + tags;
                    new_paths.push(sample_name);
                }

                parsed_csv_file.data = Buffer.from(new_paths.join('\n'), 'utf-8');

                bucket.file(datasetName + '/').createWriteStream().end("");
                bucket.file(datasetName + '/' + 'samples/').createWriteStream().end("");
                bucket.file(datasetName + '/' + 'csv/').createWriteStream().end("");

                const blob = bucket.file(parsed_csv_file.path);
                const blobStream = blob.createWriteStream();
                blobStream.on('error', (err) => {
                    bucket.deleteFiles({prefix: datasetName + '/'}, function (err) {
                    });
                    res.status(400).send('Failed uploading csv!');
                });
                blobStream.end(parsed_csv_file.data);

                for (let idx in samples) {
                    let sample = samples[idx];

                    const sample_blob = bucket.file(abs_path_samples + sample.originalname);
                    const new_promise = new Promise((resolve, reject) => {
                        sample_blob.createWriteStream()
                            .on('finish', async response => {
                                resolve(response);
                            })
                            .on('error', err => {
                                reject('upload error: ', err);
                            })
                            .end(sample.buffer);
                    });
                    promises.push(new_promise);
                }

                Promise.all(promises).then((response) => {
                    req.gs_path_csv = parsed_csv_file.gs_path;
                    req.displayName = datasetName;
                    next();
                    })
                    .catch((err) => {
                        res.status(400).send('Upload fail');
                        // res.status(400).send(err.message);
                    });
                }
            }
        catch (e) {
            res.send(500).send('Internal error!');
        }

    };



}

module.exports = storageML;