/*global window, RSVP, $, rJS*/
(function(window, RSVP, $, rJS) {
    "use strict";
    rJS(window).declareAcquiredMethod("getConfigurationDict", "getConfigurationDict").declareMethod("startService", function() {
        var g = this;
        return RSVP.all([ g.getElement(), g.getConfigurationDict() ]).then(function(result) {
            var render_element = $(result[0]).find("#tools-container");
            $.each(result[1], function(key, val) {
                var name = val.name || key.split("-")[1];
                if (key !== "Dream-Configuration") {
                    render_element.append('<div id="' + key + '" class="tool ' + key + '">' + name + "<ul/></div>");
                }
            });
        });
    });
})(window, RSVP, $, rJS);