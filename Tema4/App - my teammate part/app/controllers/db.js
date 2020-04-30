const utils = require('../utils/index');
const https = require('https');
const http = require('http');

class DBManager {

    static db_url = 'cloud-database.eastus.azurecontainer.io';

    static db_get = (id, next) => {
        const options = {
            hostname: DBManager.db_url,
            path: '/notes/get/' + id,
            method: 'GET',
        };
        const req = http.request(options, (res) => {
            if(res.statusCode !== 200){
                next(undefined);
            }else{
                utils.get_body_data(res, () => {
                    if(utils.validate_note(res.body)){
                        next(res.body);
                    }
                    else {
                        next(undefined);
                    }
                });
            }
        });
        req.on('error', (err) => {
            next(null, err);
        });
        req.end();
    };

    static db_get_all = (next) => {
        const options = {
            hostname: DBManager.db_url,
            path: '/notes/list',
            method: 'GET',
        };
        const req = http.request(options, (res) => {
            if(res.statusCode !== 200){
                next(undefined);
            }else{
                utils.get_body_data(res, () => {
                    let notes = res.body;
                    let valid_notes = [];
                    if(notes === null || notes === undefined || !Array.isArray(notes)){
                        notes = undefined;
                        valid_notes = undefined;
                    }else{
                        notes.forEach((note) => {
                            if(utils.validate_note(note)){
                                valid_notes.push(note);
                            }
                        });
                    }
                    next(valid_notes);
                });
            }
        });
        req.on('error', (err) => {
            next(undefined, err);
        });
        req.end();
    };

    static db_add = (note, next) => {
        // note.id = "5";
        const data = JSON.stringify(note);
        const options = {
            hostname: DBManager.db_url,
            path: '/notes/add',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': data.length
            }
        };

        const req = http.request(options, (res) => {
            LOG('ADD REQUEST: ' + res.statusCode);
            utils.get_body_data(res, () => {
                LOG('BODY: ');
                LOG(res.body);
                next(res.body);
            });

        });
        req.on('error', (err)=> {
            LOG(err);
            next(null, err);
        });

        req.write(data);
        req.end();
    }

}

module.exports = DBManager;