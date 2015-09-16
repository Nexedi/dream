/*global rJS, RSVP, initGadgetMixin, promiseEventListener, $, setTimeout */
(function (window, rJS, RSVP, initGadgetMixin, promiseEventListener, $) {
  "use strict";


  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.aq_getAttachment({
              "_id": jio_key,
              "_attachment": "body.json"
            }),
            gadget.getDeclaredGadget("tablediff")
          ]);
        })
        .push(function (result_list){
          var reference_spreadsheet = JSON.parse(result_list[0]).input.reference_spreadsheet || [],
            new_spreadsheet = JSON.parse(result_list[0]).result.result_list[options.result][options.action_definition.configuration.output_id];

          gadget.props.new_spreadsheet = new_spreadsheet;
          gadget.props.options = options;
          return result_list[1].render(JSON.stringify([reference_spreadsheet, new_spreadsheet]));
        });
    })
    .declareMethod("startService", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return promiseEventListener(
            gadget.props.element.querySelector(".set_reference_schedule_button"),
            'click',
            false
          );
        }).push(function() {
            return gadget.aq_getAttachment({
              _id: gadget.props.jio_key,
              _attachment: "body.json"
           });
        }).push(function (data) {
          var object_data = JSON.parse(data);
          // XXX option for that
          object_data.input.reference_spreadsheet = gadget.props.new_spreadsheet;
          object_data.input.reference_solution = parseInt(gadget.props.options.result, 10);
          return gadget.aq_putAttachment({
            "_id": gadget.props.jio_key,
           "_attachment": "body.json",
           "_data": JSON.stringify(object_data, null, " ")
          }).push(function (){
            // XXX quick way to get a popup message
            $.mobile.loading( 'show', { text: "Current schedule set as reference", textVisible: true, textonly: true });
            setTimeout(function () { $.mobile.loading( "hide" ); }, 1000);
          });
        });
    });
}(window, rJS, RSVP, initGadgetMixin, promiseEventListener, $));
