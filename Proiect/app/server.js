const router = require('./router/main');
const express = require('express');
const multer = require('multer');
const app = express();
const path = require('path');

require('./utils/init')();

app.set('views', './view');
app.set('view engine', 'pug');

app.use("/static", express.static(path.join(__dirname, 'static')));

app.use('/', router);

// Listen to the App Engine-specified port, or 8080 otherwise
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});