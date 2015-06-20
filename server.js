var express = require('express');
var app = express();
var socketio = require('socket.io');
var server = require('http').createServer(app).listen(3180, function(){
  console.log('Socket IO server listening at 3180');
});
var http = require('http');
var fs = require('fs');

fs.readFile('./index.html', function (err, html) {
  if (err) {
    throw err;
  }
  http.createServer(function(request, response) {
   response.writeHeader(200, {"Content-Type": "text/html"});
   response.write(html);
   response.end();
  }).listen(8000,function(){
    console.log('HTML OPENED');
  });
  });
 
 //app.listen(3180);
 var io = socketio.listen(server);
 /*io.sockets.on('connetcion',function(socket){
   console.log('Socket IO server listening at 3180');
   });*/
var mysql      = require('mysql').createConnection({
  host     : 'localhost',
   user     : 'root',
    password : '1q2w3e4r',
    database : 'information_schema'
});

mysql.connect(function(err){
  if(!err) {
    console.log("Database is connected ... \n\n");
  } else {
    console.log("Error connecting database ... \n\n");
  }
});
app.post('/', function (req, res) {
  res.sendfile(__dirname + '/index.html');
});
app.post('/adddb',function (req,res){
  var jsonObject = JSON.parse(data);
  var query = connection.query('INSERT INTO dbtable SET ?', post, function(err, result) {
    // Neat!
    if(err){
      console.log(err);
      throw err;
    }
  });
});

