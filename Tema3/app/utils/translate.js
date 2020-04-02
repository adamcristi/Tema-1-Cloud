'use strict';

const {Translate} = require('@google-cloud/translate').v2;

class Translator {

static translate = new Translate();

static translate_fn = function(text, target, next){
    let translated = {
        text: text,
        text_language: undefined,
        translated: undefined,
        translated_language: undefined
    };
    Translator.detect_language_fn(text, (language, err) => {
        if(err){
            LOG(err);
            next(translated);
        }
        else{
            translated.text_language = language.language;
            Translator.translate.translate(text, target)
                .then((translations) => {
                    return Array.isArray(translations) ? translations : [translations];
                })
                .then((translations) => {
                    return translations[0];
                })
                .then((translation) => {
                    translated.translated = translation;
                    translated.translated_language = target;
                    next(translated);
                })
                .catch((err)=>{
                    LOG(err);
                    next(translated);
                })
        }
    });
};

static detect_language_fn = function(text, next){
    // let [detections] = await Translator.translate.detect(text);
    // detections = Array.isArray(detections) ? detections : [detections];
    Translator.translate.detect(text)
        .then((detections) => {
            return Array.isArray(detections) ? detections : [detections];
        })
        .then((detections) => {
            return detections[0];
        })
        .then((language) => {
            next(language, null);
        })
        .catch((err) => {
            next(null, err);
        });
}

}

module.exports = Translator;