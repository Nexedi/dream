/*global jQuery, rJS, window, JSON, RSVP */

(function (window, $, rJS, JSON, RSVP) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (content, options) {
      var data = JSON.parse(content);
      return this.getElement()
        .push(function (element) {
          $(element).find('.table-container')
                    .handsontable($.extend({
              data: data,
              stretchH: 'all'
            }, options || {}));
        });
    })

    .declareMethod('getData', function () {
      return this.getElement()
        .push(function (element) {
          var data = $(element).find('.table-container')
                               .handsontable('getData');
          return JSON.stringify(data);
        });
    })

    .declareMethod("startService", function () {
      var gadget_element;
      return this.getElement()
        .push(function (element) {
          gadget_element = element;
          $(element).find('.table-container').handsontable("render");
        })
        .push(function () {
          // Infinite wait, until cancelled
          return (new RSVP.defer()).promise;
        })
        .push(undefined, function (error) {
          $(gadget_element).find('.table-container').handsontable("destroy");
          throw error;
        });
    });
}(window, jQuery, rJS, JSON, RSVP));
