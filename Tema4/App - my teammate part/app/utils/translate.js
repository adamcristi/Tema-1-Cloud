'use strict';

let request = require('request');
let keys = require('../key/tema4-private.js');

class Translator {

    static translate_fn = function(text, target, next) {
        let translated = {
            text: text,
            text_language: undefined,
            translated: undefined,
            translated_language: undefined
        };

        let options = keys.translator_text.options;
        options["body"][0]["text"] = text;
        // options["qs"]["to"] = [target];

        request(options, (err, res, body) => {
            if (err) {
                LOG(err);
                next(translated);
            } else {
                try {
                    translated.text_language = body[0]["detectedLanguage"]["language"];
                    translated.translated = body[0]["translations"][0]["text"];
                    translated.translated_language = body[0]["translations"][0]["to"];
                    next(translated);
                } catch (e) {
                    next(translated);
                }
            }
        });
    }

}

module.exports = Translator;