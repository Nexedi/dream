/*global console, jQuery, rJS, RSVP, alert, Handlebars, initGadgetMixin */
/*jslint nomen: true */
(function(window, $, rJS, RSVP, Handlebars, initGadgetMixin) {
    "use strict";
    /////////////////////////////////////////////////////////////////
    // Desactivate jQuery Mobile URL management
    /////////////////////////////////////////////////////////////////
    $.mobile.ajaxEnabled = false;
    $.mobile.linkBindingEnabled = false;
    $.mobile.hashListeningEnabled = false;
    $.mobile.pushStateEnabled = false;
    var navigation_template, gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").allowPublicAcquisition("allDocs", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.allDocs.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_ajax", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.ajax.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_post", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.post.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_remove", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.remove.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_get", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.get.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_putAttachment", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.putAttachment.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("jio_getAttachment", function(param_list) {
        return this.getDeclaredGadget("jio").push(function(jio_gadget) {
            return jio_gadget.getAttachment.apply(jio_gadget, param_list);
        });
    }).allowPublicAcquisition("whoWantToDisplayHome", function(param_list) {
        // Hey, I want to display some URL
        return this.aq_pleasePublishMyState({});
    }).allowPublicAcquisition("whoWantToDisplayThisPage", function(param_list) {
        // Hey, I want to display some URL
        return this.aq_pleasePublishMyState({
            page: param_list[0]
        });
    }).allowPublicAcquisition("whoWantToDisplayThisDocument", function(param_list) {
        // Hey, I want to display some jIO document
        return this.aq_pleasePublishMyState({
            page: "Input_viewTable",
            id: param_list[0]
        });
    }).allowPublicAcquisition("whoWantToDisplayThisDocumentPage", function(param_list) {
        // Hey, I want to display some jIO document
        return this.aq_pleasePublishMyState({
            page: param_list[0],
            id: param_list[1]
        });
    }).ready(function(g) {
        return g.aq_pleasePublishMyState({}).push(function(link) {
            g.props.element.getElementsByClassName("home_link")[0].href = link;
        });
    }).ready(function(g) {
        var jio_gadget;
        return g.getDeclaredGadget("jio").push(function(gadget) {
            jio_gadget = gadget;
            return jio_gadget.createJio({
                type: "local",
                username: "dream",
                applicationname: "dream"
            });
        }).push(function() {
            // XXX Hardcoded relative URL
            return jio_gadget.ajax({
                url: "../../getConfigurationDict"
            });
        }).push(function(evt) {
            g.props.configuration_dict = JSON.parse(evt.target.responseText);
        });
    }).ready(function(g) {
        if (navigation_template === undefined) {
            // XXX Only works as root gadget
            var source = document.getElementById("navigation-template").innerHTML;
            navigation_template = Handlebars.compile(source);
        }
    }).declareMethod("render", function(options) {
        var gadget = this, page_gadget, element = gadget.props.element.getElementsByClassName("gadget_container")[0];
        options.configuration_dict = gadget.props.configuration_dict;
        if (options.page === undefined) {
            // Redirect to the about page
            return gadget.aq_pleasePublishMyState({
                page: "InputModule_viewInputList"
            }).push(gadget.pleaseRedirectMyHash.bind(gadget));
        }
        return gadget.declareGadget(options.page + ".html").push(function(g) {
            page_gadget = g;
            if (page_gadget.render !== undefined) {
                return page_gadget.render(options);
            }
        }).push(function() {
            var navigation_list = [];
            if (page_gadget.getNavigationList !== undefined) {
                navigation_list = page_gadget.getNavigationList();
            }
            return RSVP.all([ page_gadget.getTitle(), page_gadget.getElement(), navigation_list ]);
        }).push(function(result_list) {
            var title = result_list[0], page_element = result_list[1], navigation_list = result_list[2], panel = gadget.props.element.querySelector("#leftpanel");
            gadget.props.element.querySelector("header h1").textContent = title;
            while (panel.firstChild) {
                panel.removeChild(panel.firstChild);
            }
            panel.innerHTML = navigation_template({
                navigationlist: navigation_list
            });
            // XXX JQuery mobile
            $(panel).trigger("create");
            // Append in the DOM at the end to reduce flickering and reduce DOM
            // modifications
            // Clear the previous rendering
            while (element.firstChild) {
                element.removeChild(element.firstChild);
            }
            element.appendChild(page_element);
            $(element).trigger("create");
            // XXX RenderJS hack to start sub gadget services
            // Only work if this gadget has no parent.
            if (page_gadget.startService !== undefined) {
                return page_gadget.startService();
            }
        });
    });
})(window, jQuery, rJS, RSVP, Handlebars, initGadgetMixin);