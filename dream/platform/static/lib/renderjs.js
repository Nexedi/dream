/*! RenderJs v0.2  */
/*global jQuery, window, document, DOMParser, Channel */
"use strict";

/*
 * DOMParser HTML extension
 * 2012-09-04
 *
 * By Eli Grey, http://eligrey.com
 * Public domain.
 * NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
 */
/*! @source https://gist.github.com/1129031 */
(function (DOMParser) {
  var DOMParser_proto = DOMParser.prototype,
    real_parseFromString = DOMParser_proto.parseFromString;

  // Firefox/Opera/IE throw errors on unsupported types
  try {
    // WebKit returns null on unsupported types
    if ((new DOMParser()).parseFromString("", "text/html")) {
      // text/html parsing is natively supported
      return;
    }
  } catch (ex) {}

  DOMParser_proto.parseFromString = function (markup, type) {
    var result, doc, doc_elt, first_elt;
    if (/^\s*text\/html\s*(?:;|$)/i.test(type)) {
      doc = document.implementation.createHTMLDocument("");
      doc_elt = doc.documentElement;

      doc_elt.innerHTML = markup;
      first_elt = doc_elt.firstElementChild;

      if (doc_elt.childElementCount === 1
          && first_elt.localName.toLowerCase() === "html") {
        doc.replaceChild(first_elt, doc_elt);
      }

      result = doc;
    } else {
      result = real_parseFromString.apply(this, arguments);
    }
    return result;
  };
}(DOMParser));

/*
 * renderJs - Generic Gadget library renderer.
 * http://www.renderjs.org/documentation
 */
(function (document, window, $, DOMParser, Channel, undefined) {

  var gadget_model_dict = {},
    javascript_registration_dict = {},
    stylesheet_registration_dict = {},
    gadget_loading_klass,
    methods,
    loading_gadget_promise,
    renderJS;

  function RenderJSGadget() {}
  RenderJSGadget.prototype.title = "";
  RenderJSGadget.prototype.interface_list = [];
  RenderJSGadget.prototype.path = "";
  RenderJSGadget.prototype.html = "";
  RenderJSGadget.prototype.required_css_list = [];
  RenderJSGadget.prototype.required_js_list = [];

  RenderJSGadget.ready_list = [];
  RenderJSGadget.ready = function (callback) {
    this.ready_list.push(callback);
    return this;
  };

  RenderJSGadget.declareMethod = function (name, callback) {
// // Register the potentially loading javascript
// var script_element = $('script').last(),
//   src = script_element.attr('src');
// if (src !== undefined) {
//   if (javascript_registration_dict[src] === undefined) {
//     // First time loading the JS file.
//     // Remember all declareMethod calls
//     javascript_registration_dict[src] = {
//       loaded: false,
//       method_list: [[name, callback]],
//     };
//     script_element.load(function () {
//       javascript_registration_dict[src].loaded = true;
//     });
//   } else if (!javascript_registration_dict[src].loaded) {
//     javascript_registration_dict[src].method_list.push([name, callback]);
//   }
// }

    this.prototype[name] = function () {
      var dfr = $.Deferred(),
        gadget = this;
      $.when(callback.apply(this, arguments))
        .done(function () {
          dfr.resolveWith(gadget, arguments);
        })
        .fail(function () {
          dfr.rejectWith(gadget, arguments);
        });
      return dfr.promise();
    };
    // Allow chain
    return this;
  };

  RenderJSGadget
    .declareMethod('getInterfaceList', function () {
      // Returns the list of gadget prototype
      return this.interface_list;
    })
    .declareMethod('getRequiredCSSList', function () {
      // Returns a list of CSS required by the gadget
      return this.required_css_list;
    })
    .declareMethod('getRequiredJSList', function () {
      // Returns a list of JS required by the gadget
      return this.required_js_list;
    })
    .declareMethod('getPath', function () {
      // Returns the path of the code of a gadget
      return this.path;
    })
    .declareMethod('getTitle', function () {
      // Returns the title of a gadget
      return this.title;
    })
    .declareMethod('getHTML', function () {
      // Returns the HTML of a gadget
      return this.html;
    });

  // Class inheritance
  function RenderJSEmbeddedGadget() {
    var root_gadget = this,
      declare_method_count = 0,
      gadget_ready = false,
      // Create the communication channel
      embedded_channel = Channel.build({
        window: window.parent,
        origin: "*",
        scope: "renderJS"
      });

    RenderJSGadget.call(this);

    // Bind calls to renderJS method on the instance
    embedded_channel.bind("methodCall", function (trans, v) {
      root_gadget[v[0]].apply(root_gadget, v[1]).done(function (g) {
        trans.complete(g);
      }).fail(function () {
        trans.error(Array.prototype.slice.call(arguments, 0));
      });
      trans.delayReturn(true);
    });

    // Notify parent about gadget instanciation
    function notifyReady() {
      if ((declare_method_count === 0) && (gadget_ready === true)) {
        embedded_channel.notify({method: "ready"});
      }
    }

    // Inform parent gadget about declareMethod calls here.
    function notifyDeclareMethod(name) {
      declare_method_count += 1;
      embedded_channel.call({
        method: "declareMethod",
        params: name,
        success: function () {
          declare_method_count -= 1;
          notifyReady();
        },
        error: function () {
          declare_method_count -= 1;
//           console.error(Array.prototype.slice.call(arguments, 0));
        },
      });
    }

    notifyDeclareMethod("getInterfaceList");
    notifyDeclareMethod("getRequiredCSSList");
    notifyDeclareMethod("getRequiredJSList");
    notifyDeclareMethod("getPath");
    notifyDeclareMethod("getTitle");
    notifyDeclareMethod("getHTML");

    // Surcharge declareMethod to inform parent window
    this.constructor.declareMethod = function (name, callback) {
      notifyDeclareMethod(name);
      return RenderJSGadget.declareMethod.apply(this, [name, callback]);
    };

    // Inform parent window that gadget is correctly loaded
    loading_gadget_promise.done(function () {
      gadget_ready = true;
      notifyReady();
    }).fail(function () {
      embedded_channel.notify({method: "failed"});
    });
    return root_gadget;
  }
  RenderJSEmbeddedGadget.ready_list = [];
  RenderJSEmbeddedGadget.ready =
    RenderJSGadget.ready;
  RenderJSEmbeddedGadget.prototype = new RenderJSGadget();
  RenderJSEmbeddedGadget.prototype.constructor = RenderJSEmbeddedGadget;

  // Class inheritance
  function RenderJSIframeGadget() {
    RenderJSGadget.call(this);
  }
  RenderJSIframeGadget.ready_list = [];
  RenderJSIframeGadget.declareMethod =
    RenderJSGadget.declareMethod;
  RenderJSIframeGadget.ready =
    RenderJSGadget.ready;
  RenderJSIframeGadget.prototype = new RenderJSGadget();
  RenderJSIframeGadget.prototype.constructor = RenderJSIframeGadget;

  RenderJSGadget.prototype.declareIframedGadget =
    function (url, jquery_context) {
      var previous_loading_gadget_promise = loading_gadget_promise,
        next_loading_gadget_deferred = $.Deferred();

      // Change the global variable to update the loading queue
      loading_gadget_promise = next_loading_gadget_deferred.promise();

      // Wait for previous gadget loading to finish first
      previous_loading_gadget_promise.always(function () {
        // Instanciate iframe
        var gadget = new RenderJSIframeGadget();
        gadget.context = jquery_context;
        // XXX Do not set this info on the instance!
        gadget.path = url;
        // XXX onload onerror
// $('iframe').load(function() {
//     RunAfterIFrameLoaded();
// });

        // Create the iframe
        if (gadget.context !== undefined) {
          $(gadget.context).html(
            // Use encodeURI to prevent XSS
            '<iframe src="' + encodeURI(url) + '"></iframe>'
          );
          gadget.chan = Channel.build({
            window: gadget.context.find('iframe').first()[0].contentWindow,
            origin: "*",
            scope: "renderJS"
          });

//           gadget.getTitle = function () {
//             var dfr = $.Deferred();
//             gadget.chan.call({
//               method: "getTitle",
//               success: function (v) {
//                 dfr.resolve(v);
//               }
//             });
//             return dfr.promise();
//           };

          gadget.chan.bind("declareMethod", function (trans, method_name) {
            gadget[method_name] = function () {
              var dfr = $.Deferred();
              gadget.chan.call({
                method: "methodCall",
                params: [
                  method_name,
                  Array.prototype.slice.call(arguments, 0)],
                success: function () {
                  dfr.resolveWith(gadget, arguments);
                },
                error: function () {
                  dfr.rejectWith(gadget, arguments);
                }
                // XXX Error callback
              });
              return dfr.promise();
            };
            return "OK";
          });

          // Wait for the iframe to be loaded before continuing
          gadget.chan.bind("ready", function (trans) {
            next_loading_gadget_deferred.resolve(gadget);
            return "OK";
          });
          gadget.chan.bind("failed", function (trans) {
            next_loading_gadget_deferred.reject();
            return "OK";
          });
        } else {
          next_loading_gadget_deferred.reject();
        }
      });

      loading_gadget_promise
        // Drop the current loading klass info used by selector
        .done(function () {
          gadget_loading_klass = undefined;
        })
        .fail(function () {
          gadget_loading_klass = undefined;
        })
        .done(function (created_gadget) {
          $.each(created_gadget.constructor.ready_list,
                 function (i, callback) {
              callback.apply(created_gadget);
            });
        });

      return loading_gadget_promise;
    };

  RenderJSGadget.prototype.declareGadget = function (url, jquery_context) {
    var previous_loading_gadget_promise = loading_gadget_promise,
      next_loading_gadget_deferred = $.Deferred();

    // Change the global variable to update the loading queue
    loading_gadget_promise = next_loading_gadget_deferred.promise();

    // Wait for previous gadget loading to finish first
    previous_loading_gadget_promise.always(function () {
      // Get the gadget class and instanciate it
      renderJS.declareGadgetKlass(url).done(function (Klass) {
        var gadget = new Klass();
        gadget.context = jquery_context;

        // Load dependencies if needed
        $.when(gadget.getRequiredJSList(), gadget.getRequiredCSSList())
          .done(function (js_list, css_list) {
            var result_list = [],
              first_deferred = $.Deferred(),
              first_promise = first_deferred.promise();
            gadget_loading_klass = Klass;
            // Load JS and follow the dependency declaration defined in the
            // head
            function next(next_js_list) {
              var next_js = next_js_list.shift();
              if (next_js === undefined) {
                first_deferred.resolve();
              } else {
                renderJS.declareJS(next_js)
                  .done(function () {
                    next(next_js_list);
                  })
                  .fail(function () {
                    first_deferred.reject.apply(
                      first_deferred,
                      arguments
                    );
                  });
              }
            }
            next(js_list);
            result_list.push(first_promise);
            // Load CSS
            $.each(css_list, function (i, required_url) {
              result_list.push(renderJS.declareCSS(required_url));
            });
            $.when.apply(this, result_list)
              .done(function () {
                // Dependency correctly loaded. Fire instanciation success.
                next_loading_gadget_deferred.resolve(gadget);
              }).fail(function () {
//                 console.error(Array.prototype.slice.call(arguments, 0));
                // One error during css/js loading
                next_loading_gadget_deferred.reject.apply(
                  next_loading_gadget_deferred,
                  arguments
                );
              });

          }).fail(function () {
            // Failed to fetch dependencies information.
            next_loading_gadget_deferred.reject.apply(
              next_loading_gadget_deferred,
              arguments
            );
          });
      }).fail(function () {
        // Klass not correctly loaded. Reject instanciation
        next_loading_gadget_deferred.reject.apply(next_loading_gadget_deferred,
                                                  arguments);
      });
    });

    loading_gadget_promise
      // Drop the current loading klass info used by selector
      .done(function () {
        gadget_loading_klass = undefined;
      })
      .fail(function () {
        gadget_loading_klass = undefined;
      })
      .done(function (created_gadget) {
        // Set the content html and call the ready list if instance is
        // correctly loaded
        if (created_gadget.context !== undefined) {
          $(created_gadget.context).html(
            created_gadget.constructor.prototype.html
          );
        }
        $.each(created_gadget.constructor.ready_list, function (i, callback) {
          callback.apply(created_gadget);
        });
      });

    return loading_gadget_promise;
  };

  methods = {
    loadGadgetFromDom: function () {
      $(this).find('[data-gadget-path]').each(function (index, value) {
        $(this).renderJS('declareGadget', $(this).attr('data-gadget-path'), {
          scope: $(this).attr('data-gadget-scope'),
        })
          .done(function (value) {
            var parsed_xml;
            // Check that context is still attached to the DOM
            // XXX Usefull?
            if ($(this).closest(document.body).length) {
              parsed_xml = $($.parseXML(value));

              // Inject the css
              // XXX Manage relative URL
              $.each(parsed_xml.find('link[rel=stylesheet]'),
                     function (i, link) {
                  $('head').append(
                    '<link rel="stylesheet" href="' +
                      $(link).attr('href') +
                      '" type="text/css" />'
                  );
                });


              // Inject the js
              // XXX Manage relative URL
              $.each(parsed_xml.find('script[type="text/javascript"]'),
                     function (i, script) {
//                   $('head').append(
//                     '<script type="text/javascript" href="' +
//                       $(script).attr('src') +
//                       '" />'
//                   );
                  // Prevent infinite recursion if loading render.js
                  // more than once
                  if ($('head').find('script[src="' + $(script).attr('src')
                                 + '"]').length === 0) {
                    var headID = document.getElementsByTagName("head")[0],
                      newScript = document.createElement('script');
                    newScript.type = 'text/javascript';
                    newScript.src = $(script).attr('src');
                    headID.appendChild(newScript);
                  }
                });

              // Inject the html
              // XXX parseXML does not support <div /> (without 2 tags)
              $(this).html(parsed_xml.find('body').clone());
              // XXX No idea why it is required to make it work
              // Probably because of parseXML
              $(this).html($(this).html())
                     .renderJS('loadGadgetFromDom');
            }
          });
      });
    },

  };

//   // Define a local copy of renderJS
//   renderJS = function (selector) {
//     // The renderJS object is actually just the init constructor 'enhanced'
//     return new renderJS.fn.init(selector, rootrenderJS);
//   };
//   renderJS.fn = renderJS.prototype = {
//     constructor: renderJS,
//     init: function (selector, rootrenderJS) {
//       var result;
//       // HANDLE: $(""), $(null), $(undefined), $(false)
//       if (!selector) {
//         console.log("no selector");
//         result = this;
// //       // HANDLE: $(DOMElement)
// //       } else if (selector.nodeType) {
// //         this.context = this[0] = selector;
// //         this.length = 1;
// //         result = this;
// //       } else if (selector === this) {
// //         result = this.constructor();
//       } else {
// //         throw new Error("Not implemented selector " + selector);
//         result = this.constructor();
//       }
//       return result;
//     },
//   };
//   // Give the init function the renderJS prototype for later instantiation
//   renderJS.fn.init.prototype = renderJS.fn;
//
//   jQuery.fn.extend({
//     attr: function (name, value) {
//       return jQuery.access(this, jQuery.attr, name, value,
//                            arguments.length > 1);
//     },
//   });

  renderJS = function (selector) {
    var result;
//     if (selector.nodeType) {
//       console.log(selector);
//     } else {
    if (selector === window) {
      // window is the this value when loading a javascript file
      // In this case, use the current loading gadget constructor
      result = gadget_loading_klass;
//     } else if ($.isFunction(selector)) {
//       console.log(selector);
    } else if (selector instanceof RenderJSGadget) {
      result = selector;
    }
    if (result === undefined) {
      throw new Error("Unknown selector '" + selector + "'");
    }
    return result;
  };

  renderJS.declareJS = function (url) {
//     // Prevent infinite recursion if loading render.js
//     // more than once
//     if ($('head').find('script[src="' + $(script).attr('src')
//                    + '"]').length === 0) {
//       var headID = document.getElementsByTagName("head")[0],
//         newScript = document.createElement('script');
//       newScript.type = 'text/javascript';
//       newScript.src = $(script).attr('src');
//       headID.appendChild(newScript);
//     }
    var dfr,
      origin_dfr = $.Deferred(),
      head_element,
      script_element;
    if (javascript_registration_dict.hasOwnProperty(url)) {
      setTimeout(function () {
        origin_dfr.resolve();
      });
      dfr = origin_dfr.promise();
    } else {
      dfr = $.ajax({
        url: url,
        dataType: "script",
        cache: true,
      }).done(function (script, textStatus) {
        javascript_registration_dict[url] = null;
//       }).fail(function () {
//         console.error(Array.prototype.slice.call(arguments, 0));
      });

    }
    return dfr;
  };

  renderJS.declareCSS = function (url) {
    // https://github.com/furf/jquery-getCSS/blob/master/jquery.getCSS.js
    // No way to cleanly check if a css has been loaded
    // So, always resolve the promise...
    // http://requirejs.org/docs/faq-advanced.html#css
    var origin_dfr = $.Deferred(),
      origin_promise = origin_dfr.promise(),
      head,
      link;
    if (stylesheet_registration_dict.hasOwnProperty(url)) {
      setTimeout(function () {
        origin_dfr.resolve();
      });
    } else {
      head = document.getElementsByTagName('head')[0];
      link = document.createElement('link');

      link.rel = 'stylesheet';
      link.type = 'text/css';
      link.href = url;

      origin_promise.done(function () {
        stylesheet_registration_dict[url] = null;
      });

      head.appendChild(link);

      setTimeout(function () {
        origin_dfr.resolve();
      });

    }
    return origin_promise;
  };

  renderJS.declareGadgetKlass = function (url) {
    var dfr = $.Deferred(),
      parsed_html;

    if (gadget_model_dict.hasOwnProperty(url)) {
      dfr.resolve(gadget_model_dict[url]);
    } else {
      $.ajax(url)
        .done(function (value, textStatus, jqXHR) {
          var klass, tmp_constructor, key;
          if (/^text\/html[;]?/.test(
              jqXHR.getResponseHeader("Content-Type") || ""
            )) {

            try {
              if (!gadget_model_dict.hasOwnProperty(url)) {
                // Class inheritance
                tmp_constructor = function () {
                  RenderJSGadget.call(this);
                };
                tmp_constructor.ready_list = [];
                tmp_constructor.declareMethod =
                  RenderJSGadget.declareMethod;
                tmp_constructor.ready =
                  RenderJSGadget.ready;
                tmp_constructor.prototype = new RenderJSGadget();
                tmp_constructor.prototype.constructor = tmp_constructor;
                tmp_constructor.prototype.path = url;
                parsed_html = renderJS.parseGadgetHTML(value);
                for (key in parsed_html) {
                  if (parsed_html.hasOwnProperty(key)) {
                    tmp_constructor.prototype[key] = parsed_html[key];
                  }
                }
                gadget_model_dict[url] = tmp_constructor;
              }

              dfr.resolve(gadget_model_dict[url]);
            } catch (e) {
              dfr.reject(jqXHR, "HTML Parsing failed");
            }
          } else {
            dfr.reject(jqXHR, "Unexpected content type");
          }
        })
        .fail(function () {
          dfr.reject.apply(dfr, arguments);
        });
    }
    return dfr.promise();
  };

  // For test purpose only
  renderJS.clearGadgetKlassList = function () {
    gadget_model_dict = {};
    javascript_registration_dict = {};
    stylesheet_registration_dict = {};
  };

  renderJS.parseGadgetHTML = function (html) {
    var parsed_xml,
      result,
      settings = {
        title: "",
        interface_list: [],
        html: "",
        required_css_list: [],
        required_js_list: [],
      };
    if (html.constructor === String) {

      // https://developer.mozilla.org/en-US/docs/HTML_in_XMLHttpRequest
      // https://developer.mozilla.org/en-US/docs/Web/API/DOMParser
      // https://developer.mozilla.org/en-US/docs/Code_snippets/HTML_to_DOM
      // parsed_xml = $($.parseXML(html));
      // parsed_xml = $('<div/>').html(html);
      parsed_xml = $((new DOMParser()).parseFromString(html, "text/html"));
      settings.title = parsed_xml.find('head > title').first().text();

      // XXX Manage relative URL during extraction of URLs
      $.each(parsed_xml.find('head > link[rel=stylesheet]'),
             function (i, link) {
          settings.required_css_list.push($(link).attr('href'));
        });

      $.each(parsed_xml.find('head > script[type="text/javascript"]'),
             function (i, script) {
          settings.required_js_list.push($(script).attr('src'));
        });

      $.each(parsed_xml.find(
        'head > link[rel="http://www.renderjs.org/rel/interface"]'
      ), function (i, link) {
        settings.interface_list.push($(link).attr('href'));
      });

      settings.html = parsed_xml.find('html > body').first().html();
      if (settings.html === undefined) {
        settings.html = "";
      }
      result = settings;
    } else {
      throw new Error(html + " is not a string");
    }
    return result;
  };
  window.rJS = window.renderJS = renderJS;
  window.RenderJSGadget = RenderJSGadget;

  ///////////////////////////////////////////////////
  // Bootstrap process. Register the self gadget.
  ///////////////////////////////////////////////////

  function bootstrap() {
    var url = window.location.href,
      tmp_constructor,
      root_gadget,
      loading_gadget_deferred = $.Deferred();

    // Create the gadget class for the current url
    if (gadget_model_dict.hasOwnProperty(url)) {
      throw new Error("bootstrap should not be called twice");
    }
    loading_gadget_promise = loading_gadget_deferred.promise();

    if (window.self === window.top) {
      // XXX Copy/Paste from declareGadgetKlass
      tmp_constructor = function () {
        RenderJSGadget.call(this);
      };
      tmp_constructor.declareMethod = RenderJSGadget.declareMethod;
      tmp_constructor.ready_list = [];
      tmp_constructor.ready = RenderJSGadget.ready;
      tmp_constructor.prototype = new RenderJSGadget();
      tmp_constructor.prototype.constructor = tmp_constructor;
      tmp_constructor.prototype.path = url;
      gadget_model_dict[url] = tmp_constructor;

      // Create the root gadget instance and put it in the loading stack
      root_gadget = new gadget_model_dict[url]();
    } else {
      // Create the root gadget instance and put it in the loading stack
      tmp_constructor = RenderJSEmbeddedGadget;
      root_gadget = new RenderJSEmbeddedGadget();
    }
    gadget_loading_klass = tmp_constructor;




    $(document).ready(function () {
      // XXX HTML properties can only be set when the DOM is fully loaded
      var settings = renderJS.parseGadgetHTML($('html')[0].outerHTML),
        promise,
        key;
      for (key in settings) {
        if (settings.hasOwnProperty(key)) {
          tmp_constructor.prototype[key] = settings[key];
        }
      }
      root_gadget.context = $('body');
      promise = $.when(root_gadget.getRequiredJSList(),
                       root_gadget.getRequiredCSSList())
        .done(function (js_list, css_list) {
          $.each(js_list, function (i, required_url) {
            javascript_registration_dict[required_url] = null;
          });
          $.each(css_list, function (i, required_url) {
            stylesheet_registration_dict[url] = null;
          });
          $.each(tmp_constructor.ready_list, function (i, callback) {
            callback.apply(root_gadget);
          });
          gadget_loading_klass = undefined;
          loading_gadget_deferred.resolve();
        }).fail(function () {
          loading_gadget_deferred.reject.apply(loading_gadget_deferred,
                                               arguments);
        });
    });
  }
  bootstrap();

}(document, window, jQuery, DOMParser, Channel));
