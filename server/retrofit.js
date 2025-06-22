// retrofit으로 데이터를 받기위해 새로 생성하고 작성한 코드 /routes/retrofit.js 로 저장

var express = require('express');
var router = express.Router();
// multipart 사용을 위해 multer 사용
var multer = require("multer");

//const upload = multer({ dest: 'server/uploads/' })

const upload = multer({
  storage: multer.diskStorage({
    destination: function (req, file, cb) {
      cb(null, '/workspace/server/uploads/');
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname);
    }
  }),
});

var count = 0;

// 각각의 형식으로 받을때 데이터를 받는 부분과 다시 send하는 부분으로 각각 구성됨

router.get('/get', function (req, res, next) {
    console.log('GET 호출 / data : ' + req.query.data);
    console.log('path : ' + req.path);
    res.send('get success: ' + count)
	count = count + 1;
});

/*
router.post('/post', function (req, res, next) {
    console.log('POST 호출 / data : ' + req.body.data);
    console.log('path : ' + req.path);
    res.send('post success')
});
*/


router.post('/post', upload.single('audio'), function (req, res) {
   // req.file is the name of your file in the form above, here 'uploaded_file'
   // req.body will hold the text fields, if there were any 
   //console.log(req.file, req.body)
	console.log(req.file)
	res.send('upload success')
});


router.put('/put/:id', function (req, res, next) {
    console.log('UPDATE 호출 / id : ' + req.params.id);
    console.log('body : ' + req.body.data);
    console.log('path : ' + req.path);
    res.send('put success')
});

router.delete('/delete/:id', function (req, res, next) {
    console.log('DELETE 호출 / id : ' + req.params.id);
    console.log('path : ' + req.path);
    res.send('delete success')
});

module.exports = router;