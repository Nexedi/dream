/*global rJS, RSVP, initGadgetMixin, loopEventListener, console */
(function (window, rJS, RSVP, initGadgetMixin, loopEventListener) {
  "use strict";

  function saveSpreadsheet(evt) {
    var gadget = this,
      editor_data,
      editor_gadget;
    return new RSVP.Queue()
      .push(function () {
        // Prevent double click
        if (evt) {
          evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
        }
        return gadget.getDeclaredGadget("tableeditor");
      })
      .push(function (tablegadget) {
        editor_gadget = tablegadget;
        return editor_gadget.getData();
      })
      .push(function (data) {
        editor_data = data;
        // Always get a fresh version, to prevent deleting spreadsheet & co
        return gadget.aq_getAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json"
        });
      })
      .push(function (body) {
        var data = JSON.parse(body);
        // create a property within input 
        // with name the provided at render time
        data.input[gadget.props.name] = JSON.parse(editor_data);
        return gadget.aq_putAttachment({
          "_id": gadget.props.jio_key,
          "_attachment": "body.json",
          "_data": JSON.stringify(data, null, 2),
          "_mimetype": "application/json"
        });
      })
      .push(function () {
        if (evt) {
          evt.target.getElementsByClassName("ui-btn")[0].disabled = false;
        }
      });
  }


  function waitForSave(gadget) {
    return loopEventListener(
      gadget.props.element.getElementsByClassName("save_form")[0],
      'submit',
      false,
      saveSpreadsheet.bind(gadget)
    );
  }

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
      console.log("generic spreadsheet RENDER1");
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;
      // view_##### is the formulatino of the names
      gadget.props.name = options.action.substr(5, options.action.length);
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.aq_getAttachment({
              "_id": jio_key,
              "_attachment": "body.json"
            }),
            gadget.getDeclaredGadget("tableeditor")
          ]);
        })
        .push(function (result_list) {
          var i, content,
            result = JSON.parse(result_list[0]),
            config = result.application_configuration.input;
          // if there are previously stored data in input for this sprSheet
          if (result.input[gadget.props.name]) {
            content = result.input[gadget.props.name];
          } else {
            // otherwise use the clean configuration
            for (i = 0; i <= Object.keys(config).length; i += 1) {
              if (Object.keys(config)[i] === options.action) {
                content = config[options.action].configuration.columns;
              }
            }
          }
          // application_configuration.input.view_???_spreasheet.configuration
          return result_list[1].render(
            JSON.stringify(content),
            { minSpareRows: 1,
              onChange: function () {
                if (gadget.timeout) {
                  window.clearTimeout(gadget.timeout);
                }
                gadget.timeout = window.setTimeout(
                  saveSpreadsheet.bind(gadget),
                  100
                );
              }
            }
          );
        });
    })

    .declareMethod("startService", function () {
      var gadget = this;
      return this.getDeclaredGadget("tableeditor")
        .push(function (tableeditor) {
          return RSVP.all([
            tableeditor.startService(),
            waitForSave(gadget)
          ]);
        });
    });
}(window, rJS, RSVP, initGadgetMixin, loopEventListener));
