exports.parse = function (obj) {
    let res = null;
    try {
        res = JSON.parse(obj);
    } catch (e) {
        res = null;
    }
    return res;
};

exports.get_body_data = function(res, next){

    let    body = [];
    res.on('data', (chunk) => {
        body.push(chunk);
    });

    res.on('end', () => {
        body = Buffer.concat(body).toString();
        body = this.parse(body);

        res.body = body;
        if (body === null) {
            res.body = undefined;
        }
        next();
    });

};

exports.validate_note = function(note){
  if(note === undefined || note === null){
      return false;
  }
  return note.hasOwnProperty('text') &&
      note.hasOwnProperty('text_language') &&
      note.hasOwnProperty('translated') &&
      note.hasOwnProperty('translated_language') &&
      note.hasOwnProperty('sentiment') &&
      note.sentiment.hasOwnProperty('magnitude') &&
      note.sentiment.hasOwnProperty('score');
};