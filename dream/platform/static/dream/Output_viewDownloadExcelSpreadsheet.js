/*global rJS, RSVP, jQuery, initGadgetMixin */
/*jslint nomen: true, unparam: true */
(function(window, rJS, RSVP, $, initGadgetMixin) {
    "use strict";
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        gadget.props.result = options.result;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "body.json"
        }).push(function(simulation_json) {
            var result = JSON.parse(simulation_json)[0].result, download_link = gadget.props.element.querySelector(".download_link");
            download_link.download = "demandPlannerOutput.xls";
            download_link.href = "data:application/excel;base64," + result["demandPlannerOutput.xls"];
        });
    }).declareMethod("startService", function() {
        return new RSVP.Queue().push(function() {
            // Infinite wait, until cancelled
            return new RSVP.defer().promise;
        });
    });
})(window, rJS, RSVP, jQuery, initGadgetMixin);