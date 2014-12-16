/*global jQuery, rJS, window, JSON, RSVP */
(function(window, $, rJS, JSON, RSVP) {
    "use strict";
    rJS(window).declareMethod("render", function(content, options) {
        var data = JSON.parse(content), i, ctrlflag = true, def = [];
        // if the content is not an array of arrays then create one 
        // from the content
        for (i = 0; i <= data.length - 1; i += 1) {
            if (!(data[i].constructor === Array)) {
                def.push(data[i].name);
            } else {
                // otherwise do not modify anything
                def = data;
                ctrlflag = false;
                break;
            }
        }
        if (ctrlflag) {
            def = [ def ];
        }
        return this.getElement().push(function(element) {
            $(element).find(".table-container").handsontable($.extend({
                data: def,
                stretchH: "all"
            }, options || {}));
        });
    }).declareMethod("getData", function() {
        return this.getElement().push(function(element) {
            var data = $(element).find(".table-container").handsontable("getData");
            return JSON.stringify(data);
        });
    }).declareMethod("startService", function() {
        var gadget_element;
        return this.getElement().push(function(element) {
            gadget_element = element;
            $(element).find(".table-container").handsontable("render");
        }).push(function() {
            // Infinite wait, until cancelled
            return new RSVP.defer().promise;
        }).push(undefined, function(error) {
            $(gadget_element).find(".table-container").handsontable("destroy");
            throw error;
        });
    });
})(window, jQuery, rJS, JSON, RSVP);