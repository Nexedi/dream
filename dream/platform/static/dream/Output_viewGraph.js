/*global rJS, jQuery, initGadgetMixin, console */
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
    function graph_widget(output_data, config) {
        /* FIXME: does not support more than one replic (Buffer family).
     * + see george email to integrate without the need of an EG
     */
        var conf_data = config.data, ticks = [], counter = 1, series = [], options = {};
        $.each(output_data.elementList.sort(function(a, b) {
            return a.id < b.id ? -1 : 1;
        }), function(idx, obj) {
            var reqKey, // ctrl_flag = false, 
            request, i;
            // if the obj is of the requested family
            if (obj.family === config.family) {
                if (config.plot === "bars") {
                    for (reqKey in conf_data) {
                        if (conf_data.hasOwnProperty(reqKey)) {
                            request = 0;
                            for (i = 0; i <= conf_data[reqKey].length - 1; i += 1) {
                                request += getRequestedValue(obj, conf_data[reqKey][i]);
                            }
                            series.push({
                                label: reqKey,
                                data: [ [ counter, request ] ]
                            });
                        }
                    }
                    ticks.push([ counter, obj.id ]);
                    counter += 1;
                } else if (config.plot === "line") {
                    series.push({
                        label: obj.name || obj.id,
                        data: obj.results.wip_stat_list
                    });
                }
            }
        });
        if (config.plot === "bars") {
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
        }
        console.log("series");
        console.log(series);
        console.log("options");
        console.log(options);
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
            console.log("rendering view graph");
            var json_data = JSON.parse(simulation_json), config = json_data.application_configuration.output[options.action].configuration;
            console.log(config);
            console.log(json_data.result.result_list[gadget.props.result]);
            gadget.props.result_list = graph_widget(json_data.result.result_list[gadget.props.result], config);
        });
    }).declareMethod("startService", function() {
        console.log("service graph");
        console.log(this.props.result_list);
        // XXX Manually calculate width and height when resizing
        $.plot(this.props.element.querySelector(".graph_container"), this.props.result_list[0], this.props.result_list[1]);
    });
})(window, rJS, jQuery, initGadgetMixin);