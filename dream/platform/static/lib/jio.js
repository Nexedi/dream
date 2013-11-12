/*
* Copyright 2013, Nexedi SA
* Released under the LGPL license.
* http://www.gnu.org/licenses/lgpl.html
*/

// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports, require('md5'));
  }
  window.jIO = {};
  module(window.jIO, {hex_md5: hex_md5});
}(['exports', 'md5'], function (exports, md5) {
  "use strict";

  var localstorage, hex_md5 = md5.hex_md5;
  if (typeof localStorage !== "undefined") {
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
      },
      clone: function () {
        return JSON.parse(JSON.stringify(localStorage));
      }
    };
  } else {
    (function () {
      var pseudo_localStorage = {};
      localstorage = {
        getItem: function (item) {
          var value = pseudo_localStorage[item];
          return value === undefined ? null : JSON.parse(value);
        },
        setItem: function (item, value) {
          pseudo_localStorage[item] = JSON.stringify(value);
        },
        removeItem: function (item) {
          delete pseudo_localStorage[item];
        },
        clone: function () {
          return JSON.parse(JSON.stringify(pseudo_localStorage));
        }
      };
    }());
  }
/*jslint indent:2, maxlen: 80, sloppy: true */
var jioException = function (spec, my) {
  var that = {};
  spec = spec || {};
  my = my || {};
  that.name = 'jioException';
  that.message = spec.message || 'Unknown Reason.';
  that.toString = function () {
    return that.name + ': ' + that.message;
  };
  return that;
};

var invalidCommandState = function (spec, my) {
  var that = jioException(spec, my), command = spec.command;
  spec = spec || {};
  that.name = 'invalidCommandState';
  that.toString = function () {
    return that.name + ': ' +
      command.getLabel() + ', ' + that.message;
  };
  return that;
};

var invalidStorage = function (spec, my) {
  var that = jioException(spec, my), type = spec.storage.getType();
  spec = spec || {};
  that.name = 'invalidStorage';
  that.toString = function () {
    return that.name + ': ' +
      'Type "' + type + '", ' + that.message;
  };
  return that;
};

var invalidStorageType = function (spec, my) {
  var that = jioException(spec, my), type = spec.type;
  that.name = 'invalidStorageType';
  that.toString = function () {
    return that.name + ': ' +
      type + ', ' + that.message;
  };
  return that;
};

var jobNotReadyException = function (spec, my) {
  var that = jioException(spec, my);
  that.name = 'jobNotReadyException';
  return that;
};

var tooMuchTriesJobException = function (spec, my) {
  var that = jioException(spec, my);
  that.name = 'tooMuchTriesJobException';
  return that;
};

var invalidJobException = function (spec, my) {
  var that = jioException(spec, my);
  that.name = 'invalidJobException';
  return that;
};
var jio = function(spec) {
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true, jobManager: true, job: true */
var storage = function (spec, my) {
  var that = {}, priv = {};
  spec = spec || {};
  my = my || {};
  // Attributes //
  priv.type = spec.type || '';

  // Methods //
  Object.defineProperty(that, "getType", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return priv.type;
    }
  });

  /**
   * Execute the command on this storage.
   * @method execute
   * @param  {object} command The command
   */
  that.execute = function (command) {
    that.success = command.success;
    that.error   = command.error;
    that.retry   = command.retry;
    that.end     = command.end;
    if (that.validate(command)) {
      command.executeOn(that);
    }
  };

  /**
   * Override this function to validate specifications.
   * @method isValid
   * @return {boolean} true if ok, else false.
   */
  that.isValid = function () {
    return true;
  };

  that.validate = function () {
    var mess = that.validateState();
    if (mess) {
      that.error({
        "status": 0,
        "statusText": "Invalid Storage",
        "error": "invalid_storage",
        "message": mess,
        "reason": mess
      });
      return false;
    }
    return true;
  };

  /**
   * Returns a serialized version of this storage.
   * @method serialized
   * @return {object} The serialized storage.
   */
  that.serialized = function () {
    var o = that.specToStore() || {};
    o.type = that.getType();
    return o;
  };

  /**
   * Returns an object containing spec to store on localStorage, in order to
   * be restored later if something wrong happen.
   * Override this method!
   * @method specToStore
   * @return {object} The spec to store
   */
  that.specToStore = function () {
    return {};
  };

  /**
   * Validate the storage state. It returns a empty string all is ok.
   * @method validateState
   * @return {string} empty: ok, else error message.
   */
  that.validateState = function () {
    return '';
  };

  that.post = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"Post\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.put = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"Put\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.putAttachment = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"PutAttachment\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.get = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"Get\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.allDocs = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"AllDocs\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.remove = function () {
    setTimeout(function () {
      that.error({
        "status": 0,
        "statusText": "Not Implemented",
        "error": "not_implemented",
        "message": "\"Remove\" command is not implemented",
        "reason": "Command not implemented"
      });
    });
  };

  that.check = function (command) {
    setTimeout(function () {
      that.success({"ok": true, "id": command.getDocId()});
    });
  };

  that.repair = function (command) {
    setTimeout(function () {
      that.success({"ok": true, "id": command.getDocId()});
    });
  };

  that.success = function () {};
  that.retry   = function () {};
  that.error   = function () {};
  that.end     = function () {};  // terminate the current job.

  priv.newCommand = function (method, spec) {
    var o = spec || {};
    o.label = method;
    return command(o, my);
  };

  priv.storage = my.storage;
  delete my.storage;

  that.addJob = function (method, storage_spec, doc, option, success, error) {
    var command_opt = {
      doc: doc,
      options: option,
      callbacks: {success: success, error: error}
    };
    jobManager.addJob(job({
      storage: priv.storage(storage_spec || {}),
      command: priv.newCommand(method, command_opt)
    }, my));
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var allDocsCommand = function (spec, my) {
  var that = command(spec, my);

  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'allDocs';
  };

  that.executeOn = function (storage) {
    storage.allDocs(that);
  };

  that.canBeRestored = function () {
    return false;
  };

  that.validateState = function () {
    return true;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var checkCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};

  // Methods //
  that.getLabel = function () {
    return 'check';
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
        "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    return true;
  };

  that.executeOn = function (storage) {
    storage.check(that);
  };

  that.canBeRestored = function () {
    return false;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global postCommand: true, putCommand: true, getCommand: true,
         removeCommand: true, allDocsCommand: true,
         getAttachmentCommand: true, removeAttachmentCommand: true,
         putAttachmentCommand: true, failStatus: true, doneStatus: true,
         checkCommand: true, repairCommand: true,
         hex_md5: true */
var command = function (spec, my) {
  var that = {},
    priv = {};

  spec = spec || {};
  my = my || {};

  priv.commandlist = {
    'post': postCommand,
    'put': putCommand,
    'get': getCommand,
    'remove': removeCommand,
    'allDocs': allDocsCommand,
    'getAttachment': getAttachmentCommand,
    'putAttachment': putAttachmentCommand,
    'removeAttachment': removeAttachmentCommand,
    'check': checkCommand,
    'repair': repairCommand
  };
  // creates the good command thanks to his label
  if (spec.label && priv.commandlist[spec.label]) {
    priv.label = spec.label;
    delete spec.label;
    return priv.commandlist[priv.label](spec, my);
  }

  priv.tried = 0;
  priv.doc = spec.doc || {};
  if (typeof priv.doc !== "object") {
    priv.doc = {
      "_id": priv.doc.toString()
    };
  }
  priv.option = spec.options || {};
  priv.callbacks = spec.callbacks || {};
  priv.success = [priv.callbacks.success || function () {}];
  priv.error = [priv.callbacks.error || function () {}];
  priv.retry = function () {
    that.error({
      status: 13,
      statusText: 'Fail Retry',
      error: 'fail_retry',
      message: 'Impossible to retry.',
      reason: 'Impossible to retry.'
    });
  };
  priv.end = function () {};
  priv.on_going = false;

  // Methods //
  /**
   * Returns a serialized version of this command.
   * @method serialized
   * @return {object} The serialized command.
   */
  that.serialized = function () {
    var o = {};
    o.label = that.getLabel();
    o.tried = priv.tried;
    o.doc = that.cloneDoc();
    o.option = that.cloneOption();
    return o;
  };

  /**
   * Returns the label of the command.
   * @method getLabel
   * @return {string} The label.
   */
  that.getLabel = function () {
    return 'command';
  };

  /**
   * Gets the document id
   * @method getDocId
   * @return {string} The document id
   */
  that.getDocId = function () {
    return priv.doc._id;
  };

  /**
   * Gets the attachment id
   * @method getAttachmentId
   * @return {string} The attachment id
   */
  that.getAttachmentId = function () {
    return priv.doc._attachment;
  };

  /**
   * Returns the data of the attachment
   * @method getAttachmentData
   * @return {string} The data
   */
  that.getAttachmentData = function () {
    return priv.doc._data || "";
  };

  /**
   * Returns the data length of the attachment
   * @method getAttachmentLength
   * @return {number} The length
   */
  that.getAttachmentLength = function () {
    return (priv.doc._data || "").length;
  };

  /**
   * Returns the mimetype of the attachment
   * @method getAttachmentMimeType
   * @return {string} The mimetype
   */
  that.getAttachmentMimeType = function () {
    return priv.doc._mimetype;
  };

  /**
   * Generate the md5sum of the attachment data
   * @method md5SumAttachmentData
   * @return {string} The md5sum
   */
  that.md5SumAttachmentData = function () {
    return hex_md5(priv.doc._data || "");
  };

  /**
   * Returns an information about the document.
   * @method getDocInfo
   * @param  {string} infoname The info name.
   * @return The info value.
   */
  that.getDocInfo = function (infoname) {
    return priv.doc[infoname];
  };

  /**
   * Returns the value of an option.
   * @method getOption
   * @param  {string} optionname The option name.
   * @return The option value.
   */
  that.getOption = function (optionname) {
    return priv.option[optionname];
  };

  /**
   * Validates the storage.
   * @param  {object} storage The storage.
   */
  that.validate = function (storage) {
    if (typeof priv.doc._id === "string" && priv.doc._id === "") {
      that.error({
        "status": 21,
        "statusText": "Invalid Document Id",
        "error": "invalid_document_id",
        "message": "The document id is invalid",
        "reason": "empty"
      });
      return false;
    }
    if (!that.validateState()) {
      return false;
    }
    return storage.validate();
  };

  /*
   * Extend this function
   */
  that.validateState = function () {
    return true;
  };

    /**
   * Check if the command can be retried.
   * @method canBeRetried
   * @return {boolean} The result
   */
  that.canBeRetried = function () {
    return (priv.option.max_retry === undefined ||
      priv.option.max_retry === 0 ||
        priv.tried < priv.option.max_retry);
  };

  /**
   * Gets the number time the command has been tried.
   * @method getTried
   * @return {number} The number of time the command has been tried
   */
  that.getTried = function () {
    return priv.tried;
  };

  /**
   * Delegate actual excecution the storage.
   * @param {object} storage The storage.
   */
  that.execute = function (storage) {
    if (!priv.on_going) {
      if (that.validate(storage)) {
        priv.tried += 1;
        priv.on_going = true;
        storage.execute(that);
      }
    }
  };
  /**
   * Execute the good method from the storage.
   * Override this function.
   * @method executeOn
   * @param  {object} storage The storage.
   */
  that.executeOn = function (storage) {};
  that.success = function (return_value) {
    var i;
    priv.on_going = false;
    for (i = 0; i < priv.success.length; i += 1) {
      priv.success[i](return_value);
    }
    priv.end(doneStatus());
    priv.success = [];
    priv.error = [];
  };
  that.retry = function (return_error) {
    priv.on_going = false;
    if (that.canBeRetried()) {
      priv.retry();
    } else {
      that.error(return_error);
    }
  };
  that.error = function (return_error) {
    var i;
    priv.on_going = false;
    for (i = 0; i < priv.error.length; i += 1) {
      priv.error[i](return_error);
    }
    priv.end(failStatus());
    priv.success = [];
    priv.error = [];
  };
  that.end = function () {
    priv.end(doneStatus());
  };
  that.addCallbacks = function (success, error) {
    if (arguments.length > 1) {
      priv.success.push(success || function () {});
      priv.error.push(error || function () {});
    } else {
      priv.success.push(function (response) {
        (success || function () {})(undefined, response);
      });
      priv.error.push(function (err) {
        (success || function () {})(err, undefined);
      });
    }
  };
  that.onSuccessDo = function (fun) {
    if (fun) {
      priv.success = fun;
    } else {
      return priv.success;
    }
  };
  that.onErrorDo = function (fun) {
    if (fun) {
      priv.error = fun;
    } else {
      return priv.error;
    }
  };
  that.onEndDo = function (fun) {
    priv.end = fun;
  };
  that.onRetryDo = function (fun) {
    priv.retry = fun;
  };
  /**
   * Is the command can be restored by another JIO : yes.
   * @method canBeRestored
   * @return {boolean} true
   */
  that.canBeRestored = function () {
    return true;
  };
  /**
   * Clones the command and returns it.
   * @method clone
   * @return {object} The cloned command.
   */
  that.clone = function () {
    return command(that.serialized(), my);
  };
  /**
   * Clones the command options and returns the clone version.
   * @method cloneOption
   * @return {object} The clone of the command options.
   */
  that.cloneOption = function () {
    return JSON.parse(JSON.stringify(priv.option));
  };
  /**
   * Clones the document and returns the clone version.
   * @method cloneDoc
   * @return {object} The clone of the document.
   */
  that.cloneDoc = function () {
    return JSON.parse(JSON.stringify(priv.doc));
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var getAttachmentCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'getAttachment';
  };

  that.executeOn = function (storage) {
    storage.getAttachment(that);
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
          "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    if (typeof that.getAttachmentId() !== "string") {
      that.error({
        "status": 22,
        "statusText": "Attachment Id Required",
        "error": "attachment_id_required",
        "message": "The attachment id must be set",
        "reason": "Attachment id not set"
      });
      return false;
    }
    if (that.getAttachmentId() === "") {
      that.error({
        "status": 23,
        "statusText": "Invalid Attachment Id",
        "error": "invalid_attachment_id",
        "message": "The attachment id must not be an empty string",
        "reason": "Attachment id is empty"
      });
    }
    return true;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var getCommand = function (spec, my) {
  var that = command(spec, my);

  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'get';
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" &&
      that.getDocId() !== "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    return true;
  };

  that.executeOn = function (storage) {
    storage.get(that);
  };

  that.canBeRestored = function () {
    return false;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var postCommand = function (spec, my) {
  var that = command(spec, my);

  spec = spec || {};
  my = my || {};

  // Methods //
  that.getLabel = function () {
    return 'post';
  };

  that.validateState = function () {
    return true;
  };
  that.executeOn = function (storage) {
    storage.post(that);
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var putAttachmentCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'putAttachment';
  };

  that.executeOn = function (storage) {
    storage.putAttachment(that);
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
          "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    if (typeof that.getAttachmentId() !== "string") {
      that.error({
        "status": 22,
        "statusText": "Attachment Id Required",
        "error": "attachment_id_required",
        "message": "The attachment id must be set",
        "reason": "Attachment id not set"
      });
      return false;
    }
    if (that.getAttachmentId() === "") {
      that.error({
        "status": 23,
        "statusText": "Invalid Attachment Id",
        "error": "invalid_attachment_id",
        "message": "The attachment id must not be an empty string",
        "reason": "Attachment id is empty"
      });
    }
    return true;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var putCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};

  // Methods //
  that.getLabel = function () {
    return 'put';
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
        "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    return true;
  };
  that.executeOn = function (storage) {
    storage.put(that);
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var removeAttachmentCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'removeAttachment';
  };

  that.executeOn = function (storage) {
    storage.removeAttachment(that);
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
          "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    if (typeof that.getAttachmentId() !== "string") {
      that.error({
        "status": 22,
        "statusText": "Attachment Id Required",
        "error": "attachment_id_required",
        "message": "The attachment id must be set",
        "reason": "Attachment id not set"
      });
      return false;
    }
    if (that.getAttachmentId() === "") {
      that.error({
        "status": 23,
        "statusText": "Invalid Attachment Id",
        "error": "invalid_attachment_id",
        "message": "The attachment id must not be an empty string",
        "reason": "Attachment id is empty"
      });
    }
    return true;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var removeCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'remove';
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
        "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    return true;
  };

  that.executeOn = function (storage) {
    storage.remove(that);
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global command: true */
var repairCommand = function (spec, my) {
  var that = command(spec, my);
  spec = spec || {};
  my = my || {};

  // Methods //
  that.getLabel = function () {
    return 'repair';
  };

  that.validateState = function () {
    if (!(typeof that.getDocId() === "string" && that.getDocId() !==
        "")) {
      that.error({
        "status": 20,
        "statusText": "Document Id Required",
        "error": "document_id_required",
        "message": "The document id is not provided",
        "reason": "Document id is undefined"
      });
      return false;
    }
    return true;
  };
  that.executeOn = function (storage) {
    storage.repair(that);
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true */
var doneStatus = function (spec, my) {
  var that = jobStatus(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'done';
  };

  that.canStart = function () {
    return false;
  };
  that.canRestart = function () {
    return false;
  };

  that.isDone = function () {
    return true;
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true */
var failStatus = function (spec, my) {
  var that = jobStatus(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'fail';
  };

  that.canStart = function () {
    return false;
  };
  that.canRestart = function () {
    return true;
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true */
var initialStatus = function (spec, my) {
  var that = jobStatus(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return "initial";
  };

  that.canStart = function () {
    return true;
  };
  that.canRestart = function () {
    return true;
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true */
var jobStatus = function (spec, my) {
  var that = {};
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'job status';
  };

  that.canStart = function () {};
  that.canRestart = function () {};

  that.serialized = function () {
    return {"label": that.getLabel()};
  };

  that.isWaitStatus = function () {
    return false;
  };

  that.isDone = function () {
    return false;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true */
var onGoingStatus = function (spec, my) {
  var that = jobStatus(spec, my);
  spec = spec || {};
  my = my || {};
  // Attributes //
  // Methods //
  that.getLabel = function () {
    return 'on going';
  };

  that.canStart = function () {
    return false;
  };
  that.canRestart = function () {
    return false;
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobStatus: true, jobManager: true */
var waitStatus = function (spec, my) {
  var that = jobStatus(spec, my), priv = {};
  spec = spec || {};
  my = my || {};
  // Attributes //
  priv.job_id_array = spec.job_id_array || [];
  priv.threshold = 0;

  // Methods //
  /**
   * Returns the label of this status.
   * @method getLabel
   * @return {string} The label: 'wait'.
   */
  that.getLabel = function () {
    return 'wait';
  };

  /**
   * Refresh the job id array to wait.
   * @method refreshJobIdArray
   */
  priv.refreshJobIdArray = function () {
    var tmp_job_id_array = [], i;
    for (i = 0; i < priv.job_id_array.length; i += 1) {
      if (jobManager.jobIdExists(priv.job_id_array[i])) {
        tmp_job_id_array.push(priv.job_id_array[i]);
      }
    }
    priv.job_id_array = tmp_job_id_array;
  };

  /**
   * The status must wait for the job end before start again.
   * @method waitForJob
   * @param  {object} job The job to wait for.
   */
  that.waitForJob = function (job) {
    var i;
    for (i = 0; i < priv.job_id_array.length; i += 1) {
      if (priv.job_id_array[i] === job.getId()) {
        return;
      }
    }
    priv.job_id_array.push(job.getId());
  };

  /**
   * The status stops to wait for this job.
   * @method dontWaitForJob
   * @param  {object} job The job to stop waiting for.
   */
  that.dontWaitForJob = function (job) {
    var i, tmp_job_id_array = [];
    for (i = 0; i < priv.job_id_array.length; i += 1) {
      if (priv.job_id_array[i] !== job.getId()) {
        tmp_job_id_array.push(priv.job_id_array[i]);
      }
    }
    priv.job_id_array = tmp_job_id_array;
  };

  /**
   * The status must wait for some milliseconds.
   * @method waitForTime
   * @param  {number} ms The number of milliseconds
   */
  that.waitForTime = function (ms) {
    priv.threshold = Date.now() + ms;
  };

  /**
   * The status stops to wait for some time.
   * @method stopWaitForTime
   */
  that.stopWaitForTime = function () {
    priv.threshold = 0;
  };

  that.canStart = function () {
    priv.refreshJobIdArray();
    return (priv.job_id_array.length === 0 && Date.now() >= priv.threshold);
  };
  that.canRestart = function () {
    return that.canStart();
  };

  that.serialized = function () {
    return {
      "label": that.getLabel(),
      "waitfortime": priv.threshold,
      "waitforjob": priv.job_id_array
    };
  };

  /**
   * Checks if this status is waitStatus
   * @method isWaitStatus
   * @return {boolean} true
   */
  that.isWaitStatus = function () {
    return true;
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global jobIdHandler: true, initialStatus: true, invalidJobException: true,
waitStatus: true, failStatus: true, tooMuchTriesJobException: true,
jobManager: true, jobNotReadyException: true, onGoingStatus: true */
var job = function (spec) {
  var that = {},
    priv = {};

  spec = spec || {};

  priv.id = jobIdHandler.nextId();
  priv.command = spec.command;
  priv.storage = spec.storage;
  priv.status = initialStatus();
  priv.date = new Date();

  // Initialize //
  if (!priv.storage) {
    throw invalidJobException({
      job: that,
      message: 'No storage set'
    });
  }
  if (!priv.command) {
    throw invalidJobException({
      job: that,
      message: 'No command set'
    });
  }
  // Methods //
  /**
  * Returns the job command.
  * @method getCommand
  * @return {object} The job command.
  */
  that.getCommand = function () {
    return priv.command;
  };

  that.getStatus = function () {
    return priv.status;
  };

  that.getId = function () {
    return priv.id;
  };

  that.getStorage = function () {
    return priv.storage;
  };

  that.getDate = function () {
    return priv.date;
  };

  /**
  * Checks if the job is ready.
  * @method isReady
  * @return {boolean} true if ready, else false.
  */
  that.isReady = function () {
    if (priv.command.getTried() === 0) {
      return priv.status.canStart();
    }
    return priv.status.canRestart();
  };

  /**
    * Returns a serialized version of this job.
    * @method serialized
    * @return {object} The serialized job.
    */
  that.serialized = function () {
    return {
      id: priv.id,
      date: priv.date.getTime(),
      status: priv.status.serialized(),
      command: priv.command.serialized(),
      storage: priv.storage.serialized()
    };
  };

  /**
  * Tells the job to wait for another one.
  * @method waitForJob
  * @param  {object} job The job to wait for.
  */
  that.waitForJob = function (job) {
    if (priv.status.getLabel() !== 'wait') {
      priv.status = waitStatus({});
    }
    priv.status.waitForJob(job);
  };

  /**
  * Tells the job to do not wait for a job.
  * @method dontWaitForJob
  * @param  {object} job The other job.
  */
  that.dontWaitFor = function (job) {
    if (priv.status.getLabel() === 'wait') {
      priv.status.dontWaitForJob(job);
    }
  };

  /**
  * Tells the job to wait for a while.
  * @method waitForTime
  * @param  {number} ms Time to wait in millisecond.
  */
  that.waitForTime = function (ms) {
    if (priv.status.getLabel() !== 'wait') {
      priv.status = waitStatus({});
    }
    priv.status.waitForTime(ms);
  };

  /**
  * Tells the job to do not wait for a while anymore.
  * @method stopWaitForTime
  */
  that.stopWaitForTime = function () {
    if (priv.status.getLabel() === 'wait') {
      priv.status.stopWaitForTime();
    }
  };

  that.eliminated = function () {
    priv.command.error({
      status: 10,
      statusText: 'Stopped',
      error: 'stopped',
      message: 'This job has been stopped by another one.',
      reason: 'this job has been stopped by another one'
    });
  };

  that.notAccepted = function () {
    priv.command.onEndDo(function () {
      priv.status = failStatus();
      jobManager.terminateJob(that);
    });
    priv.command.error({
      status: 11,
      statusText: 'Not Accepted',
      error: 'not_accepted',
      message: 'This job is already running.',
      reason: 'this job is already running'
    });
  };

  /**
  * Updates the date of the job with the another one.
  * @method update
  * @param  {object} job The other job.
  */
  that.update = function (job) {
    priv.command.addCallbacks(job.getCommand().onSuccessDo()[0],
                              job.getCommand().onErrorDo()[0]);
    priv.date = new Date(job.getDate().getTime());
  };

  /**
  * Executes this job.
  * @method execute
  */
  that.execute = function () {
    if (!that.getCommand().canBeRetried()) {
      throw tooMuchTriesJobException({
        job: that,
        message: 'The job was invoked too much time.'
      });
    }
    if (!that.isReady()) {
      throw jobNotReadyException({
        job: that,
        message: 'Can not execute this job.'
      });
    }
    priv.status = onGoingStatus();
    priv.command.onRetryDo(function () {
      var ms = priv.command.getTried();
      ms = ms * ms * 200;
      if (ms > 10000) {
        ms = 10000;
      }
      that.waitForTime(ms);
    });
    priv.command.onEndDo(function (status) {
      priv.status = status;
      jobManager.terminateJob(that);
    });
    priv.command.execute(priv.storage);
  };
  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global announcement: true */
var announcement = function (spec, my) {
  var that = {},
    callback_a = [],
    announcer = spec.announcer || {};

  spec = spec || {};
  my = my || {};

  // Methods //
  that.add = function (callback) {
    callback_a.push(callback);
  };

  that.remove = function (callback) {
    var i, tmp_callback_a = [];
    for (i = 0; i < callback_a.length; i += 1) {
      if (callback_a[i] !== callback) {
        tmp_callback_a.push(callback_a[i]);
      }
    }
    callback_a = tmp_callback_a;
  };

  that.register = function () {
    announcer.register(that);
  };

  that.unregister = function () {
    announcer.unregister(that);
  };

  that.trigger = function (args) {
    var i;
    for (i = 0; i < callback_a.length; i += 1) {
      callback_a[i].apply(null, args);
    }
  };

  return that;
};
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global localstorage: true, setInterval: true, clearInterval: true */
var activityUpdater = (function (spec, my) {
  var that = {}, priv = {};
  spec = spec || {};
  my = my || {};

  priv.id = spec.id || 0;
  priv.interval = 400;
  priv.interval_id = null;

  // Methods //
  /**
   * Update the last activity date in the localStorage.
   * @method touch
   */
  priv.touch = function () {
    localstorage.setItem('jio/id/' + priv.id, Date.now());
  };

  /**
   * Sets the jio id into the activity.
   * @method setId
   * @param  {number} id The jio id.
   */
  that.setId = function (id) {
    priv.id = id;
  };

  /**
   * Sets the interval delay between two updates.
   * @method setIntervalDelay
   * @param  {number} ms In milliseconds
   */
  that.setIntervalDelay = function (ms) {
    priv.interval = ms;
  };

  /**
   * Gets the interval delay.
   * @method getIntervalDelay
   * @return {number} The interval delay.
   */
  that.getIntervalDelay = function () {
    return priv.interval;
  };

  /**
   * Starts the activity updater. It will update regulary the last activity
   * date in the localStorage to show to other jio instance that this instance
   * is active.
   * @method start
   */
  that.start = function () {
    if (!priv.interval_id) {
      priv.touch();
      priv.interval_id = setInterval(function () {
        priv.touch();
      }, priv.interval);
    }
  };

  /**
   * Stops the activity updater.
   * @method stop
   */
  that.stop = function () {
    if (priv.interval_id !== null) {
      clearInterval(priv.interval_id);
      priv.interval_id = null;
    }
  };

  return that;
}());
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global announcement: true */
var announcer = (function (spec, my) {
  var that = {},
    announcement_o = {};
  spec = spec || {};
  my = my || {};

  // Methods //
  that.register = function (name) {
    if (!announcement_o[name]) {
      announcement_o[name] = announcement();
    }
  };

  that.unregister = function (name) {
    if (announcement_o[name]) {
      delete announcement_o[name];
    }
  };

  that.at = function (name) {
    return announcement_o[name];
  };

  that.on = function (name, callback) {
    that.register(name);
    that.at(name).add(callback);
  };

  that.trigger = function (name, args) {
    that.at(name).trigger(args);
  };

  return that;
}());
/*jslint indent: 2, maxlen: 80, sloppy: true */
var jobIdHandler = (function (spec) {
  var that = {},
    id = 0;
  spec = spec || {};

  // Methods //
  that.nextId = function () {
    id = id + 1;
    return id;
  };

  return that;
}());
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global localstorage: true, setInterval: true, clearInterval: true,
 command: true, job: true, jobRules: true */
var jobManager = (function (spec) {
  var that = {},
    job_array_name = 'jio/job_array',
    priv = {};

  spec = spec || {};
  // Attributes //
  priv.id = spec.id;
  priv.interval_id = null;
  priv.interval = 200;
  priv.job_array = [];

  // Methods //
  /**
  * Get the job array name in the localStorage
  * @method getJobArrayName
  * @return {string} The job array name
  */
  priv.getJobArrayName = function () {
    return job_array_name + '/' + priv.id;
  };

  /**
  * Returns the job array from the localStorage
  * @method getJobArray
  * @return {array} The job array.
  */
  priv.getJobArray = function () {
    return localstorage.getItem(priv.getJobArrayName()) || [];
  };

  /**
  * Does a backup of the job array in the localStorage.
  * @method copyJobArrayToLocal
  */
  priv.copyJobArrayToLocal = function () {
    var new_a = [],
      i;
    for (i = 0; i < priv.job_array.length; i += 1) {
      new_a.push(priv.job_array[i].serialized());
    }
    localstorage.setItem(priv.getJobArrayName(), new_a);
  };

  /**
  * Removes a job from the current job array.
  * @method removeJob
  * @param  {object} job The job object.
  */
  priv.removeJob = function (job) {
    var i,
      tmp_job_array = [];
    for (i = 0; i < priv.job_array.length; i += 1) {
      if (priv.job_array[i] !== job) {
        tmp_job_array.push(priv.job_array[i]);
      }
    }
    priv.job_array = tmp_job_array;
    priv.copyJobArrayToLocal();
  };

  /**
  * Sets the job manager id.
  * @method setId
  * @param  {number} id The id.
  */
  that.setId = function (id) {
    priv.id = id;
  };

  /**
  * Starts listening to the job array, executing them regulary.
  * @method start
  */
  that.start = function () {
    var i;
    if (priv.interval_id === null) {
      priv.interval_id = setInterval(function () {
        priv.restoreOldJio();
        for (i = 0; i < priv.job_array.length; i += 1) {
          that.execute(priv.job_array[i]);
        }
      }, priv.interval);
    }
  };

  /**
  * Stops listening to the job array.
  * @method stop
  */
  that.stop = function () {
    if (priv.interval_id !== null) {
      clearInterval(priv.interval_id);
      priv.interval_id = null;
      if (priv.job_array.length === 0) {
        localstorage.removeItem(priv.getJobArrayName());
      }
    }
  };

  /**
  * Try to restore an the inactive older jio instances.
  * It will restore the on going or initial jobs from their job array
  * and it will add them to this job array.
  * @method restoreOldJio
  */
  priv.restoreOldJio = function () {
    var i,
      jio_id_a;
    priv.lastrestore = priv.lastrestore || 0;
    if (priv.lastrestore > (Date.now()) - 2000) {
      return;
    }
    jio_id_a = localstorage.getItem('jio/id_array') || [];
    for (i = 0; i < jio_id_a.length; i += 1) {
      priv.restoreOldJioId(jio_id_a[i]);
    }
    priv.lastrestore = Date.now();
  };

  /**
  * Try to restore an old jio according to an id.
  * @method restoreOldJioId
  * @param  {number} id The jio id.
  */
  priv.restoreOldJioId = function (id) {
    var jio_date;
    jio_date = localstorage.getItem('jio/id/' + id) || 0;
    if (new Date(jio_date).getTime() < (Date.now() - 10000)) { // 10 sec
      priv.restoreOldJobFromJioId(id);
      priv.removeOldJioId(id);
      priv.removeJobArrayFromJioId(id);
    }
  };

  /**
  * Try to restore all jobs from another jio according to an id.
  * @method restoreOldJobFromJioId
  * @param  {number} id The jio id.
  */
  priv.restoreOldJobFromJioId = function (id) {
    var i,
      command_object,
      jio_job_array;
    jio_job_array = localstorage.getItem('jio/job_array/' + id) || [];
    for (i = 0; i < jio_job_array.length; i += 1) {
      command_object = command(jio_job_array[i].command);
      if (command_object.canBeRestored()) {
        that.addJob(job({
          storage: that.storage(jio_job_array[i].storage),
          command: command_object
        }));
      }
    }
  };
  /**
  * Removes a jio instance according to an id.
  * @method removeOldJioId
  * @param  {number} id The jio id.
  */
  priv.removeOldJioId = function (id) {
    var i,
      jio_id_array,
      new_array = [];
    jio_id_array = localstorage.getItem('jio/id_array') || [];
    for (i = 0; i < jio_id_array.length; i += 1) {
      if (jio_id_array[i] !== id) {
        new_array.push(jio_id_array[i]);
      }
    }
    localstorage.setItem('jio/id_array', new_array);
    localstorage.removeItem('jio/id/' + id);
  };
  /**
  * Removes a job array from a jio instance according to an id.
  * @method removeJobArrayFromJioId
  * @param  {number} id The jio id.
  */
  priv.removeJobArrayFromJioId = function (id) {
    localstorage.removeItem('jio/job_array/' + id);
  };
  /**
  * Executes a job.
  * @method execute
  * @param  {object} job The job object.
  */
  that.execute = function (job) {
    try {
      job.execute();
    } catch (e) {
      switch (e.name) {
      case 'jobNotReadyException':
        break; // do nothing
      case 'tooMuchTriesJobException':
        break; // do nothing
      default:
        throw e;
      }
    }
    priv.copyJobArrayToLocal();
  };
  /**
  * Checks if a job exists in the job array according to a job id.
  * @method jobIdExists
  * @param  {number} id The job id.
  * @return {boolean} true if exists, else false.
  */
  that.jobIdExists = function (id) {
    var i;
    for (i = 0; i < priv.job_array.length; i += 1) {
      if (priv.job_array[i].getId() === id) {
        return true;
      }
    }
    return false;
  };
  /**
  * Terminate a job. It only remove it from the job array.
  * @method terminateJob
  * @param  {object} job The job object
  */
  that.terminateJob = function (job) {
    priv.removeJob(job);
  };
  /**
  * Adds a job to the current job array.
  * @method addJob
  * @param  {object} job The new job.
  */
  that.addJob = function (job) {
    var result_array = that.validateJobAccordingToJobList(priv.job_array, job);
    priv.appendJob(job, result_array);
  };
  /**
  * Generate a result array containing action string to do with the good job.
  * @method validateJobAccordingToJobList
  * @param  {array} job_array A job array.
  * @param  {object} job The new job to compare with.
  * @return {array} A result array.
  */
  that.validateJobAccordingToJobList = function (job_array, job) {
    var i,
      result_array = [];
    for (i = 0; i < job_array.length; i += 1) {
      result_array.push(jobRules.validateJobAccordingToJob(job_array[i], job));
    }
    return result_array;
  };
  /**
  * It will manage the job in order to know what to do thanks to a result
  * array. The new job can be added to the job array, but it can also be
  * not accepted. It is this method which can tells jobs to wait for another
  * one, to replace one or to eliminate some while browsing.
  * @method appendJob
  * @param  {object} job The job to append.
  * @param  {array} result_array The result array.
  */
  priv.appendJob = function (job, result_array) {
    var i;
    if (priv.job_array.length !== result_array.length) {
      throw new RangeError("Array out of bound");
    }
    for (i = 0; i < result_array.length; i += 1) {
      if (result_array[i].action === 'dont accept') {
        return job.notAccepted();
      }
    }
    for (i = 0; i < result_array.length; i += 1) {
      switch (result_array[i].action) {
      case 'eliminate':
        result_array[i].job.eliminated();
        priv.removeJob(result_array[i].job);
        break;
      case 'update':
        result_array[i].job.update(job);
        priv.copyJobArrayToLocal();
        return;
      case 'wait':
        job.waitForJob(result_array[i].job);
        break;
      default:
        break;
      }
    }
    priv.job_array.push(job);
    priv.copyJobArrayToLocal();
  };
  that.serialized = function () {
    var a = [],
      i,
      job_array = priv.job_array || [];
    for (i = 0; i < job_array.length; i += 1) {
      a.push(job_array[i].serialized());
    }
    return a;
  };
  return that;
}());
/*jslint indent: 2, maxlen: 80, sloppy: true */
var jobRules = (function () {
  var that = {}, priv = {};

  priv.compare = {};
  priv.action = {};

  Object.defineProperty(that, "eliminate", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return 'eliminate';
    }
  });
  Object.defineProperty(that, "update", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return 'update';
    }
  });
  Object.defineProperty(that, "dontAccept", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return 'dont accept';
    }
  });
  Object.defineProperty(that, "wait", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return 'wait';
    }
  });
  Object.defineProperty(that, "ok", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function () {
      return 'none';
    }
  });
  that.default_action = that.ok;
  that.default_compare = function (job1, job2) {
    return job1.getId() !== job2.getId() &&
      job1.getStatus().getLabel() !== "done" &&
      job1.getStatus().getLabel() !== "fail" &&
      JSON.stringify(job1.getStorage().serialized()) ===
      JSON.stringify(job2.getStorage().serialized());
  };

  // Compare Functions //

  Object.defineProperty(that, "sameDocumentId", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      return job1.getCommand().getDocId() === job2.getCommand().getDocId();
    }
  });

  Object.defineProperty(that, "sameRevision", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      return job1.getCommand().getDocInfo("_rev") ===
        job2.getCommand().getDocInfo("_rev");
    }
  });

  Object.defineProperty(that, "sameAttachmentId", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      return job1.getCommand().getAttachmentId() ===
        job2.getCommand().getAttachmentId();
    }
  });

  Object.defineProperty(that, "sameDocument", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      return JSON.stringify(job1.getCommand().cloneDoc()) ===
        JSON.stringify(job2.getCommand().cloneDoc());
    }
  });

  Object.defineProperty(that, "sameOption", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      return JSON.stringify(job1.getCommand().cloneOption()) ===
        JSON.stringify(job2.getCommand().cloneOption());
    }
  });

  // Methods //
  /**
   * Returns an action according the jobs given in parameters.
   * @method getAction
   * @param  {object} job1 The already existant job.
   * @param  {object} job2 The job to compare with.
   * @return {string} An action string.
   */
  priv.getAction = function (job1, job2) {
    var method1, method2, tmp = priv.action, i, j, condition_list = [], res;
    method1 = job1.getCommand().getLabel();
    method2 = job2.getCommand().getLabel();
    tmp = tmp[method1] = tmp[method1] || {};
    tmp = tmp[method2] = tmp[method2] || [];
    for (i = 0; i < tmp.length; i += 1) {
      // browsing all method1 method2 rules
      condition_list = tmp[i].condition_list;
      res = true;
      for (j = 0; j < condition_list.length; j += 1) {
        // test all the rule's conditions
        if (!condition_list[j](job1, job2)) {
          res = false;
          break;
        }
      }
      if (res) {
        // if all respects condition list, then action
        return tmp[i].rule();
      }
    }
    return that.default_action();
  };

  /**
   * Checks if the two jobs are comparable.
   * @method canCompare
   * @param  {object} job1 The already existant job.
   * @param  {object} job2 The job to compare with.
   * @return {boolean} true if comparable, else false.
   */
  priv.canCompare = function (job1, job2) {
    var method1, method2;
    method1 = job1.getCommand().getLabel();
    method2 = job2.getCommand().getLabel();
    if (priv.compare[method1] && priv.compare[method1][method2]) {
      return priv.compare[method1][method2](job1, job2);
    }
    return that.default_compare(job1, job2);
  };

  /**
   * Returns an action string to show what to do if we want to add a job.
   * @method validateJobAccordingToJob
   * @param  {object} job1 The current job.
   * @param  {object} job2 The new job.
   * @return {string} The action string.
   */
  Object.defineProperty(that, "validateJobAccordingToJob", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (job1, job2) {
      if (priv.canCompare(job1, job2)) {
        return {
          action: priv.getAction(job1, job2),
          job: job1
        };
      }
      return {
        action: that.default_action(job1, job2),
        job: job1
      };
    }
  });

  /**
   * Adds a rule the action rules.
   * @method addActionRule
   * @param {string} method1 The action label from the current job.
   * @param {boolean} ongoing Is this action is on going or not?
   * @param {string} method2 The action label from the new job.
   * @param {function} rule The rule that return an action string.
   */
  Object.defineProperty(that, "addActionRule", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (method1, method2, condition_list, rule) {
      var tmp = priv.action;
      tmp = tmp[method1] = tmp[method1] || {};
      tmp = tmp[method2] = tmp[method2] || [];
      tmp.push({
        "condition_list": condition_list,
        "rule": rule
      });
    }
  });

  /**
   * Adds a rule the compare rules.
   * @method addCompareRule
   * @param {string} method1 The action label from the current job.
   * @param {string} method2 The action label from the new job.
   * @param {function} rule The rule that return a boolean
   * - true if job1 and job2 can be compared, else false.
   */
  Object.defineProperty(that, "addCompareRule", {
    configurable: false,
    enumerable: false,
    writable: false,
    value: function (method1, method2, rule) {
      priv.compare[method1] = priv.compare[method1] || {};
      priv.compare[method1][method2] = rule;
    }
  });

  ////////////////////////////////////////////////////////////////////////////
  // Adding some rules

  /*
    Rules
    original job |job to add |condition                                |action

    post          post        same doc                                  update
      "             "         same docid, same rev                      wait
      "           put                   "                                 "
      "           putA                  "                                 "
      "           remove                "                                 "
      "           removeA               "                                 "
    put           post        same docid, same rev                      wait
      "           put         same doc                                  update
      "             "         same docid, same rev                      wait
      "           putA                  "                                 "
      "           remove                "                                 "
      "           removeA               "                                 "
    putA          post        same docid, same rev                      wait
      "           put                   "                                 "
      "           putA        same doc                                  update
      "             "         same docid, same rev, same attmt          wait
      "           remove      same docid, same rev                        "
      "           removeA     same docid, same rev, same attmt            "
    remove        post        same docid, same rev                      wait
      "           put                   "                                 "
      "           putA                  "                                 "
      "           remove                "                               update
      "           removeA               "                               wait
    removeA       post        same docid, same rev                      wait
      "           put                   "                                 "
      "           putA        same docid, same rev, same attmt            "
      "           remove      same docid, same rev                        "
      "           removeA     same doc                                  update
      "           removeA     same docid, same rev, same attmt          wait
    get           get         same doc, same options                    update
    getA          getA        same doc, same options                    update
    allDocs       allDocs     same doc, same options                    update
   */

  that.addActionRule("post", "post", [that.sameDocument], that.update);
  that.addActionRule("post", "post",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("post", "put",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("post", "putAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("post", "remove",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("post", "removeAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);

  that.addActionRule("put", "post",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("put", "put", [that.sameDocument], that.update);
  that.addActionRule("put", "put",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("put", "putAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("put", "remove",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("put", "removeAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);

  that.addActionRule("putAttachment", "post",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("putAttachment", "put",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("putAttachment", "putAttachment", [that.sameDocument],
                     that.update);
  that.addActionRule("putAttachment", "putAttachment", [
    that.sameDocumentId,
    that.sameRevision,
    that.sameAttachmentId
  ], that.wait);
  that.addActionRule("putAttachment", "remove",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("putAttachment", "removeAttachment", [
    that.sameDocumentId,
    that.sameRevision,
    that.sameAttachmentId
  ], that.wait);

  that.addActionRule("remove", "post",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("remove", "put",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("remove", "putAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("remove", "remove",
                     [that.sameDocumentId, that.sameRevision], that.update);
  that.addActionRule("remove", "removeAttachment",
                     [that.sameDocumentId, that.sameRevision], that.wait);

  that.addActionRule("removeAttachment", "post",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("removeAttachment", "put",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("removeAttachment", "putAttachment", [
    that.sameDocumentId,
    that.sameRevision,
    that.sameAttachmentId
  ], that.wait);
  that.addActionRule("removeAttachment", "remove",
                     [that.sameDocumentId, that.sameRevision], that.wait);
  that.addActionRule("removeAttachment", "removeAttachment",
                     [that.sameDocument], that.update);
  that.addActionRule("removeAttachment", "removeAttachment", [
    that.sameDocumentId,
    that.sameRevision,
    that.sameAttachmentId
  ], that.wait);

  that.addActionRule("get", "get",
                     [that.sameDocument, that.sameOption], that.update);
  that.addActionRule("getAttachment", "getAttachment",
                     [that.sameDocument, that.sameOption], that.update);
  that.addActionRule("allDocs", "allDocs",
                     [that.sameDocument, that.sameOption], that.update);

  // end adding rules
  ////////////////////////////////////////////////////////////////////////////
  return that;
}());
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global spec: true, localstorage: true,
         activityUpdater: true, jobManager: true, storage: true,
         storage_type_object: true, invalidStorageType: true, jobRules: true,
         job: true, postCommand: true, putCommand: true, getCommand:true,
         allDocsCommand: true, putAttachmentCommand: true,
         getAttachmentCommand: true, removeAttachmentCommand: true,
         removeCommand: true, checkCommand: true, repairCommand: true */
// Class jio
var that = {}, priv = {}, jio_id_array_name = 'jio/id_array';
spec = spec || {};
// Attributes //
priv.id = null;

priv.storage_spec = spec;

priv.environments = {};

// initialize //
priv.init = function () {
  // Initialize the jio id and add the new id to the list
  if (priv.id === null) {
    var i, jio_id_a =
      localstorage.getItem(jio_id_array_name) || [];
    priv.id = 1;
    for (i = 0; i < jio_id_a.length; i += 1) {
      if (jio_id_a[i] >= priv.id) {
        priv.id = jio_id_a[i] + 1;
      }
    }
    jio_id_a.push(priv.id);
    localstorage.setItem(jio_id_array_name, jio_id_a);
    activityUpdater.setId(priv.id);
    jobManager.setId(priv.id);
  }
};

// Methods //
/**
 * Returns a storage from a storage description.
 * @method storage
 * @param  {object} spec The specifications.
 * @param  {object} my The protected object.
 * @param  {string} forcetype Force storage type
 * @return {object} The storage object.
 */
Object.defineProperty(that, "storage", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (spec, my, forcetype) {
    var spec_str, type;
    spec = spec || {};
    my = my || {};
    my.basicStorage = storage;
    spec_str = JSON.stringify(spec);
    // environment initialization
    priv.environments[spec_str] = priv.environments[spec_str] || {};
    my.env = priv.environments[spec_str];
    my.storage = that.storage; // NOTE : or proxy storage
    type = forcetype || spec.type || 'base';
    if (type === 'base') {
      return storage(spec, my);
    }
    if (!storage_type_object[type]) {
      throw invalidStorageType({
        "type": type,
        "message": "Storage does not exists."
      });
    }
    return storage_type_object[type](spec, my);
  }
});
jobManager.storage = that.storage;

Object.defineProperty(that, "start", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    priv.init();
    activityUpdater.start();
    jobManager.start();
  }
});

Object.defineProperty(that, "stop", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    jobManager.stop();
  }
});

Object.defineProperty(that, "close", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    activityUpdater.stop();
    jobManager.stop();
    priv.id = null;
  }
});

/**
 * Returns the jio id.
 * @method getId
 * @return {number} The jio id.
 */
Object.defineProperty(that, "getId", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    return priv.id;
  }
});

/**
 * Returns the jio job rules object used by the job manager.
 * @method getJobRules
 * @return {object} The job rules object
 */
Object.defineProperty(that, "getJobRules", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    return jobRules;
  }
});

/**
 * Checks if the storage description is valid or not.
 * @method validateStorageDescription
 * @param  {object} description The description object.
 * @return {boolean} true if ok, else false.
 */
Object.defineProperty(that, "validateStorageDescription", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (description) {
    return that.storage(description).isValid();
  }
});

Object.defineProperty(that, "getJobArray", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function () {
    return jobManager.serialized();
  }
});

priv.makeCallbacks = function (param, callback1, callback2) {
  param.callback = function (err, val) {
    if (err) {
      param.error(err);
    } else {
      param.success(val);
    }
  };
  param.success = function (val) {
    param.callback(undefined, val);
  };
  param.error = function (err) {
    param.callback(err, undefined);
  };
  if (typeof callback1 === 'function') {
    if (typeof callback2 === 'function') {
      param.success = callback1;
      param.error = callback2;
    } else {
      param.callback = callback1;
    }
  } else {
    param.callback = function () {};
  }
};

priv.parametersToObject = function (list, default_options) {
  var k, i = 0, callbacks = [], param = {"options": {}};
  for (i = 0; i < list.length; i += 1) {
    if (typeof list[i] === 'object') {
      // this is the option
      param.options = list[i];
      for (k in default_options) {
        if ((typeof default_options[k]) !== (typeof list[i][k])) {
          param.options[k] = default_options[k];
        }
      }
    }
    if (typeof list[i] === 'function') {
      // this is a callback
      callbacks.push(list[i]);
    }
  }
  priv.makeCallbacks(param, callbacks[0], callbacks[1]);
  return param;
};

priv.addJob = function (commandCreator, spec) {
  jobManager.addJob(job({
    "storage": that.storage(priv.storage_spec),
    "command": commandCreator(spec)
  }));
};

/**
 * Post a document.
 * @method post
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id (optional)
 * For revision managing: choose at most one of the following informations:
 * - {string} _rev The revision we want to update
 * - {string} _revs_info The revision information we want the document to have
 * - {string} _revs The revision history we want the document to have
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "post", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 0}
    );

    priv.addJob(postCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Put a document.
 * @method put
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * For revision managing: choose at most one of the following informations:
 * - {string} _rev The revision we want to update
 * - {string} _revs_info The revision information we want the document to have
 * - {string} _revs The revision history we want the document to have
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "put", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 0}
    );

    priv.addJob(putCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Get a document.
 * @method get
 * @param  {string} doc The document object. Contains at least:
 * - {string} _id The document id
 * For revision managing:
 * - {string} _rev The revision we want to get. (optional)
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * For revision managing:
 * - {boolean} revs Include revision history of the document.
 * - {boolean} revs_info Include list of revisions, and their availability.
 * - {boolean} conflicts Include a list of conflicts.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "get", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 3}
    );

    priv.addJob(getCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Remove a document.
 * @method remove
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * For revision managing:
 * - {string} _rev The revision we want to remove
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "remove", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, callback) {
    var param = priv.parametersToObject(
      [options, success, callback],
      {max_retry: 0}
    );

    priv.addJob(removeCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Get a list of documents.
 * @method allDocs
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * - {boolean} include_docs Include document metadata
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "allDocs", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 3}
    );

    priv.addJob(allDocsCommand, {
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Get an attachment from a document.
 * @method gettAttachment
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * - {string} _attachment The attachment id
 * For revision managing:
 * - {string} _rev The document revision
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,respons)
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "getAttachment", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 3}
    );

    priv.addJob(getAttachmentCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Put an attachment to a document.
 * @method putAttachment
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * - {string} _attachment The attachment id
 * - {string} _data The attachment data
 * - {string} _mimetype The attachment mimetype
 * For revision managing:
 * - {string} _rev The document revision
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,respons)
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "putAttachment", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 0}
    );

    priv.addJob(putAttachmentCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Put an attachment to a document.
 * @method putAttachment
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * - {string} _attachment The attachment id
 * For revision managing:
 * - {string} _rev The document revision
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,respons)
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "removeAttachment", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, error) {
    var param = priv.parametersToObject(
      [options, success, error],
      {max_retry: 0}
    );

    priv.addJob(removeAttachmentCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Check a document.
 * @method check
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "check", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, callback) {
    var param = priv.parametersToObject(
      [options, success, callback],
      {max_retry: 3}
    );

    priv.addJob(checkCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});

/**
 * Repair a document.
 * @method repair
 * @param  {object} doc The document object. Contains at least:
 * - {string} _id The document id
 * @param  {object} options (optional) Contains some options:
 * - {number} max_retry The number max of retries, 0 = infinity.
 * @param  {function} callback (optional) The callback(err,response).
 * @param  {function} error (optional) The callback on error, if this
 *     callback is given in parameter, "callback" is changed as "success",
 *     called on success.
 */
Object.defineProperty(that, "repair", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: function (doc, options, success, callback) {
    var param = priv.parametersToObject(
      [options, success, callback],
      {max_retry: 3}
    );

    priv.addJob(repairCommand, {
      doc: doc,
      options: param.options,
      callbacks: {success: param.success, error: param.error}
    });
  }
});
  return that;
};                              // End Class jio
/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global exports, jio, invalidStorageType */

var storage_type_object = { // -> 'key':constructorFunction
  'base': function () { // overriden by jio
    return undefined;
  }
};

/**
 * Creates a new jio instance.
 * @method newJio
 * @param  {object} spec The storage description
 * @return {object} The new Jio instance.
 */
Object.defineProperty(exports, "newJio", {
  configurable: false,
  enumerable: true,
  writable: false,
  value: function (spec) {
    var storage = spec, instance = null;
    if (typeof storage === 'string') {
      storage = JSON.parse(storage);
    } else {
      storage = JSON.stringify(storage);
      if (storage !== undefined) {
        storage = JSON.parse(storage);
      }
    }
    storage = storage || {
      type: 'base'
    };
    instance = jio(storage);
    instance.start();
    return instance;
  }
});

/**
 * Add a storage type to jio.
 * @method addStorageType
 * @param  {string} type The storage type
 * @param  {function} constructor The associated constructor
 */
Object.defineProperty(exports, "addStorageType", {
  configurable: false,
  enumerable: true,
  writable: false,
  value: function (type, constructor) {
    constructor = constructor || function () {
      return null;
    };
    if (storage_type_object[type]) {
      throw invalidStorageType({
        type: type,
        message: 'Already known.'
      });
    }
    storage_type_object[type] = constructor;
  }
});

}));
