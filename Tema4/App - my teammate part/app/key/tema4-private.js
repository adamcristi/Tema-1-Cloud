'use strict';

const uuidv4 = require('uuid/v4');

let text_analytics_secret = {
    header_name: "Ocp-Apim-Subscription-Key",

    // endpoint: "https://tema4-cc-text-analytics-we.cognitiveservices.azure.com/",
    endpoint: "https://westeurope.api.cognitive.microsoft.com",
    subscription_key: "not_provided_on_git",
    region: "westeurope",
    language: {
        path: "/text/analytics/v2.1/languages"
    },
    sentiment: {
        path: "/text/analytics/v2.1/sentiment",
    }
};

let text_analytics = {
    sentiment: {
        request_params: {
            method: 'POST',
            hostname: (new URL(text_analytics_secret.endpoint)).hostname,
            path: text_analytics_secret.sentiment.path,
            headers: {
                'Ocp-Apim-Subscription-Key': text_analytics_secret.subscription_key,
                'Ocp-Apim-Subscription-Region': text_analytics_secret.region,
            }
        },
        body: {
            /* change language with dettected one */
            'documents': [ {'id': '1', 'language': 'en', 'text': 'change this text' } ]
        }

    }
};

let translator_text_secret = {
    header_name: "Ocp-Apim-Subscription-Key",

    // endpoint: "https://tema4-cc-translator-text.cognitiveservices.azure.com/",
    // endpoint: "https://api.cognitive.microsofttranslator.com/",
    endpoint: "https://api-eur.cognitive.microsofttranslator.com/",
    region: "westeurope",
    subscription_key: "not_provided_on_git",

    /* sample options for request */
};

let translator_text = {
    options: {
        method: 'POST',
        baseUrl: translator_text_secret.endpoint,
        url: 'translate',
        qs: {
            'api-version': '3.0',
            'to': ['en']
        },
        headers: {
            'Ocp-Apim-Subscription-Key': translator_text_secret.subscription_key,
            'Ocp-Apim-Subscription-Region': translator_text_secret.region,
            'Content-type': 'application/json',
            'X-ClientTraceId': uuidv4().toString()
        },
        body: [{
            'text': 'change this with actual text'
        }],
        json: true
    }
};

exports.text_analytics = text_analytics;
exports.translator_text = translator_text;