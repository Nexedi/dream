/*global console, rJS, RSVP, Handlebars, initGadgetMixin */
/*jslint nomen: true */
(function(window, rJS, RSVP, Handlebars, initGadgetMixin) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), source = gadget_klass.__template_element.getElementById("table-template").innerHTML, table_template = Handlebars.compile(source);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareAcquiredMethod("whoWantToDisplayThisResult", "whoWantToDisplayThisResult").declareMethod("render", function(options) {
        var gadget = this;
        this.props.jio_key = options.id;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "simulation.json"
        }).push(function(sim_json) {
            var document_list = JSON.parse(sim_json), result_list = [], i;
            for (i = 0; i < document_list.length; i += 1) {
                result_list.push(RSVP.all([ gadget.whoWantToDisplayThisResult(gadget.props.jio_key, i), document_list[i].score, document_list[i].key ]));
            }
            return RSVP.all(result_list);
        }).push(function(document_list) {
            var i, parameter_list = [], doc;
            for (i = 0; i < document_list.length; i += 1) {
                doc = document_list[i];
                parameter_list[i] = {
                    link: doc[0],
                    title: doc[1] + " " + doc[2]
                };
            }
            gadget.props.element.querySelector(".document_list").innerHTML = table_template({
                documentlist: parameter_list
            });
        });
    });
})(window, rJS, RSVP, Handlebars, initGadgetMixin);