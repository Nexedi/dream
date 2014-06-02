/*global window, jQuery, jIO, rJS */
/*jslint unparam: true*/
"use strict";
(function (window, $, jIO, rJS) {

  var gk = rJS(window);

  gk.declareMethod('configureIO', function (json_configuration, key) {
    rJS(this).jio = jIO.newJio(json_configuration);
    rJS(this).jio_key = key;
    //console.log(rJS(this).jio);
    return key;
  })

    .declareMethod('getIO', function () {
      var deferred = $.Deferred(),
        default_value = "",
        gadget = rJS(this);

      gadget.jio.getAttachment({
        "_id": gadget.jio_key,
        "_attachment": "body.txt"
      }, function (err, response) {
        if (err) {
          if (err.status === 404) {
            deferred.resolve(default_value);
          } else {
            deferred.reject(err);
          }
        } else {
          //console.log("getIO: " + response);
          deferred.resolve(response || default_value);
        }
      });

      return deferred.promise();
    })

    .declareMethod('setIO', function (value) {
      //console.log("couscous");
      var deferred = $.Deferred(),
        gadget = rJS(this);
      gadget.jio.put({"_id": gadget.jio_key},
        function (err, response) {
          if (err) {
            deferred.reject(err);
          } else {
            gadget.jio.putAttachment({
              "_id": gadget.jio_key,
              "_attachment": "body.txt",
              "_data": value,

              "_mimetype": "text/plain"
            }, function (err, response) {
              if (err) {
                deferred.reject(err);
              } else {
                //console.log("putIO: " + value);
                deferred.resolve();
              }
            });
          }
        });
      return deferred.promise();
    });

}(window, jQuery, jIO, rJS));
