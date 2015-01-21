/*global rJS, RSVP, jQuery, gantt,
         initGadgetMixin */
/*jslint nomen: true, unparam: true */
(function(window, rJS, RSVP, $, gantt, initGadgetMixin) {
    "use strict";
    gantt.templates.task_class = function(start, end, obj) {
        return obj.parent ? "sub_task" : "";
    };
    function job_gantt_widget(data, result_id) {
        // XXX: use dhx_gantt zoom level feature (
        // http://dhtmlx.com/docs/products/dhtmlxGantt/02_features.html )
        var now = new Date(), start_date, gantt_data = {
            data: [ {
                id: "by_order",
                text: "By Order",
                start_date: start_date,
                duration: 0,
                project: 1,
                open: true
            }, {
                id: "by_station",
                text: "By Station",
                start_date: start_date,
                duration: 0,
                project: 1,
                open: true
            } ],
            link: []
        }, input_data = data, output_data = data.result.result_list[result_id];
        // temporary hack
        now.setHours(0);
        now.setMinutes(0);
        now.setSeconds(0);
        start_date = input_data.general.currentDate;
        if (start_date !== undefined && start_date !== "") {
            start_date = new Date(start_date);
        } else {
            start_date = new Date(now.getTime());
        }
        function isVisibleStation(station) {
            // we should be able to define in the backend which
            // station is visible
            return input_data.graph.node[station].family !== "Buffer" && input_data.graph.node[station].family !== "Exit";
        }
        $.each(output_data.elementList.sort(function(a, b) {
            return a.id < b.id ? -1 : 1;
        }), function(idx, obj) {
            var input_job = null, input_order = null, i, j, node, node_key, order, component, duration, seen_parts = {};
            if (obj.family === "Job") {
                // find the corresponding input
                // find the input order and order component for this job
                for (node_key in input_data.graph.node) {
                    if (input_data.graph.node.hasOwnProperty(node_key)) {
                        node = input_data.graph.node[node_key];
                        if (node.wip) {
                            for (i = 0; i < node.wip.length; i += 1) {
                                order = node.wip[i];
                                if (order.id === obj.id) {
                                    input_job = input_order = order;
                                }
                                if (input_job === null && order.componentsList) {
                                    for (j = 0; j < order.componentsList.length; j += 1) {
                                        component = order.componentsList[j];
                                        if (component.id === obj.id) {
                                            input_order = order;
                                            input_job = component;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                duration = 0;
                if (input_job === input_order) {
                    // if we are on the order definition
                    gantt_data.data.push({
                        id: input_order.id,
                        text: input_order.name,
                        project: 1,
                        open: false,
                        parent: "by_order"
                    });
                }
                seen_parts = {};
                $.each(obj.results.schedule, function(i, schedule) {
                    var task_start_date, job_full_id;
                    // Filter intermediate steps in part job shop
                    if (isVisibleStation(schedule.stationId)) {
                        if (schedule.exitTime) {
                            duration = 24 * (schedule.exitTime - schedule.entranceTime);
                        } else {
                            if (obj.results.schedule[i + 1]) {
                                duration = obj.results.schedule[i + 1].entranceTime - schedule.entranceTime;
                            } else {
                                duration = obj.results.completionTime - schedule.entranceTime;
                            }
                        }
                        if (duration > 0) {
                            task_start_date = new Date(start_date.getTime());
                            // for simulation time unit as days
                            // task_start_date.setDate(task_start_date.getDate() +
                            //   schedule['entranceTime']);
                            // for simulation time unit as days hours
                            task_start_date.setTime(task_start_date.getTime() + schedule.entranceTime * 1e3 * 3600 * 24);
                            job_full_id = input_job.id + "." + input_order.id;
                            if (seen_parts[job_full_id] === undefined) {
                                gantt_data.data.push({
                                    id: job_full_id,
                                    text: input_job.name,
                                    parent: input_order.id
                                });
                                seen_parts[job_full_id] = 1;
                            }
                            gantt_data.data.push({
                                id: input_order.id + "." + idx + "_" + i,
                                text: schedule.stationId,
                                start_date: task_start_date,
                                duration: duration,
                                parent: job_full_id
                            });
                            gantt_data.data.push({
                                id: "job." + obj.id + "." + idx + "_" + i,
                                text: input_order.name + "-" + input_job.name,
                                start_date: task_start_date,
                                duration: duration,
                                parent: schedule.stationId,
                                by_station: 1
                            });
                        }
                    }
                });
            } else {
                if (isVisibleStation(obj.id)) {
                    gantt_data.data.push({
                        id: obj.id,
                        text: obj.id,
                        project: 1,
                        open: false,
                        parent: "by_station"
                    });
                }
            }
        });
        //     gantt_output_height = 35 * (gantt_data.data.length + 1) + 1;
        gantt_data.data.sort(function(a, b) {
            // sort gantt data in a chronological order
            var result;
            if (a.start_date === undefined && b.start_date !== undefined) {
                result = 1;
            } else if (a.start_date !== undefined && b.start_date === undefined) {
                result = -1;
            } else if (a.start_date === undefined && b.start_date === undefined) {
                result = 0;
            } else if (a.start_date > b.start_date) {
                result = 1;
            } else if (a.start_date < b.start_date) {
                result = -1;
            } else {
                result = 0;
            }
            return result;
        });
        return gantt_data;
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
            gadget.props.result = job_gantt_widget(JSON.parse(simulation_json), gadget.props.result);
        });
    }).declareMethod("startService", function() {
        $(this.props.element).find(".gant_container").dhx_gantt({
            data: this.props.result,
            readonly: true,
            /* for days has simulation time unit
        scale_unit: 'day',
        step: 7
        */
            // for hours has simulation time unit
            scale_unit: "day",
            duration_unit: 60 * 60 * 1e3,
            //date_grid: "%H:%i",
            date_scale: "%M/%d",
            step: 1,
            subscales: [ {
                unit: "hour",
                step: 4,
                date: "%H:%i"
            } ]
        });
        return new RSVP.Queue().push(function() {
            // Infinite wait, until cancelled
            return new RSVP.defer().promise;
        }).push(undefined, function(error) {
            gantt.clearAll();
            throw error;
        });
    });
})(window, rJS, RSVP, jQuery, gantt, initGadgetMixin);