/*global console, jQuery, rJS, RSVP, alert, Handlebars, initGadgetMixin, confirm, alert */
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
    // Prompt user to reload after manifest update.
    // from http://www.html5rocks.com/en/tutorials/appcache/beginner/#toc-updating-cache
    window.addEventListener("load", function() {
        var updating = false;
        if (window.applicationCache) {
            window.applicationCache.addEventListener("downloading", function() {
                updating = true;
            }, false);
            window.applicationCache.addEventListener("updateready", function() {
                if (window.applicationCache.status === window.applicationCache.UPDATEREADY) {
                    // Browser downloaded a new app cache.
                    // Swap it in and reload the page to get the new hotness.
                    window.applicationCache.swapCache();
                    if (confirm("A new version of this site is available. Load it?")) {
                        window.location.reload();
                    }
                }
            }, false);
            window.applicationCache.addEventListener("error", function() {
                if (updating) {
                    alert("Fatal error while updating, retrying");
                    window.location.reload();
                }
            }, false);
        }
    }, false);
    /////////////////////////////////////////////////////////////////
    // Minimalistic ERP5's like portal type configuration
    /////////////////////////////////////////////////////////////////
    var portal_types = {
        "Input Module": {
            view: {
                gadget: "InputModule_viewInputList",
                type: "object_list",
                title: "Document List"
            },
            view_fast_input: {
                gadget: "InputModule_viewAddDocumentDialog",
                type: "object_fast_input",
                title: "Create Document"
            }
        }
    }, panel_template, navigation_template, active_navigation_template, error_template, gadget_klass = rJS(window);
    function calculateTabHTML(gadget, options, key, title, active) {
        return new RSVP.Queue().push(function() {
            var kw = {
                action: key,
                id: options.id
            };
            if (options.result !== undefined) {
                kw.result = options.result;
            }
            return gadget.aq_pleasePublishMyState(kw);
        }).push(function(url) {
            var kw = {
                title: title,
                link: url
            };
            if (active === true) {
                return active_navigation_template(kw);
            }
            return navigation_template(kw);
        });
    }
    function getNextLink(gadget, portal_type, options) {
        var forward_kw = {
            action: options.action || "view"
        }, queue = new RSVP.Queue();
        if (portal_type === "Input") {
            forward_kw.id = options.id;
        } else if (portal_type === "Output") {
            forward_kw.id = options.id;
            queue.push(function() {
                return gadget.getDeclaredGadget("jio");
            }).push(function(jio_gadget) {
                return jio_gadget.getAttachment({
                    _id: options.id,
                    _attachment: "body.json"
                });
            }).push(function(sim_json) {
                var document_list = JSON.parse(sim_json), current = parseInt(options.result, 10);
                if (current === document_list.length - 1) {
                    forward_kw.result = 0;
                } else {
                    forward_kw.result = current + 1;
                }
            });
        } else if (portal_type !== "Input Module") {
            throw new Error("Unknown portal type: " + portal_type);
        }
        return queue.push(function() {
            return gadget.aq_pleasePublishMyState(forward_kw);
        });
    }
    function getTitle(gadget, portal_type, options) {
        var title;
        if (portal_type === "Input Module") {
            title = "Documents";
        } else if (portal_type === "Input") {
            title = gadget.getDeclaredGadget("jio").push(function(jio_gadget) {
                return jio_gadget.get({
                    _id: options.id
                });
            }).push(function(jio_doc) {
                return jio_doc.data.title + " (" + jio_doc.data.modified + ")";
            });
        } else if (portal_type === "Output") {
            title = gadget.getDeclaredGadget("jio").push(function(jio_gadget) {
                return jio_gadget.getAttachment({
                    _id: options.id,
                    _attachment: "body.json"
                });
            }).push(function(sim_json) {
                var document_list = JSON.parse(sim_json).result.result_list;
                return document_list[options.result].score + " " + document_list[options.result].key;
            });
        } else {
            throw new Error("Unknown portal type: " + portal_type);
        }
        return title;
    }
    function calculateNavigationHTML(gadget, portal_type, options) {
        var nav_html, action;
        if (portal_types[portal_type][options.action].type === "object_view") {
            return new RSVP.Queue().push(function() {
                var url_list = [], action_item_list = [], i, key2;
                for (key2 in portal_types[portal_type]) {
                    if (portal_types[portal_type].hasOwnProperty(key2)) {
                        action = portal_types[portal_type][key2];
                        if (action.type === "object_view") {
                            if (action.condition === undefined || action.condition(gadget)) {
                                action_item_list.push([ key2, action ]);
                            }
                        }
                    }
                }
                /*
          * Sort actions so that higher priorities are displayed first.
          * If no priority is defined, sort by action id to have stable order.
          */
                action_item_list.sort(function(a, b) {
                    var key_a = a[0], value_a = a[1], key_b = b[0], value_b = b[1];
                    if (!isNaN(value_a.priority)) {
                        if (!isNaN(value_b.priority)) {
                            return value_b.priority - value_a.priority;
                        }
                        return -1;
                    }
                    if (!isNaN(value_b.priority)) {
                        return 1;
                    }
                    return key_a < key_b ? -1 : key_a > key_b ? 1 : 0;
                });
                for (i = 0; i < action_item_list.length; i += 1) {
                    url_list.push(calculateTabHTML(gadget, options, action_item_list[i][0], action_item_list[i][1].title, action_item_list[i][0] === options.action));
                }
                return RSVP.all(url_list);
            }).push(function(entry_list) {
                var i;
                nav_html = '<nav data-role="navbar" data-collapsible="true"><ul>';
                for (i = 0; i < entry_list.length; i += 1) {
                    nav_html += entry_list[i];
                }
                nav_html += "</ul></nav>";
                return nav_html;
            });
        }
    }
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash").allowPublicAcquisition("jio_allDocs", function(param_list) {
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
    }).allowPublicAcquisition("whoWantsToDisplayHome", function() {
        // Hey, I want to display some URL
        return this.aq_pleasePublishMyState({});
    }).allowPublicAcquisition("whoWantsToDisplayThisDocument", function(param_list) {
        // Hey, I want to display some jIO document
        // XXX should be merged with whoWantsToDisplayThisResult
        var kw = {
            action: param_list[1] || "view"
        };
        if (param_list[0] !== undefined) {
            kw.id = param_list[0];
        }
        return this.aq_pleasePublishMyState(kw);
    }).allowPublicAcquisition("whoWantsToDisplayThisResult", function(param_list) {
        // Hey, I want to display some jIO document
        // We'll display the result using the first enabled action
        var action = "view", action_info, action_id;
        for (action_id in portal_types.Output) {
            if (portal_types.Output.hasOwnProperty(action_id)) {
                action_info = portal_types.Output[action_id];
                // XXX condition not needed
                if (action_info.condition === undefined || action_info.condition(this)) {
                    action = action_id;
                    break;
                }
            }
        }
        return this.aq_pleasePublishMyState({
            action: action,
            id: param_list[0],
            result: param_list[1]
        });
    }).ready(function() {
        if (panel_template === undefined) {
            // XXX Only works as root gadget
            panel_template = Handlebars.compile(document.getElementById("panel-template").innerHTML);
            navigation_template = Handlebars.compile(document.getElementById("navigation-template").innerHTML);
            active_navigation_template = Handlebars.compile(document.getElementById("active-navigation-template").innerHTML);
            error_template = Handlebars.compile(document.getElementById("error-template").innerHTML);
        }
    }).ready(function(g) {
        return new RSVP.Queue().push(function() {
            return RSVP.all([ g.aq_pleasePublishMyState({}), g.aq_pleasePublishMyState({
                action: "view_fast_input"
            }) ]);
        }).push(function(link_list) {
            var panel = g.props.element.querySelector("#leftpanel");
            panel.innerHTML = panel_template({
                navigationlist: []
            });
            panel.getElementsByClassName("home_link")[0].href = link_list[0];
            panel.getElementsByClassName("fast_input_link")[0].href = link_list[1];
            // XXX JQuery mobile
            $(panel).trigger("create");
        });
    }).ready(function(g) {
        return g.getDeclaredGadget("jio").push(function(gadget) {
            return gadget.createJio({
                type: "query",
                sub_storage: {
                    type: "document",
                    document_id: "/",
                    sub_storage: {
                        type: "local"
                    }
                }
            });
        });
    }).declareMethod("render", function(options) {
        var gadget = this, back_kw = {
            action: "view"
        }, page_gadget, portal_type = "Input Module", nav_element = gadget.props.element.getElementsByClassName("nav_container")[0], element = gadget.props.element.getElementsByClassName("gadget_container")[0];
        if (options.action === undefined) {
            // Redirect to the view action
            options.action = "view";
            return gadget.aq_pleasePublishMyState(options).push(gadget.pleaseRedirectMyHash.bind(gadget));
        }
        // Detect what is the kind of document displayed
        if (options.id !== undefined) {
            if (options.result === undefined) {
                portal_type = "Input";
            } else {
                portal_type = "Output";
                back_kw.action = "view_result";
                back_kw.id = options.id;
            }
        }
        return gadget.getDeclaredGadget("jio").push(function(jio_gadget) {
            if (options.id) {
                return jio_gadget.getAttachment({
                    _id: options.id,
                    _attachment: "body.json"
                });
            }
        }).push(function(result) {
            var data;
            if (result) {
                try {
                    data = JSON.parse(result);
                } catch (error) {
                    portal_type = "Input";
                    options.action = "debug";
                    portal_types.Input = {
                        debug: {
                            gadget: "Input_viewDebugJson",
                            type: "object_view",
                            title: "Emergency Mode, JSON cannot be parsed"
                        }
                    };
                    return gadget.declareGadget("Input_viewDebugJson.html");
                }
                gadget.props.data = data;
                portal_types.Input = data.application_configuration.input;
                portal_types.Output = data.application_configuration.output;
            }
            options.action_definition = portal_types[portal_type][options.action];
            // Get the action information
            return gadget.declareGadget(portal_types[portal_type][options.action].gadget + ".html");
        }).push(function(g) {
            page_gadget = g;
            if (page_gadget.render !== undefined) {
                return page_gadget.render(options);
            }
        }).push(function() {
            return RSVP.all([ page_gadget.getElement(), calculateNavigationHTML(gadget, portal_type, options), gadget.aq_pleasePublishMyState(back_kw), getTitle(gadget, portal_type, options), getNextLink(gadget, portal_type, options) ]);
        }).push(function(result_list) {
            var nav_html = result_list[1], page_element = result_list[0];
            // Update title
            gadget.props.element.querySelector("header h1").textContent = result_list[3];
            // XXX Hide the back button in case of module display?
            // Update back link
            gadget.props.element.getElementsByClassName("back_link")[0].href = result_list[2];
            // XXX Hide the forward button in case of non result?
            // Update forward link
            gadget.props.element.getElementsByClassName("next_link")[0].href = result_list[4];
            // Update the navigation panel
            // Clear the previous rendering
            while (nav_element.firstChild) {
                nav_element.removeChild(nav_element.firstChild);
            }
            if (nav_html !== undefined) {
                nav_element.innerHTML = nav_html;
                $(nav_element).trigger("create");
            }
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
        }).push(undefined, function(error) {
            if (error instanceof RSVP.CancellationError) {
                throw error;
            }
            console.error(error.stack);
            document.querySelector("article[class='gadget_container']").innerHTML = error_template({
                error: error,
                error_stack: error.stack
            });
        });
    });
})(window, jQuery, rJS, RSVP, Handlebars, initGadgetMixin);