/*global rJS, RSVP, Handlebars, initGadgetMixin */
/*jslint nomen: true */
(function(window, rJS, RSVP, Handlebars, initGadgetMixin) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Handlebars
    /////////////////////////////////////////////////////////////////
    // Precompile the templates while loading the first gadget instance
    var gadget_klass = rJS(window), source = gadget_klass.__template_element.getElementById("table-template").innerHTML, table_template = Handlebars.compile(source);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_allDocs", "jio_allDocs").declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").declareAcquiredMethod("whoWantsToDisplayThisDocument", "whoWantsToDisplayThisDocument").declareMethod("render", function() {
        var gadget = this;
        return gadget.aq_allDocs({
            select_list: [ "title", "modified" ]
        }).push(function(document_list) {
            var result_list = [], doc, i;
            for (i = 0; i < document_list.data.total_rows; i += 1) {
                doc = document_list.data.rows[i];
                result_list.push(RSVP.all([ gadget.whoWantsToDisplayThisDocument(doc.id), doc.value.title, doc.value.modified ]));
            }
            return RSVP.all(result_list);
        }).push(function(document_list) {
            // Create new doc if nothing exists
            if (document_list.length === 0) {
                return gadget.whoWantsToDisplayThisDocument(undefined, "view_fast_input").push(function(url) {
                    return gadget.pleaseRedirectMyHash(url);
                });
            }
            var i, parameter_list = [], doc;
            for (i = 0; i < document_list.length; i += 1) {
                doc = document_list[i];
                parameter_list[i] = {
                    link: doc[0],
                    title: doc[1] + " (" + doc[2] + ")",
                    date: new Date(doc[2])
                };
            }
            parameter_list.sort(function(a, b) {
                return b.date - a.date;
            });
            //           gadget.props.element.querySelector('a').href = document_list[0];
            gadget.props.element.querySelector(".document_list").innerHTML = table_template({
                documentlist: parameter_list
            });
        });
    });
})(window, rJS, RSVP, Handlebars, initGadgetMixin);