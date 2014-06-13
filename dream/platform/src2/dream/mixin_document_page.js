/*global console, rJS, RSVP */
(function (window, rJS, RSVP) {
  "use strict";
  window.initDocumentPageMixin = function (gadget_klass) {

    gadget_klass
      .declareAcquiredMethod("whoWantToDisplayThisDocumentPage",
                             "whoWantToDisplayThisDocumentPage")
      .declareMethod("getNavigationList", function () {
        var key = this.props.jio_key,
          gadget = this;
        return new RSVP.Queue()
          .push(function () {
            // XXX Conditional simulation menu
            return RSVP.all([
              gadget.whoWantToDisplayThisDocumentPage("production_line", key),
              gadget.whoWantToDisplayThisDocumentPage("edit_table", key),
              gadget.whoWantToDisplayThisDocumentPage("run_simulation", key),
              gadget.whoWantToDisplayThisDocumentPage("manage_document", key),

              gadget.whoWantToDisplayThisDocumentPage(
                "station_utilisation_graph",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "queue_stat_graph",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage("exit_stat", key),
              gadget.whoWantToDisplayThisDocumentPage("job_gantt", key),
              gadget.whoWantToDisplayThisDocumentPage(
                "job_schedule_spreadsheet",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage("debug_json", key)
            ]);
          })
          .push(function (result_list) {
            return [
              {link: result_list[0], title: "Production line"},
              {link: result_list[1], title: "Edit table"},
              {link: result_list[2], title: "Run simulation"},
              {link: result_list[3], title: "Manage document"},
              {link: result_list[4], title: "Stations Utilization"},
              {link: result_list[5], title: "Queues Statistics"},
              {link: result_list[6], title: "Exit Statistics"},
              {link: result_list[7], title: "Job Gantt"},
              {link: result_list[8], title: "Job Schedule"},
              {link: result_list[9], title: "Debug JSON"}
            ];
          });
      });
  };

}(window, rJS, RSVP));
