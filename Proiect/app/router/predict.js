const express = require('express');
const router = express.Router();
const predictManager = require('../controller/predictManager');

router.get('/', predictManager.predict_get_fn);
router.post('/', predictManager.predict_fn);

module.exports = router;