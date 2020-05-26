const validator = require('express-validator');
const utils = require('../utils/index');
const data = require('../utils/data');
const express = require('express');
const https = require('https');

const {AutoMlClient} = require('@google-cloud/automl').v1;

const fn_get_operations_status = (db_name, operations, automl_client, callback) => {
    let promises = [];
    operations.forEach((db_entry) => {
        const request = {
            name: db_entry.operation_name
        };
        const promise = new Promise((resolve, reject) => {
            automl_client.operationsClient.getOperation(request)
                .then(([response]) => {
                    response.db_id = db_entry.id;
                    response.operation = db_entry;
                    resolve(response);
                })
                .catch((err) => {
                    reject(err);
                });
        });
        promises.push(promise);
        // promises.push(automl_client.operationsClient.getOperation(request));
    });
    Promise.all(promises).then((responses) => {
        let updated = [];
        responses.forEach((response) => {
            if(response.operation !== undefined){
                let operation = response.operation;
                operation.operation_done = response.done;
                if(operation.operation_done === true) {
                    let update_fields = {
                        operation_done: true
                    };
                    if(db_name === 'models'){
                        let modelID = response.name.split('/')[response.name.split('/').length - 1].split('\n')[0];
                        update_fields.modelID = modelID;
                    }
                    appDB.db_update(db_name, update_fields, operation.id, (_res, _err) => {});
                }
                updated.push(operation);
            }
        });
        callback(updated, null);
    })
    .catch((err)=> {
        callback(undefined, err);
    });
};

class appDB {

    static automl_client = new AutoMlClient();
    static db_url = 'app-kvpi7jkm6a-uc.a.run.app';

    static db_add = (db_name, dataset_data, callback) => {
        const data = JSON.stringify(dataset_data);
        const options = {
            hostname: appDB.db_url,
            path: '/' + db_name + '/add',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };
        const req = https.request(options, (res) => {
            LOG('ADD REQUEST: ' + res.statusCode);
            utils.get_body_data(res, () => {
                LOG('BODY: ');
                LOG(res.body);
                callback({body: res.body, status: res.statusCode}, null);
            });
        });
        req.on('error', (err)=> {
            LOG(err);
            callback(null, err);
        });
        req.write(data);
        req.end();
    };

    static db_update = (db_name, update_fields, entry_id, callback) => {
        const data = JSON.stringify(update_fields);
        const options = {
            hostname: appDB.db_url,
            path: '/' + db_name + '/update/' + entry_id,
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };
        const req = https.request(options, (res) => {
            LOG('UPDATE REQUEST: ' + res.statusCode);
            utils.get_body_data(res, () => {
                LOG('BODY: ');
                LOG(res.body);
                callback(res.body, null);
            });
        });
        req.on('error', (err)=> {
            LOG(err);
            callback(null, err);
        });
        req.write(data);
        req.end();
    };

    static db_get_all = (db_name, callback) => {
        const options = {
            hostname: appDB.db_url,
            path: '/' + db_name + '/list',
            method: 'GET',
        };
        const req = https.request(options, (res) => {
            if(res.statusCode !== 200){
                callback(undefined, null);
            }else{
                utils.get_body_data(res, () => {
                    let db_entries = res.body;
                    let valid_db_entries = [];
                    if(db_entries === null || db_entries === undefined || !Array.isArray(db_entries)){
                        db_entries = undefined;
                        valid_db_entries = undefined;
                        callback(valid_db_entries, null);
                    }else{
                        let not_done_operations = [];
                        let done_operations = [];
                        db_entries.forEach((db_entry) => {
                            if(utils.validate_db_entry(db_name, db_entry)){
                                if(db_entry.operation_done === false){
                                    not_done_operations.push(db_entry);
                                }
                                else{
                                    done_operations.push(db_entry);
                                }
                                valid_db_entries.push(db_entry);
                            }
                        });
                        if(not_done_operations.length === 0){
                            callback(valid_db_entries, null);
                        }
                        else{
                            fn_get_operations_status(db_name, not_done_operations, appDB.automl_client, (response, err) => {
                                let updated_db_entries = response;
                                if(updated_db_entries.length === 0 || updated_db_entries.length !== not_done_operations.length){
                                    callback(valid_db_entries, null);
                                }
                                else {
                                    callback(done_operations.concat(updated_db_entries), null);
                                }
                            });
                        }
                    }
                });
            }
        });
        req.on('error', (err) => {
            callback(undefined, err);
        });
        req.end();
    };


}

module.exports = appDB;