var express = require('express');
var app = express();

// Setting a html view engine - Make sure you install consolidate and mustache
app.engine('html', require('consolidate').mustache);
app.set('view engine', 'html');


//your routes here
app.get('/', function (req, res) {
    //res.send("Hello World!");
    res.render('index.html');
});

app.listen(8080, function () {
  console.log('Example app listening on port 8080!');
});
