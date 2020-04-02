const router = require('./router/main');
const express = require('express');
const app = express();

const bodyParser = require('body-parser');
const multer = require('multer');
const upload = multer();


/* init */
require('./utils/init')();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(upload.array());

app.set('views', './views');
app.set('view engine', 'pug');

app.use('/', router);

// Listen to the App Engine-specified port, or 8080 otherwise
const PORT = process.env.PORT || 8080;

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});