'use strict';

let https = require('https');
let keys = require('../key/tema4-private');
let utils = require('../utils');

class Language {

    static process(text, next){
        let body = keys.text_analytics.sentiment.body;
        body['documents'][0]['text'] = text;

        let sentiment = {
            score: 0.0
        };

        let request_params = keys.text_analytics.sentiment.request_params;

        let req = https.request(request_params, (response) => {
            utils.get_body_data(response, ()=> {
                let result = response.body;
                if (result === null || result === undefined){
                    next({}, null);
                }
                else{
                    if(result.hasOwnProperty("documents") && Array.isArray(result["documents"])){
                        let docs = result["documents"];
                        sentiment.score = docs[0]["score"];
                        next(sentiment, null);
                    }
                    else{
                        next({}, null);
                    }
                }
            })
        });
        req.write(JSON.stringify(body));
        req.on('error', (err) => {
            next(undefined, err);
        });
        req.end();
    }

}

module.exports = Language;