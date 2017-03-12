var page = require('webpage').create();
var system = require('system');

var address = system.args[1];
var save = system.args[2];

page.open(address, function() {
  // being the actual size of the headless browser
  page.viewportSize = {
                width: 1024,height: 768
      };

  page.clipRect = {
    top:    0,
    left:   0,
    width:  1024,
    height: 768
  };

  page.render(save);
  phantom.exit(0);
});