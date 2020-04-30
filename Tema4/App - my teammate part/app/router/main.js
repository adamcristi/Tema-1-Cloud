const express = require('express');
const router = express.Router();
const notes_routes = require('./notes');

router.get('/', (req, res) => {
    // res.render('index', {title: 'CC3', message: 'Alo pronto sunt contactu'});
    res.render('index', {title: 'CC3', message: 'Notes App!'});
});

router.get('/index.html', (req, res) => {
    // res.render('index', {title: 'CC3', message: 'Alo pronto sunt contactu'});
    res.render('index', {title: 'CC3', message: 'Notes App!'});
});

router.get('/about.html', (req, res) => {
    res.sendfile('./views/about.html');
});

router.use('/notes', notes_routes);

module.exports = router;