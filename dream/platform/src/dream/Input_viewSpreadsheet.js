/*global rJS, RSVP, initGadgetMixin, loopEventListener, $ */
(function (window, rJS, RSVP, initGadgetMixin, loopEventListener, $) {
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
      var jio_key = options.id,
        gadget = this;
      gadget.props.jio_key = jio_key;
      
      // view_##### is the formulatino of the names
      gadget.props.name = options.action.substr(5, options.action.length);
      // Use input_id from action definition
      if (options.action_definition.configuration.input_id){
        gadget.props.name = options.action_definition.configuration.input_id;
      }
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
          var content,
            i, ctrlflag = true, def  = [],
            result = JSON.parse(result_list[0]),
            handsontable_options = {
              minSpareRows: 1,
              onChange: function () {
                if (gadget.timeout) {
                  window.clearTimeout(gadget.timeout);
                }
                gadget.timeout = window.setTimeout(
                  saveSpreadsheet.bind(gadget),
                  100
                );
              }
            };

          // if there are previously stored data in input for this sprSheet
          if (result.input[gadget.props.name]) {
            content = result.input[gadget.props.name];
          } else {
            content = options.action_definition.configuration.columns;
            // XXX this is for the case of the initial setup
            // if the content is not an array of arrays then create one
            // from the content
            for (i = 0; i <= content.length-1; i += 1) {
              if (!(content[i].constructor === Array)) {
                def.push(content[i].name);
              } else {
                // otherwise do not modify anything
                def = content;
                ctrlflag = false;
                break;
              }
            }
            if (ctrlflag) { def = [def]; }
            content = def;
          }
          $.extend(handsontable_options, options.action_definition.configuration.handsontable_options || {});
          return result_list[1].render(
            JSON.stringify(content),
            handsontable_options
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
}(window, rJS, RSVP, initGadgetMixin, loopEventListener, $));
