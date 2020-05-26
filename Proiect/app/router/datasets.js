const express = require('express');
const router = express.Router();
const datasetManager = require('../controller/datasetManager');
const storageML = require('../controller/storageML');
const visionML = require('../controller/visionML');
const multer = require('multer');

const FILES_LIMIT = 1000;

router.get('/', datasetManager.datasets_get_all_fn);

const upload = multer({
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 2 * 1024 * 1024
    }
});

// router.post('/', upload.array('files', 1000), storageML.upload_files);
router.post('/create_dataset',
    upload.fields([{name: 'csv_file', maxCount:1}, {name: 'samples', maxCount: FILES_LIMIT}]),
    storageML.upload_files_middleware,
    visionML.create_dataset_middleware,
    visionML.import_dataset_middleware);

router.get('/create_dataset', (req, res) => {
    res.render('create_dataset.pug');
});

module.exports = router;