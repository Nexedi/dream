/*global $, rJS, RSVP, promiseEventListener, promiseReadAsText,
         initGadgetMixin, console */
(function (window, rJS, RSVP, promiseEventListener,
           promiseReadAsText, initGadgetMixin) {
  "use strict";
  // delete last session document
  function removeLastSession(gadget, name) {
    var now = new Date(), documents, element_list,
      element, i, len, promise_list;
    promise_list = [];
    gadget.aq_allDocs({
      "include_docs": true,
      "query": 'type:= "DreamLastInstance"',
      "select_list": ["title", "modified"]
    })
      .push(function (docs) {
        documents = docs;
        if (documents.data.total_rows === undefined) {
          console.log("Last instance data is undefined");
        } else if (documents.data.total_rows === 0) {
          console.log("There is no record of  DreamLastInstance type");
        } else if (documents.data.total_rows > 0) {
          //aq_remove should be performed here
          element_list = documents.data.rows;
          for (i = 0, len = element_list.length; i < len; i += 1) {
            element = element_list[i];//.nextSibling;
            promise_list[i] = gadget.aq_remove({"_id": element.id});
          }
        }
      });
    // create last instance jIO document
    promise_list[promise_list.length] = gadget.aq_post({
      title: name,
      type: "DreamLastInstance",
      format: "application/json",
      modified: now.toUTCString(),
      date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" +
        now.getDate()
    });
    return RSVP.all(promise_list);
  }
  // create a jIO document
  function createDocument(gadget, name) {
    var now = new Date(), documents, element_list,
      element, i, len, promise_list;
    promise_list = [];
    gadget.aq_allDocs({
      "include_docs": true,
      "query": 'type:= "DreamLastInstance"',
      "select_list": ["title", "modified"]
    })
      .push(function (docs) {
        documents = docs;
        if (documents.data.total_rows === undefined) {
          console.log("Last instance data is undefined");
        } else if (documents.data.total_rows === 0) {
          console.log("There is no record in the last",
                      "instance list, can proceed without deleting");
        } else if (documents.data.total_rows > 0) {
          //aq_remove should be performed here
          element_list = documents.data.rows;
          for (i = 0, len = element_list.length; i < len; i += 1) {
            element = element_list[i];//.nextSibling;
            promise_list[i] = gadget.aq_remove({"_id": element.id});
          }
        }
      });
    // Create jIO document
    promise_list[promise_list.length] = gadget.aq_post({
      title: name,
      type: "DreamInstance",
      format: "application/json",
      modified: now.toUTCString(),
      date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" +
        now.getDate()
    });
    // create last instance jIO document
    promise_list[promise_list.length] = gadget.aq_post({
      title: name,
      type: "DreamLastInstance",
      format: "application/json",
      modified: now.toUTCString(),
      date: now.getFullYear() + "-" + (now.getMonth() + 1) + "-" +
        now.getDate()
    });
    return RSVP.all(promise_list);
  }

  function waitForImport(gadget) {
    // here import definition dict from a local file
    var json_data, name;
    return new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          gadget.props.element.getElementsByClassName("import_form")[0],
          "submit",
          false
        );
      })
      .push(function (evt) {
        // Prevent double click
        evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
        var file = evt.target.dream_import.files[0];
        name = file.name;
        return promiseReadAsText(file);
      })
      .push(function (json) {
        json_data = json;
        gadget.configurationIsSet(true);
        gadget.setConfigurationDict(json_data);
        return createDocument(gadget, name);
      })
      .push(function (jio_document_list) {
        // Add JSON as attachment
        return RSVP.all([
          gadget.aq_putAttachment({
            "_id": jio_document_list[0].id,
            "_attachment": "body.json",
            "_data": json_data,
            "_mimetype": "application/json"
          }),
          gadget.aq_putAttachment({
            "_id": jio_document_list[1].id,
            "_attachment": "body.json",
            "_data": json_data,
            "_mimetype": "application/json"
          })
        ]);
      });
  }

  function waitForDefault(gadget) {
    var name = "DefaultInstance", json_data = {};
    return new RSVP.Queue()
      .push(function () {
        return promiseEventListener(
          gadget.props.element.getElementsByClassName("new_form")[0],
          "submit",
          false
        );
      })
      .push(function (evt) {
        // Prevent double click
        evt.target.getElementsByClassName("ui-btn")[0].disabled = true;
      })
      .push(function () {
        //return gadget.getConfigurationDict();
        return gadget.getDefaultConfigurationDict();
      })
      .push(function (data) {
        json_data = data || {};
        gadget.configurationIsSet(true);
        return createDocument(gadget, name);
      })
      .push(function (jio_document_list) {
        // Add JSON as attachment
        return RSVP.all([
          gadget.aq_putAttachment({
            "_id": jio_document_list[0].id,
            "_attachment": "body.json",
            "_data": JSON.stringify(json_data),
            "_mimetype": "application/json"
          }),
          gadget.aq_putAttachment({
            "_id": jio_document_list[1].id,
            "_attachment": "body.json",
            "_data": JSON.stringify(json_data),
            "_mimetype": "application/json"
          })
        ]);
      });
  }

  var gadget_klass = rJS(window);
  initGadgetMixin(gadget_klass);
  gadget_klass.declareAcquiredMethod("aq_post", "jio_post")
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("aq_allDocs", "jio_allDocs")
    .declareAcquiredMethod("aq_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("aq_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("aq_remove", "jio_remove")
    .declareAcquiredMethod("whoWantsToDisplayHome", "whoWantsToDisplayHome")
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")
    .declareAcquiredMethod("whoWantsToDisplayThisDocument",
                           "whoWantsToDisplayThisDocument")
    .declareAcquiredMethod("aq_startListenTo", "startListenTo")
    .declareAcquiredMethod("getConfigurationDict", "getConfigurationDict")
    .declareAcquiredMethod("getDefaultConfigurationDict",
                           "getDefaultConfigurationDict")
    .declareAcquiredMethod("configurationIsSet", "configurationIsSet")
    .declareAcquiredMethod("setConfigurationDict", "setConfigurationDict")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.state_parameter_dict = {};
    })
    .declareMethod("render", function () {
      var gadget, doc_list;
      gadget = this;
      doc_list = gadget.props.element.querySelector("ul.document-list");
      // helper: add options to selects
      function makeListItems(row_list) {
        var i, len, fragment, item, record, button, box, label; /*text_node*/
        fragment = document.createDocumentFragment();
        for (i = 0, len = row_list.length; i < len; i += 1) {
          record = row_list[i].doc;

          item = document.createElement("li");

          button = document.createElement("input");
          button.type = "submit";
          button.value = record.title + " (" + record.date + ")";
          /*jslint nomen: true*/
          button.setAttribute("name", "record_" + record._id);
          /*jslint nomen: false*/

          label = document.createElement("label");
          box = document.createElement("input");
          box.type = "checkbox";
          box.value = " ";
          /*jslint nomen: true*/
          box.setAttribute("name", "record_" + record._id);
          /*jslint nomen: false*/

          label.appendChild(box);
          item.appendChild(button);
          item.appendChild(label);
          fragment.appendChild(item);
        }
        return fragment;
      }
      // helper: select a configuration dictionary from a doc 
      function handleDictSelect(e) {
        //console.log('SELECTING CONFIGURATION DICTIONARY??????');
        var form, element, id, json_data;
        //prevent default
        e.preventDefault();
        form = e.target;
        element = form.querySelector("div.ui-focus");
        id = element.childNodes[1].name.replace("record_", "");
        return gadget.aq_getAttachment({
          "_id": id,
          "_attachment": "body.json"
        })
          .push(function (json) {
            json_data = json;
            gadget.configurationIsSet(true);
            gadget.setConfigurationDict(json_data);
          })
          .push(function () {
            console.log("happiness");
            return removeLastSession(gadget);
          })
          .push(function (jio_document_list) {
            // receive jio_document_list
            return gadget.aq_putAttachment({
              "_id": jio_document_list[0].id,
              "_attachment": "body.json",
              "_data": JSON.stringify(json_data),
              "_mimetype": "application/json"
            });
          })
          .push(function () {
            return gadget.whoWantsToDisplayThisDocument(id);
          })
          .push(function (url) {
            return gadget.pleaseRedirectMyHash(url);
          });
      }
      // helper: delete a doc 
      function handleDelete(e) {
        var form, element_list, promise_list, i, len,
          element, list_element, id, fragment, $doc;
        //prevent default
        e.preventDefault();
        form = e.target;
        promise_list = [];
        element_list = form.querySelectorAll("label.ui-checkbox-on");
        if (element_list) {
          for (i = 0, len = element_list.length; i < len; i += 1) {
            element = element_list[i].nextSibling;
            id = element.name.replace("record_", "");
            list_element = element.parentNode.parentNode;
            list_element.parentNode.removeChild(list_element);
            if (form.querySelector("ul").children.length === 0) {
              fragment = document.createElement("li");
              fragment.innerHTML = "No records";
              form.querySelector("ul").appendChild(fragment);
            }
            promise_list[i] = gadget.aq_remove({"_id": id});
          }
          // enhance/refresh
          $doc = $(doc_list);
          if ($doc.listview("instance")) {
            $doc.listview("refresh");
          }
        }
        return RSVP.all(promise_list);
      }
      return gadget.aq_allDocs({
        "include_docs": true,
        "query": 'type:= "DreamInstance"',
        "select_list": ["title", "modified"]
      })
        .push(function (document_list) {
          var len, data, $doc, fragment;
          data = document_list.data;
          len = data.total_rows;
          if (len > 0) {
            fragment = makeListItems(data.rows);
          } else {
            fragment = document.createElement("li");
            fragment.innerHTML = "no records";
          }
          // append
          while (doc_list.firstChild) {
            doc_list.removeChild(doc_list.firstChild);
          }
          doc_list.appendChild(fragment);
          // enhance/refresh
          $doc = $(doc_list);
          if ($doc.listview("instance")) {
            $doc.listview("refresh");
          }
        })
        .push(function () {
          if (!gadget.state_parameter_dict.bound) {
            gadget.state_parameter_dict.bound = true;
            return RSVP.all([
              gadget.aq_startListenTo(
                gadget.props.element.getElementsByTagName("FORM")[2],
                "submit",
                handleDelete
              ),
              // XXXXXXXXXXXXXXXXXXXXX
              gadget.aq_startListenTo(
                gadget.props.element.getElementsByTagName("FORM")[2],
                "submit",
                handleDictSelect
              )
            ]);
          }
        });/*.fail(console.log);*/
    })
    .declareMethod("startService", function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          return RSVP.any([ waitForImport(gadget), waitForDefault(gadget) ]);
        })
        .push(function (result) {
          return gadget.whoWantsToDisplayThisDocument(result[0].id);
        })
        .push(function (url) {
          return gadget.pleaseRedirectMyHash(url);
        });
    });

}(window, rJS, RSVP, promiseEventListener, promiseReadAsText,
  initGadgetMixin));