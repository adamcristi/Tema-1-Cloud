'use strict';

const language = require('@google-cloud/language');

class Language {

    static client = new language.LanguageServiceClient();

    static process(text, next){
        const document = {
            content: text,
            type: 'PLAIN_TEXT'
        };

        Language.client.analyzeSentiment({document: document})
            .then(([result]) => {
                return result.documentSentiment;
            })
            .then((sentiment) => {
                next(sentiment, null);
            })
            .catch((err) => {
                LOG(err);
                next({}, err);
            });
    }

}

module.exports = Language;