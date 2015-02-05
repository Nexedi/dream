/*global rJS, RSVP, jQuery, gantt,
         initGadgetMixin, console */
/*jslint nomen: true, unparam: true */
(function(window, rJS, RSVP, $, gantt, initGadgetMixin) {
    "use strict";
    gantt.templates.task_class = function(start, end, obj) {
        return obj.parent ? "sub_task" : "";
    };
    function gantt_widget(all_data, gadget) {
        // XXX: use dhx_gantt zoom level feature (
        // http://dhtmlx.com/docs/products/dhtmlxGantt/02_features.html )
        var now = new Date(), start_date = all_data.general.currentDate, input_data = all_data.input, graph_data = all_data.graph, output_data = all_data.result.result_list[gadget.props.result], config = all_data.application_configuration.output[gadget.props.action].configuration, gantt_data;
        // temporary hack
        now.setHours(0);
        now.setMinutes(0);
        now.setSeconds(0);
        if (start_date !== undefined && start_date !== "") {
            start_date = new Date(start_date);
        } else {
            start_date = new Date(now.getTime());
        }
        gantt_data = {
            data: [ {
                id: "by_operator",
                text: "By Operator",
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
        };
        console.log("gantt gadget method");
        console.log(config);
        console.log(input_data);
        console.log(graph_data);
        console.log(output_data);
        function isVisibleStation(station) {
            var i;
            // we should be able to define in the backend which
            // station is visible
            for (i = 0; i <= output_data.elementList.length - 1; i += 1) {
                if (output_data.elementList[i].id === station) {
                    return output_data.elementList[i].family !== "Buffer" && output_data.elementList[i].family !== "Exit" && output_data.elementList[i].family !== "Operator" && output_data.elementList[i].family !== "Entry";
                }
            }
        }
        $.each(output_data.elementList.sort(function(a, b) {
            return a.id < b.id ? -1 : 1;
        }), function(idx, obj) {
            var duration = 0;
            if (obj.family === "Operator") {
                gantt_data.data.push({
                    id: obj.id,
                    text: obj.id,
                    project: 1,
                    open: false,
                    parent: "by_operator"
                });
                console.log("operator");
                console.log(obj.id);
                if (obj.results.schedule) {
                    $.each(obj.results.schedule, function(i, schedule) {
                        var task_start_date;
                        // Filter intermediate steps in part job shop
                        if (isVisibleStation(schedule.stationId)) {
                            if (schedule.exitTime) {
                                duration = 24 * (schedule.exitTime - schedule.entranceTime);
                            } else {
                                if (obj.results.schedule[i + 1]) {
                                    duration = obj.results.schedule[i + 1].entranceTime - schedule.entranceTime;
                                } else {
                                    // XXX completion time not provided
                                    duration = obj.results.completionTime - schedule.entranceTime;
                                }
                            }
                            if (duration > 0) {
                                console.log("..");
                                console.log("step");
                                console.log(i);
                                console.log("duration");
                                console.log(duration);
                                task_start_date = new Date(start_date.getTime());
                                // for simulation time unit as days
                                // task_start_date.setDate(task_start_date.getDate() +
                                //   schedule['entranceTime']);
                                // for simulation time unit as days hours
                                task_start_date.setTime(task_start_date.getTime() + schedule.entranceTime * 1e3 * 60);
                                console.log("start date");
                                console.log(task_start_date);
                                console.log(schedule.entranceTime);
                                console.log(schedule.entranceTime * 1e3 * 60);
                                gantt_data.data.push({
                                    id: obj.id + "." + schedule.stationId + "." + i,
                                    text: schedule.stationId,
                                    start_date: task_start_date,
                                    duration: duration,
                                    parent: obj.id
                                });
                                gantt_data.data.push({
                                    id: "operator." + obj.id + "." + idx + "_" + i,
                                    text: obj.id + "-" + schedule.stationId,
                                    start_date: task_start_date,
                                    duration: duration,
                                    parent: schedule.stationId,
                                    by_station: 1
                                });
                            }
                        }
                    });
                }
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
        console.log("Returning the Gantt Data");
        console.log(gantt_data);
        return gantt_data;
    }
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        gadget.props.result = options.result;
        gadget.props.action = options.action;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "body.json"
        }).push(function(simulation_json) {
            var json_data = JSON.parse(simulation_json);
            gadget.props.result = gantt_widget(json_data, gadget);
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
            duration_unit: 60 * 1e3,
            // date_grid: "%H:%i",
            date_scale: "%M/%d",
            step: 1,
            subscales: [ {
                unit: "hour",
                step: 1,
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