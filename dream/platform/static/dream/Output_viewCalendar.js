/*global rJS, RSVP, jQuery, scheduler,
         initGadgetMixin, console */
/*jslint nomen: true, unparam: true */
(function(window, rJS, RSVP, $, scheduler, initGadgetMixin) {
    "use strict";
    var gadget_klass = rJS(window);
    initGadgetMixin(gadget_klass);
    gadget_klass.declareAcquiredMethod("aq_getAttachment", "jio_getAttachment").declareMethod("render", function(options) {
        var jio_key = options.id, gadget = this;
        gadget.props.jio_key = jio_key;
        gadget.props.result = options.result;
        gadget.props.action_definition = options.action_definition;
        return gadget.aq_getAttachment({
            _id: gadget.props.jio_key,
            _attachment: "body.json"
        }).push(function(simulation_json) {
            var json_data = JSON.parse(simulation_json);
            gadget.props.result = json_data.result.result_list[options.result].sample_gantt;
        });
    }).declareMethod("xstartService", function() {
        scheduler.config.multisection = true;
        scheduler.templates.event_class = function(start, end, event) {
            var original = scheduler.getEvent(event.id);
            if (!scheduler.isMultisectionEvent(original)) {
                return "";
            }
            return "multisection section_" + event.section_id;
        };
        scheduler.config.xml_date = "%Y-%m-%d %H:%i";
        scheduler.locale.labels.timeline_tab = "Timeline";
        scheduler.locale.labels.unit_tab = "Unit";
        scheduler.locale.labels.section_custom = "Section";
        var sections = [ {
            key: 1,
            label: "James Smith"
        }, {
            key: 2,
            label: "John Williams"
        }, {
            key: 3,
            label: "David Miller"
        }, {
            key: 4,
            label: "Linda Brown"
        } ];
        scheduler.createTimelineView({
            name: "timeline",
            x_unit: "hour",
            x_date: "%H:%i",
            x_step: 8,
            x_size: 33,
            x_length: 33,
            event_dy: 60,
            resize_events: false,
            y_unit: sections,
            y_property: "section_id",
            render: "bar",
            second_scale: {
                x_unit: "day",
                // unit which should be used for second scale
                x_date: "%F %d"
            }
        });
        scheduler.date.timeline_start = scheduler.date.day_start;
        scheduler.createUnitsView({
            name: "unit",
            property: "section_id",
            list: sections
        });
        scheduler.config.lightbox.sections = [ {
            name: "description",
            height: 130,
            map_to: "text",
            type: "textarea",
            focus: true
        }, {
            name: "custom",
            height: 22,
            map_to: "section_id",
            type: "multiselect",
            options: sections,
            vertical: "false"
        }, {
            name: "time",
            height: 72,
            type: "time",
            map_to: "auto"
        } ];
        scheduler.init("scheduler_here", new Date(2012, 5, 30), "timeline");
        scheduler.parse([ {
            start_date: "2012-06-30 09:00",
            end_date: "2012-06-30 18:00",
            text: "Task A-12458",
            section_id: "1"
        }, {
            start_date: "2012-06-30 10:00",
            end_date: "2012-06-30 16:00",
            text: "Task A-89411",
            section_id: "1"
        }, {
            start_date: "2012-06-30 4:00",
            end_date: "2012-06-30 15:00",
            text: "Task 1,3",
            section_id: "1,3"
        }, {
            start_date: "2012-06-30 16:00",
            end_date: "2012-07-01 17:00",
            text: "Task A-46598",
            section_id: "1"
        }, {
            start_date: "2012-07-04 00:00",
            end_date: "2012-07-04 23:00",
            text: "Task 2,3,4",
            section_id: "2,3,4"
        }, {
            start_date: "2012-07-01 02:00",
            end_date: "2012-07-01 16:00",
            text: "Task B-44864",
            section_id: "2"
        }, {
            start_date: "2012-07-06 02:00",
            end_date: "2012-07-06 18:00",
            text: "Task C-32421",
            section_id: "3"
        }, {
            start_date: "2012-07-02 08:30",
            end_date: "2012-07-02 19:45",
            text: "Task 3,1",
            section_id: "3,1"
        }, {
            start_date: "2012-06-30 11:40",
            end_date: "2012-07-02 16:30",
            text: "Task 4,2,3",
            section_id: "4,2,3"
        }, {
            start_date: "2012-06-30 12:00",
            end_date: "2012-06-30 18:00",
            text: "Task D-12458",
            section_id: "4"
        } ], "json");
    }).declareMethod("startService", function() {
        console.log("start", this.props.result);
        scheduler.config.xml_date = "%Y-%m-%d %H:%i";
        scheduler.config.time_step = 30;
        scheduler.config.multi_day = true;
        scheduler.locale.labels.section_subject = "Subject";
        scheduler.config.first_hour = 6;
        scheduler.config.limit_time_select = true;
        scheduler.config.details_on_dblclick = true;
        scheduler.config.details_on_create = true;
        scheduler.templates.event_class = function(start, end, event) {
            var css = "";
            if (event.subject) {
                // if event has subject property then special class should be assigned
                css += "event_" + event.subject;
            }
            if (event.id === scheduler.getState().select_id) {
                css += " selected";
            }
            return css;
        };
        var subject = [ {
            key: "",
            label: "Appointment"
        }, {
            key: "english",
            label: "English"
        }, {
            key: "math",
            label: "Math"
        }, {
            key: "science",
            label: "Science"
        } ];
        scheduler.config.lightbox.sections = [ {
            name: "description",
            height: 43,
            map_to: "text",
            type: "textarea",
            focus: true
        }, {
            name: "subject",
            height: 20,
            type: "select",
            options: subject,
            map_to: "subject"
        }, {
            name: "time",
            height: 72,
            type: "time",
            map_to: "auto"
        } ];
        scheduler.init($(this.props.element).find("#scheduler_here")[0], new Date(2015, 3, 18), "week");
        scheduler.parse([ {
            start_date: "2015-04-18 09:00",
            end_date: "2015-04-18 12:00",
            text: "English lesson",
            subject: "english"
        }, {
            start_date: "2015-04-20 10:00",
            end_date: "2015-04-21 16:00",
            text: "Math exam",
            subject: "math"
        }, {
            start_date: "2015-04-21 10:00",
            end_date: "2015-04-21 14:00",
            text: "Science lesson",
            subject: "science"
        }, {
            start_date: "2015-04-23 16:00",
            end_date: "2015-04-23 17:00",
            text: "English lesson",
            subject: "english"
        }, {
            start_date: "2015-04-24 09:00",
            end_date: "2015-04-24 17:00",
            text: "Usual event"
        } ], "json");
        return new RSVP.Queue().push(function() {
            // Infinite wait, until cancelled
            return new RSVP.defer().promise;
        }).push(undefined, function(error) {
            scheduler.clearAll();
            throw error;
        });
    });
})(window, rJS, RSVP, jQuery, scheduler, initGadgetMixin);