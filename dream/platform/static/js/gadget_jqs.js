/*global window, jQuery, rJS*/
"use strict";

(function (window, $, rJS) {

  function init(config) {
    this.parent = this.context.find('.jQuerySheet');
    this.parent.sheet(config);
    this.instance = this.parent.getSheet();
  }

  var default_config = {
    id: "jquerysheet-div",
    style: '',
    jquerySheet: true,
    jquerySheetCss: true,
    parser: true,
    jqueryUiCss: true,
    scrollTo: false,
    jQueryUI: false,
    raphaelJs: false,
    gRaphaelJs: false,
    colorPicker: false,
    colorPickerCss: false,
    elastic: false,
    advancedMath: false,
    finance: false,
    editable: true,
    autoFiller: true,
    urlGet: '../lib/jquery.sheet-2.0.0/new_spreadsheet.html'
  };

  rJS(window).declareMethod('getContent', function () {
    var content = JSON.stringify($.sheet.instance[0].exportSheet.json());
    //console.log("function getContent" + content);
    return content;
  })

    .declareMethod('setContent', function (content) {
      var config = $.extend({
        buildSheet: $.sheet.makeTable.json(JSON.parse(content))
      }, default_config);
      //console.log(config.buildSheet);
      init.apply(rJS(this), [config]);
    })

    .declareMethod('clearContent', function () {
      $.sheet.killAll();
      init.apply(rJS(this), [default_config]);
    })

    .ready(function () {
      init.apply(rJS(this), [default_config]);
    });

}(window, jQuery, rJS));
