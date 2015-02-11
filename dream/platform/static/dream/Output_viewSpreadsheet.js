/*global rJS, RSVP, initGadgetMixin, $ */
(function(window, rJS, RSVP, initGadgetMixin, $) {
    "use strict";
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        return new RSVP.Queue().push(function() {
            return RSVP.all([ gadget.aq_getAttachment({
                _id: jio_key,
                _attachment: "body.json"
            }), gadget.getDeclaredGadget("tableeditor") ]);
        }).push(function(result_list) {
            var content = JSON.parse(result_list[0]).result.result_list[options.result][options.action_definition.configuration.output_id], handsontable_options = {
                readOnly: true
            };
            $.extend(handsontable_options, options.action_definition.configuration.handsontable_options || {});
            result_list[1].render(JSON.stringify(content), handsontable_options);
        });
    }).declareMethod("startService", function() {
        return this.getDeclaredGadget("tableeditor").push(function(tableeditor) {
            return tableeditor.startService();
        });
    });
})(window, rJS, RSVP, initGadgetMixin, $);