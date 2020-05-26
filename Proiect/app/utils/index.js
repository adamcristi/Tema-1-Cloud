exports.parse = function (obj) {
    let res = null;
    try {
        res = JSON.parse(obj);
    } catch (e) {
        res = null;
    }
    return res;
};

exports.get_body_data = function(res, next){

    let    body = [];
    res.on('data', (chunk) => {
        body.push(chunk);
    });

    res.on('end', () => {
        body = Buffer.concat(body).toString();
        body = this.parse(body);

        res.body = body;
        if (body === null) {
            res.body = undefined;
        }
        next();
    });

};

exports.validate_db_entry = function(db_name, db_entry){
    if (db_entry === undefined || db_entry === null) {
        return false;
    }
    if(db_name === 'datasets') {
        return db_entry.hasOwnProperty("displayName") &&
            db_entry.hasOwnProperty("datasetID") &&
            db_entry.hasOwnProperty("gs_path_csv") &&
            db_entry.hasOwnProperty("operation_name") &&
            db_entry.hasOwnProperty("operation_done");
    }
    else if(db_name === 'models'){
        return db_entry.hasOwnProperty("modelID") &&
            db_entry.hasOwnProperty("modelName") &&
            db_entry.hasOwnProperty("operation_name") &&
            db_entry.hasOwnProperty("operation_done") &&
            db_entry.hasOwnProperty("datasetID");
    }
    return false;
};