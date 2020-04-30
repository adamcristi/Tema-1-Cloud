const validator = require('express-validator');

const express = require('express');
const router = express.Router();
const db = require('./db');
const translator = require('../utils/translate');
const language = require('../utils/language');

class Notes {

    static create_get_fn = [
        (req, res, next) => {
        res.render('create', {title: 'CC3-create'});
        }
    ];

    static create_post_fn = [
        validator.body('note', 'Note text required').isLength({min: 1}),

        (req, res, next) => {
            let errors = validator.validationResult(req);
            let note = {};
            if(!errors.isEmpty()){
                res.render('create', {title: 'CC3-create', errors: errors.array()});
            }
            else {
                translator.translate_fn(req.body.note, 'en', (translated) => {
                    // LOG(translated);
                    // res.redirect('/details');
                    note = translated;
                    if(note.translated !== undefined){
                        language.process(note.translated, (sentiment, err) => {
                            note.sentiment = sentiment;
                            LOG(note);
                            db.db_add(note, (data, err) => {
                                let id = undefined;
                                if(data !== undefined && data.hasOwnProperty("id")){
                                    id = data.id;
                                }
                                res.render('details', {title: "CC3-Details", note: note});
                            });
                        })
                    }else {
                        LOG(note);
                        res.render('details', {title: "CC3-Details", note: note});
                    }
                });
            }
        }
    ];

    static notes_get_fn = [
        (req, res, next) => {
            db.db_get_all((notes, err) => {
               if(err){
                   notes = undefined;
               }
               res.render('notes', {title: 'Notes', notes: notes});
            });
        }
    ];

    static details_get_fn = [
        (req, res, next) => {
            let id = req.params.id;
            let _note = {};
            db.db_get(id, (note, err) => {
                if(err){
                    _note = undefined;
                }else{
                    _note = note;
                }
                res.render('details', {title: 'CC3-Details', note: _note});
            });
        }
    ];

}

module.exports = Notes;