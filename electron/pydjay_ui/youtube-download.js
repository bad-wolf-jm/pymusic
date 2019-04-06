var YouTube = require('youtube-node');

var youTube = new YouTube();

youTube.setKey('AIzaSyAZ1QneYwqT_jyYEkWvcdRsnBGedTHlzqg');
youTube.addParam('type', 'video');
youTube.search('Texas Blues', 10, function(error, result) {
  if (error) {
    console.log(error);
  }
  else {
    console.log(JSON.stringify(result, null, 2));
  }
});