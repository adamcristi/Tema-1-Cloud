const express = require('express');
const Notes = require('../controllers/notes');
const router = express.Router();

router.get('/', Notes.notes_get_fn);
router.get('/create', Notes.create_get_fn);
router.post('/create', Notes.create_post_fn);
router.get('/details/:id', Notes.details_get_fn);

module.exports = router;