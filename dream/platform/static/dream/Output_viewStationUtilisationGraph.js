/*global rJS, jQuery, initGadgetMixin */
/*jslint unparam: true */
(function(window, rJS, $, initGadgetMixin) {
    "use strict";
    function getRequestedValue(object, key) {
        var value = 0;
        if (object.results[key] !== undefined) {
            if (object.results[key].avg !== undefined) {
                value = object.results[key].avg;
            } else {
                value = object.results[key];
            }
        }
        return value;
    }
    function station_utilisation_graph_widget(output_data, config) {
        var data = {}, ticks = [], counter = 1, key, series = [], options;
        // initialize the data dict holding the properties requested
        for (key in config) {
            if (config.hasOwnProperty(key)) {
                data[key] = [];
            }
        }
        // XXX output is still elementList ???
        $.each(output_data.elementList.sort(function(a, b) {
            return a.id < b.id ? -1 : 1;
        }), function(idx, obj) {
            var ctrl_flag = false, reqKey, request, i;
            // determine weather the current 
            // obj has the requested key
            for (reqKey in config) {
                if (config.hasOwnProperty(reqKey)) {
                    if (obj.results !== undefined && obj.results[config[reqKey][0]] !== undefined) {
                        // control flag, if the results contain 
                        // entities that have working ratios
                        ctrl_flag = true;
                        break;
                    }
                }
            }
            // if the obj contains the requested key
            if (ctrl_flag === true) {
                for (reqKey in config) {
                    if (config.hasOwnProperty(reqKey)) {
                        request = 0;
                        for (i = 0; i <= config[reqKey].length - 1; i += 1) {
                            request += getRequestedValue(obj, config[reqKey][i]);
                        }
                        data[reqKey].push([ counter, request ]);
                    }
                }
                ticks.push([ counter, obj.id ]);
                counter += 1;
            }
        });
        for (key in data) {
            if (data.hasOwnProperty(key)) {
                series.push({
                    label: key,
                    data: data[key]
                });
            }
        }
        options = {
            xaxis: {
                minTickSize: 1,
                ticks: ticks
            },
            yaxis: {
                max: 100
            },
            series: {
                bars: {
                    show: true,
                    barWidth: .7,
                    align: "center"
                },
                stack: true
            }
        };
        return [ series, options ];
    }
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        gadget.props.result = options.result;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "simulation.json"
        }).push(function(simulation_json) {
            var json_data = JSON.parse(simulation_json), config = json_data.application_configuration.output[options.action].configuration.data;
            gadget.props.result_list = station_utilisation_graph_widget(json_data.result.result_list[gadget.props.result], config);
        });
    }).declareMethod("startService", function() {
        // XXX Manually calculate width and height when resizing
        $.plot(this.props.element.querySelector(".graph_container"), this.props.result_list[0], this.props.result_list[1]);
    });
})(window, rJS, jQuery, initGadgetMixin);