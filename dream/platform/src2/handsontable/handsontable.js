/*global jQuery, rJS, window, JSON */

(function (window, $, rJS, JSON) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (content) {
      var data = JSON.parse(content);
      return this.getElement()
        .push(function (element) {
          $(element).find('.table-container')
                    .handsontable({data: data});
        });
    })

    .declareMethod('getData', function () {
      return this.getElement()
        .push(function (element) {
          var data = $(element).find('.table-container')
                               .handsontable('getData');
          return JSON.stringify(data);
        });
    });
}(window, jQuery, rJS, JSON));
