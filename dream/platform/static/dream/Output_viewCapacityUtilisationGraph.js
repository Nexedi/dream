/*global rJS, jQuery, initGadgetMixin */
/*jslint unparam: true */
(function(window, rJS, $, initGadgetMixin) {
    "use strict";
    function capacity_utilisation_graph_widget(data, result_id) {
        var available_capacity_by_station = {}, station_id, series, graph_list = [], options, capacity_usage_by_station = {}, input_data = data, output_data = data.result.result_list[result_id];
        // Compute availability by station
        $.each(input_data.graph.node, function(idx, obj) {
            var available_capacity = [];
            if (obj.intervalCapacity !== undefined) {
                $.each(obj.intervalCapacity, function(i, capacity) {
                    available_capacity.push([ i, capacity ]);
                });
                available_capacity_by_station[obj.id] = available_capacity;
            }
        });
        // Compute used capacity by station
        $.each(output_data.elementList.sort(function(a, b) {
            return a.id < b.id ? -1 : 1;
        }), function(idx, obj) {
            if (obj.results !== undefined && obj.results.capacityUsed !== undefined) {
                var capacity_usage = [];
                $.each(obj.results.capacityUsed, function(i, step) {
                    var period = 0, usage = 0;
                    $.each(step, function(k, v) {
                        if (k === "period") {
                            period = v;
                        }
                    });
                    $.each(step, function(k, v) {
                        if (k !== "utilization" && k !== "period") {
                            usage += v;
                        }
                    });
                    capacity_usage.push([ period, usage ]);
                });
                capacity_usage_by_station[obj.id] = capacity_usage;
            }
        });
        for (station_id in available_capacity_by_station) {
            if (available_capacity_by_station.hasOwnProperty(station_id)) {
                series = [ {
                    label: "Capacity",
                    data: available_capacity_by_station[station_id],
                    color: "green"
                }, {
                    label: "Utilisation",
                    data: capacity_usage_by_station[station_id],
                    color: "red"
                } ];
                options = {
                    series: {
                        lines: {
                            show: true,
                            fill: true
                        }
                    }
                };
                graph_list.push([ input_data.graph.node[station_id].name || station_id, series, options ]);
            }
        }
        return graph_list;
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
            gadget.props.result_list = capacity_utilisation_graph_widget(JSON.parse(simulation_json), gadget.props.result);
        });
    }).declareMethod("startService", function() {
        var element = $(this.props.element), graph;
        $.each(this.props.result_list, function(idx, result) {
            graph = $("<div class='capacity_graph' " + "style='width: 70%; height: 250px'></div>");
            element.append($("<h2>").text(result[0]), graph);
            $.plot(graph, result[1], result[2]);
        });
    });
})(window, rJS, jQuery, initGadgetMixin);