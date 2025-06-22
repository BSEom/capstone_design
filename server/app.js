var express = require('express');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
//추가?
//var parser = bodyParser.urlencoded({extended:false});
//var fileupload = require("express-fileupload");

var index = require('./routes/index');
var users = require('./routes/users');
//retrofit.js을 사용하기위해 routes 에서 가져온다
var retrofitRouter = require('./routes/retrofit');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
//수정
app.use(bodyParser.urlencoded({ extended: false }));
//추가
//app.use(express.json());

app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);
app.use('/users', users);
//retrofit.js 사용
app.use('/retrofit', retrofitRouter);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

app.listen(process.env.PORT || 3000, () => console.log('Example app listening on port 3000!'));

module.exports = app;
