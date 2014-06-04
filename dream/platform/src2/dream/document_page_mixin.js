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
              gadget.whoWantToDisplayThisDocumentPage("edit_table", key),
              gadget.whoWantToDisplayThisDocumentPage("run_simulation", key),
              gadget.whoWantToDisplayThisDocumentPage("manage_document", key),

              gadget.whoWantToDisplayThisDocumentPage("debug_json", key)
            ]);
          })
          .push(function (result_list) {
            return [
              {link: result_list[0], title: "Edit table"},
              {link: result_list[1], title: "Run simulation"},
              {link: result_list[2], title: "Manage document"},
              {link: result_list[3], title: "Debug JSON"}
            ];
          });
      });
  };

}(window, rJS, RSVP));
