// TizenBrew site module: hand the current page URL to the TV web browser.
// The module page is loaded inside TizenBrew's own runtime, so the browser
// itself is opened as a separate application with a view operation deep link.
(function () {
  'use strict';
  var TARGET = 'http://172.16.40.1:8080/probe.html';

  function launchBrowser() {
    try {
      if (typeof tizen === 'undefined') { return false; }
      var op = 'http://tizen.org/appcontrol/operation/view';
      var ctrl = new tizen.ApplicationControl(op, TARGET, null, null);
      tizen.application.launchAppControl(ctrl, 'org.tizen.browser',
        function () { console.log('browser launch ok'); },
        function (e) { console.log('launchAppControl error: ' + e.message); });
      return true;
    } catch (e) {
      console.log('launchBrowser exception: ' + e);
      return false;
    }
  }

  if (!launchBrowser()) {
    try {
      var app = new tizen.Application('org.tizen.browser');
      tizen.application.launch(app,
        function () { console.log('browser plain launch ok'); },
        function (e) { console.log('plain launch error: ' + e.message); });
    } catch (e) {
      console.log('plain launch exception: ' + e);
    }
  }
})();
