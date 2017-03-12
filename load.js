// call this script like
// phantomjs load.js http://website outputPath zoom

console.log("Start phantomjs");

var scroll = 400;

var page = require('webpage').create();
var system = require('system');

var address = system.args[1];
var save = system.args[2];
var zoom = system.args[3];

console.log("Website : " + address);
console.log("Save path : " + save);

page.zoomFactor = zoom;

page.open(address, function(status) {

  if (status === "success")
  {
      page.injectJs("injectme.js")

      // being the actual size of the headless browser
      page.viewportSize = { width: 1280, height: 720 };

      var height = page.evaluate(function() { return document.body.offsetHeight });
      var act = 0;

      var urlIndex = 0;
      var d = new Date();
      var n = d.getTime();

      height = parseInt(height * page.zoomFactor);
      console.log("page =" + height);

      while (act < height)
      {
        console.log(act);

        page.clipRect = {
         top:    act,
         left:   0,
         width:  1280,
         height: 720
        };

        if(urlIndex > 99)
        {
            getFilename = save + "t" + n + "_" + urlIndex + ".jpg";
        }
        else if(urlIndex > 9)
        {
            getFilename = save + "t" + n + "_0" + urlIndex + ".jpg";
        }
        else
        {
            getFilename = save + "t" + n + "_00" + urlIndex + ".jpg";
        };

        page.render(getFilename);

        // zoom ?
        if(zoom != 1)
        {
            // workarround for zoom not working !
            if(parseInt(urlIndex) & 1)
            {
                page.zoomFactor = zoom;
            }
            else
            {
                page.zoomFactor = zoom - 0.01;
            }
        }

        urlIndex++;
        act  = act + scroll;
      };
  };

  var fs = require('fs');
  fs.write(save + 'page.html', page.content, 'w');

});

page.onLoadFinished = function(status){

   console.log('Status: ' + status);
   console.log('Starting evaluate links...');

   var txt = "";

   var links = page.evaluate(function() {
        return [].map.call(document.querySelectorAll('a'), function(link) {

            var ht = link.getAttribute('href');
            var no = link.getAttribute('ml_link');

            if(ht != null)
            {
                return ht + " [_" + no + "_]";
            }
            else
                return null;
        });
    });

   txt = links.join('\n');

   var fs = require('fs');
   try {
    fs.write(save + "links.txt", txt, 'w');
    } catch(e) {
        console.log(e);
    }

    phantom.exit(0);
}