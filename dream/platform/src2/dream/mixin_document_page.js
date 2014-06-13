/*global console, RSVP */
(function (window, RSVP) {
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
              gadget.whoWantToDisplayThisDocumentPage(
                "Input_viewProductionLine",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage("Input_viewTable", key),
              gadget.whoWantToDisplayThisDocumentPage(
                "Input_viewSimulation",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Input_viewDocumentManagement",
                key
              ),

              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewStationUtilisationGraph",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewQueueStatGraph",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewExitStatistics",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewJobGantt",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewJobScheduleSpreadsheet",
                key
              ),
              gadget.whoWantToDisplayThisDocumentPage(
                "Output_viewDebugJson",
                key
              )
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

}(window, RSVP));
