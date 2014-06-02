/*
* Copyright 2013, Nexedi SA
* Released under the LGPL license.
* http://www.gnu.org/licenses/lgpl.html
*/

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global jIO: true, localStorage: true, setTimeout: true,
         complex_queries: true */

/**
 * JIO Local Storage. Type = 'local'.
 * Local browser "database" storage.
 */
jIO.addStorageType('local', function (spec, my) {

  spec = spec || {};
  var that, priv, localstorage;
  that = my.basicStorage(spec, my);
  priv = {};

  /*
   * Wrapper for the localStorage used to simplify instion of any kind of
   * values
   */
  localstorage = {
    getItem: function (item) {
      var value = localStorage.getItem(item);
      return value === null ? null : JSON.parse(value);
    },
    setItem: function (item, value) {
      return localStorage.setItem(item, JSON.stringify(value));
    },
    removeItem: function (item) {
      return localStorage.removeItem(item);
    }
  };

  // attributes
  priv.username = spec.username || '';
  priv.application_name = spec.application_name || 'untitled';

  priv.localpath = 'jio/localstorage/' + priv.username + '/' +
    priv.application_name;

  // ==================== Tools ====================
  /**
   * Generate a new uuid
   * @method generateUuid
   * @return {string} The new uuid
   */
  priv.generateUuid = function () {
    var S4 = function () {
      /* 65536 */
      var i, string = Math.floor(
        Math.random() * 0x10000
      ).toString(16);
      for (i = string.length; i < 4; i += 1) {
        string = '0' + string;
      }
      return string;
    };
    return S4() + S4() + "-" + S4() + "-" + S4() + "-" + S4() + "-" + S4() +
      S4() + S4();
  };

  /**
   * Update [doc] the document object and remove [doc] keys
   * which are not in [new_doc]. It only changes [doc] keys not starting
   * with an underscore.
   * ex: doc:     {key:value1,_key:value2} with
   *     new_doc: {key:value3,_key:value4} updates
   *     doc:     {key:value3,_key:value2}.
   * @param  {object} doc The original document object.
   * @param  {object} new_doc The new document object
   */
  priv.documentObjectUpdate = function (doc, new_doc) {
    var k;
    for (k in doc) {
      if (doc.hasOwnProperty(k)) {
        if (k[0] !== '_') {
          delete doc[k];
        }
      }
    }
    for (k in new_doc) {
      if (new_doc.hasOwnProperty(k)) {
        if (k[0] !== '_') {
          doc[k] = new_doc[k];
        }
      }
    }
  };

  /**
   * Checks if an object has no enumerable keys
   * @method objectIsEmpty
   * @param  {object} obj The object
   * @return {boolean} true if empty, else false
   */
  priv.objectIsEmpty = function (obj) {
    var k;
    for (k in obj) {
      if (obj.hasOwnProperty(k)) {
        return false;
      }
    }
    return true;
  };

  // ===================== overrides ======================
  that.specToStore = function () {
    return {
      "application_name": priv.application_name,
      "username": priv.username
    };
  };

  that.validateState = function () {
    if (typeof priv.username === "string" && priv.username !== '') {
      return '';
    }
    return 'Need at least one parameter: "username".';
  };

  // ==================== commands ====================
  /**
   * Create a document in local storage.
   * @method post
   * @param  {object} command The JIO command
   */
  that.post = function (command) {
    setTimeout(function () {
      var doc, doc_id = command.getDocId();
      if (!doc_id) {
        doc_id = priv.generateUuid();
      }
      doc = localstorage.getItem(priv.localpath + "/" + doc_id);
      if (doc === null) {
        doc = command.cloneDoc();
        doc._id = doc_id;
        // the document does not exist
        localstorage.setItem(priv.localpath + "/" + doc_id,
          doc);
        that.success({
          "ok": true,
          "id": doc_id
        });
      } else {
        // the document already exists
        that.error({
          "status": 409,
          "statusText": "Conflicts",
          "error": "conflicts",
          "message": "Cannot create a new document",
          "reason": "Document already exists"
        });
      }
    });
  };

  /**
   * Create or update a document in local storage.
   * @method put
   * @param  {object} command The JIO command
   */
  that.put = function (command) {
    setTimeout(function () {
      var doc;
      doc = localstorage.getItem(priv.localpath + "/" + command.getDocId());
      if (doc === null) {
        //  the document does not exist
        doc = command.cloneDoc();
      } else {
        // the document already exists
        priv.documentObjectUpdate(doc, command.cloneDoc());
      }
      // write
      localstorage.setItem(priv.localpath + "/" + command.getDocId(), doc);
      that.success({
        "ok": true,
        "id": command.getDocId()
      });
    });
  };

  /**
   * Add an attachment to a document
   * @method  putAttachment
   * @param  {object} command The JIO command
   */
  that.putAttachment = function (command) {
    setTimeout(function () {
      var doc;
      doc = localstorage.getItem(priv.localpath + "/" + command.getDocId());
      if (doc === null) {
        //  the document does not exist
        that.error({
          "status": 404,
          "statusText": "Not Found",
          "error": "not_found",
          "message": "Impossible to add attachment",
          "reason": "Document not found"
        });
        return;
      }

      // the document already exists
      doc._attachments = doc._attachments || {};
      doc._attachments[command.getAttachmentId()] = {
        "content_type": command.getAttachmentMimeType(),
        "digest": "md5-" + command.md5SumAttachmentData(),
        "length": command.getAttachmentLength()
      };

      // upload data
      localstorage.setItem(priv.localpath + "/" + command.getDocId() + "/" +
        command.getAttachmentId(),
        command.getAttachmentData());
      // write document
      localstorage.setItem(priv.localpath + "/" + command.getDocId(), doc);
      that.success({
        "ok": true,
        "id": command.getDocId(),
        "attachment": command.getAttachmentId()
      });
    });
  };

  /**
   * Get a document
   * @method get
   * @param  {object} command The JIO command
   */
  that.get = function (command) {
    setTimeout(function () {
      var doc = localstorage.getItem(priv.localpath + "/" + command.getDocId());
      if (doc !== null) {
        that.success(doc);
      } else {
        that.error({
          "status": 404,
          "statusText": "Not Found",
          "error": "not_found",
          "message": "Cannot find the document",
          "reason": "Document does not exist"
        });
      }
    });
  };

  /**
   * Get a attachment
   * @method getAttachment
   * @param  {object} command The JIO command
   */
  that.getAttachment = function (command) {
    setTimeout(function () {
      var doc = localstorage.getItem(priv.localpath + "/" + command.getDocId() +
                                     "/" + command.getAttachmentId());
      if (doc !== null) {
        that.success(doc);
      } else {
        that.error({
          "status": 404,
          "statusText": "Not Found",
          "error": "not_found",
          "message": "Cannot find the attachment",
          "reason": "Attachment does not exist"
        });
      }
    });
  };

  /**
   * Remove a document
   * @method remove
   * @param  {object} command The JIO command
   */
  that.remove = function (command) {
    setTimeout(function () {
      var doc, i, attachment_list;
      doc = localstorage.getItem(priv.localpath + "/" + command.getDocId());
      attachment_list = [];
      if (doc !== null && typeof doc === "object") {
        if (typeof doc._attachments === "object") {
          // prepare list of attachments
          for (i in doc._attachments) {
            if (doc._attachments.hasOwnProperty(i)) {
              attachment_list.push(i);
            }
          }
        }
      } else {
        return that.error({
          "status": 404,
          "statusText": "Not Found",
          "error": "not_found",
          "message": "Document not found",
          "reason": "missing"
        });
      }
      localstorage.removeItem(priv.localpath + "/" + command.getDocId());
      // delete all attachments
      for (i = 0; i < attachment_list.length; i += 1) {
        localstorage.removeItem(priv.localpath + "/" + command.getDocId() +
                                "/" + attachment_list[i]);
      }
      that.success({
        "ok": true,
        "id": command.getDocId()
      });
    });
  };

  /**
   * Remove an attachment
   * @method removeAttachment
   * @param  {object} command The JIO command
   */
  that.removeAttachment = function (command) {
    setTimeout(function () {
      var doc, error, i, attachment_list;
      error = function (word) {
        that.error({
          "status": 404,
          "statusText": "Not Found",
          "error": "not_found",
          "message": word + " not found",
          "reason": "missing"
        });
      };
      doc = localstorage.getItem(priv.localpath + "/" + command.getDocId());
      // remove attachment from document
      if (doc !== null && typeof doc === "object" &&
          typeof doc._attachments === "object") {
        if (typeof doc._attachments[command.getAttachmentId()] ===
            "object") {
          delete doc._attachments[command.getAttachmentId()];
          if (priv.objectIsEmpty(doc._attachments)) {
            delete doc._attachments;
          }
          localstorage.setItem(priv.localpath + "/" + command.getDocId(),
                               doc);
          localstorage.removeItem(priv.localpath + "/" + command.getDocId() +
                                  "/" + command.getAttachmentId());
          that.success({
            "ok": true,
            "id": command.getDocId(),
            "attachment": command.getAttachmentId()
          });
        } else {
          error("Attachment");
        }
      } else {
        error("Document");
      }
    });
  };

  /**
   * Get all filenames belonging to a user from the document index
   * @method allDocs
   * @param  {object} command The JIO command
   */
  that.allDocs = function (command) {
    var i, row, path_re, rows = [], document_list = [], option, document_object;
    path_re = new RegExp(
      "^" + complex_queries.stringEscapeRegexpCharacters(priv.localpath) +
        "/[^/]+$"
    );
    option = command.cloneOption();
    if (typeof complex_queries !== "object" ||
        (option.query === undefined && option.sort_on === undefined &&
         option.select_list === undefined &&
         option.include_docs === undefined)) {
      rows = [];
      for (i in localStorage) {
        if (localStorage.hasOwnProperty(i)) {
          // filter non-documents
          if (path_re.test(i)) {
            row = { value: {} };
            row.id = i.split('/').slice(-1)[0];
            row.key = row.id;
            if (command.getOption('include_docs')) {
              row.doc = JSON.parse(localStorage.getItem(i));
            }
            rows.push(row);
          }
        }
      }
      that.success({"rows": rows, "total_rows": rows.length});
    } else {
      // create complex query object from returned results
      for (i in localStorage) {
        if (localStorage.hasOwnProperty(i)) {
          if (path_re.test(i)) {
            document_list.push(localstorage.getItem(i));
          }
        }
      }
      option.select_list = option.select_list || [];
      option.select_list.push("_id");
      if (option.include_docs === true) {
        document_object = {};
        document_list.forEach(function (meta) {
          document_object[meta._id] = meta;
        });
      }
      complex_queries.QueryFactory.create(option.query || "").
        exec(document_list, option);
      document_list = document_list.map(function (value) {
        var o = {
          "id": value._id,
          "key": value._id
        };
        if (option.include_docs === true) {
          o.doc = document_object[value._id];
          delete document_object[value._id];
        }
        delete value._id;
        o.value = value;
        return o;
      });
      that.success({"total_rows": document_list.length,
                    "rows": document_list});
    }
  };

  return that;
});
