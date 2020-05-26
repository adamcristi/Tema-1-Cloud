const express = require('express');
const router = express.Router();
const modelManager = require('../controller/modelManager');
const bodyParser = require('body-parser');

router.get('/', modelManager.model_get_all_fn);

router.post('/create_model', bodyParser.urlencoded({extended: true}), modelManager.model_create_fn);
router.get('/create_model', modelManager.model_create_get_fn);

module.exports = router;