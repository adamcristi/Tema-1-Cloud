const express = require('express');
const router = express.Router();
const datasets_router = require('./datasets');
const models_router = require('./models');
const predict_router = require('./predict');

router.get('/', (req, res) => {
    res.render('home', {title: 'Cloud ML'});
});

router.get('/index.html', (req, res) => {
    res.render('index', {title: 'Cloud ML'});
});

router.use('/datasets', datasets_router);
router.use('/models', models_router);
router.use('/predict', predict_router);

module.exports = router;