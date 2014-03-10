/* ===========================================================================
 * Copyright 2013 Nexedi SA and Contributors
 *
 * This file is part of DREAM.
 *
 * DREAM is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * DREAM is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
 * =========================================================================== */

(function ($) {
  "use strict";
  jsPlumb.bind("ready", function () {
    var dream_instance, jio;
    jio = new jIO.newJio({
      type: "local",
      username: "dream",
      applicationname: "dream"
    });

    var configuration = { };

    $.ajax(
        '../getConfigurationDict', {
       success: function (data) {
         configuration = $.extend(configuration, data);

    dream_instance = Dream(configuration);
    dream_instance.start();

    $(".tool").draggable({
      containment: '#main',
      opacity: 0.7,
      helper: "clone",
      cursorAt: {
        top: 0,
        left: 0
      },
      stop: function (event) {
        var box_top, box_left, _class;
        var offset = $("#main").offset();
        box_top = event.clientY - offset.top + "px";
        box_left = event.clientX - offset.left + "px";
        var relative_position = dream_instance.convertToRelativePosition(
          box_left, box_top);
        _class = event.target.id.replace('-', '.'); // XXX - vs .
        dream_instance.newElement({
          coordinate: {
            top: relative_position[1],
            left: relative_position[0]
          },
          _class: _class
        });
      }
    });

    var loadData = function (data) {
      dream_instance.clearAll();
      $('#reports').hide();
      $('#result_zone').hide();

      $('#shift_spreadsheet').hide();
      $("#wip_part_spreadsheet").hide();

      if (configuration['Dream-Configuration'].gui.wip_part_spreadsheet){
        $("#wip_part_spreadsheet").show();
      }
      if (configuration['Dream-Configuration'].gui.shift_spreadsheet){
        $("#shift_spreadsheet").show();
      }

      try {
        // spreadsheets
        var shift_spreadsheet_data = data.shift_spreadsheet;
        if (shift_spreadsheet_data !== undefined) {
          var spreadsheet = $('#shift_spreadsheet');
          spreadsheet.handsontable('populateFromArray', 0, 0, shift_spreadsheet_data);
        }
        var wip_part_spreadsheet_data = data.wip_part_spreadsheet;
        if (wip_part_spreadsheet_data !== undefined) {
          var spreadsheet = $('#wip_part_spreadsheet');
          spreadsheet.handsontable('populateFromArray', 0, 0, wip_part_spreadsheet_data);
        }

        var preference = data.preference !== undefined ?
          data.preference : {};
        dream_instance.setPreferences(preference);

        // Add all elements
        var coordinates = preference['coordinates'];
        $.each(data.nodes, function (key, value) {
          if (coordinates === undefined || coordinates[key] === undefined) {
            value['coordinate'] = {
              'top': 0.0,
              'left': 0.0
            };
          } else {
            value['coordinate'] = coordinates[key];
          }
          value['id'] = key;
          dream_instance.newElement(value);
          if (value.data) { // backward compatibility
            dream_instance.updateElementData(key, {
              data: value.data
            });
          }
        });
        $.each(data.edges, function (key, value) {
          dream_instance.addEdge(key, value);
        });

        dream_instance.updateGeneralProperties(data.general);
        dream_instance.prepareDialogForGeneralProperties();

        if ($.isEmptyObject(coordinates)) {
          dream_instance.positionGraph();
        } else {
          dream_instance.redraw();
        }
      } catch (e) {
        alert('Loading data failed.');
        console.error(e);
      }
    };
    // Check if there is already data when we first load the page, if yes, then build graph from it
    jio.get({
      _id: "dream_demo"
    }, function (err, response) {
      if (response !== undefined && response.data !== undefined) {
        var load = function () {
          loadData(response.data);
        }
        jsPlumb.doWhileSuspended(load);
      }
      // once the data is read, we can subscribe to every changes
      $.subscribe("Dream.Gui.onDataChange", function (event, data) {
        jio.put({
          _id: "dream_demo",
          data: data
        }, function (err, response) {});
      });
    });

    // Enable "Run Knowledge Extraction" button
    $("#run_knowledge_extraction").button().click(
      function (e) {
        $("#ke_loading_spinner").show();
        $("#run_knowledge_extraction").button('disable');
        $('#error').empty();
        dream_instance.runKnowledgeExtraction(
          function(data) {
              $("#ke_loading_spinner").hide();
              $("#run_knowledge_extraction").button('enable');
              if (data['success']) {
                loadData(data.data);
              } else {
                $("#error").text(data["error"]).show().effect('shake', 50);
                console.error(data['error'])
              }
            });
      });

    // Enable "Run Simulation" button
    $("#xxrun_simulation").button().click(
      function (e) {
        $("#loading_spinner").show();
        $("#run_simulation").button('disable');
        dream_instance.runSimulation(
          function (data) {
            $("#loading_spinner").hide();
            $("#run_simulation").button('enable');
            $("#reports").show();
            $("#result_zone").show();
            $('#result_list').empty();
            $('#error').empty();
            if (data['success']) {

              $.each(data.data, function (idx, result) {
                $('#result_list').append('<li class="result"></li>');
                $('#result_list').children().last().text(idx + ' : ' + result['score'] + ' ' + result['key']).click(
                  function (e) {
                    dream_instance.displayResult(idx, result)
                  }
                );
              });
              dream_instance.displayResult(0, data.data[0]);
            } else {
              $("#reports").hide();
              $("#error").text(data["error"]).show().effect('shake', 50);
              console.error(data['error'])
            }
          });
        e.preventDefault();
        return false;
      });

    // Enable "Layout Graph" button
    $("#layout_graph").button().click(
      function (e) {
        dream_instance.positionGraph();
      });

    // Enable "Clear All" button
    $("#clear_all").button().click(
      function (e) {
        if (confirm("Are you sure you want to clear all ?")) {
          dream_instance.clearAll();
          e.preventDefault();
        }
        return false;
      });

    // Enable "Zoom +" button
    $("#zoom_in").button().click(
      function (e) {
        dream_instance.zoom_in();
      });

    // Enable "Zoom -" button
    $("#zoom_out").button().click(
      function (e) {
        dream_instance.zoom_out();
      });

    // Enable "Export" button
    $("#export").button().click(
      function (e) {
        dream_instance.readGeneralPropertiesDialog();
        $('#export_json').val(JSON.stringify(dream_instance.getData()));
        $('#export_form').submit();
        return false;
      });

    // Enable "Import" button
    $("#import").button().click(
      function (e) {
        $('#import_file').click();
      });
    $("#import_file").change(function () {
      var form = $(this).parent('form')[0];
      var form_data = new FormData(form);
      $.ajax('../postJSONFile', {
        type: 'POST',
        contentType: false,
        processData: false,
        data: form_data,
        dataType: 'json',
        error: function () {
          console.error('error');
        },
        success: function (data, textStatus, jqXHR) {
          form.reset();
          loadData(data);
        }
      });
      return false;
    });

    // Redraw if the graph area or the window is resized
    $('#main').resizable().resize(function () {
      dream_instance.redraw();
    });
    $(window).resize(function () {
      dream_instance.redraw();
    });
    $("#job_schedule_spreadsheet").hide();
    $("#shift_spreadsheet").hide();
       }
    });


    // display entities in a station
    function displayEntities(element_id, node_id) {
      var node = $("#" + element_id);
      var node_position = node.position();
      var entities = $(".in_" + node_id);
      var offset = 0;
      if (entities.length > 4) {
        entities.hide();
        dream_instance.updateElementData(node_id, 
            {status: entities.length});
      }
      entities.each(
        function (idx, entity) {
          entity = $(entity)
          entity.css({top: node_position.top +
                           node.height() -
                           (idx * entity.height()) - 
                           (entity.height() / 2),
                      left: node_position.left +
                            node.width() -
                            entity.width()})
        }
      )
    }

    // move an entity from source to destination
    function moveEntity(message, queue) {
        var size = 20 * dream_instance.getData().preference.zoom_level;
        var entity = $("#" + message.entity);
        var source = dream_instance.getElementId(message.source);
        var destination = dream_instance.getElementId(message.destination);
          // XXX do we need a getElementId for edges ? for entities ?
        var edge = $("#" + message.edge);
        var win_offset = $('#main').offset()
        var path = edge.find("path")[1]
        var offset = edge.find("path:nth(1)").offset();
        var path_length = path.getTotalLength()
        var percent = 100;
        if (!entity.length) {
          var d= $("<div class='entity' id='" + message.entity + "'>"
            + message.entity + "</div>").css(
            {"width": size,
             "height": size,
             "position": "absolute",
             "border-radius": size / 2, 
             "background": "red"} // TODO: random color ?
          ).appendTo($("#main"));
          entity = $("#" + message.entity);
        }

        // XXX at this point the entity does not have the class yet 
        entity.removeClass("in_"+ message.source)

        displayEntities(source, message.source);
        $("#now").text(message.time.toFixed(2));

        var timer;
        ( function calc() {
          percent -= Math.min(dream_instance.getData().general.animationSpeed, 100);
          if (percent < 0) {
            percent = 0;
          }
          timer = setTimeout(calc, 10)
          var point = path.getPointAtLength(percent*path_length/100);
          var c = { 'z-index':100,
                    position:"absolute",
                    top:(offset.top + point.y - win_offset.top) + "px",
                    left:(offset.left + point.x - win_offset.left) + "px" }
          entity.css(c)
          if (percent == 0){
            clearTimeout(timer)
            $(queue).dequeue()
            entity.removeClass("in_"+ message.source)
            entity.addClass("in_"+ message.destination)
            displayEntities(source, message.source);
            displayEntities(destination, message.destination);
          }
        })()

        
      }
  
    function notifyEndSimulation(message){
        $("#json_result").val(JSON.stringify(message['success'],
          undefined, " "));
        $("#loading_spinner").hide();
        $("#run_simulation").button('enable');
        $("#result_zone").show();
  
        $(".entity").remove();

        $('#result_list').empty();
        $('.window > .status').remove();
        $.each(message['success'], function (idx, obj) {
          $('#result_list').append('<li class="result"></li>');
          $('#result_list').children().last().text(
            idx + ' : ' + obj['score'] + ' ' + obj['key']).click(
             function (e) {
              dream_instance.displayResult(idx);
            }
          );
        });
        dream_instance.displayResult(0);
      }

    function onWebSocketMessage(e) {
      var message = JSON.parse(e.data)

      if (message.action === "move_entity"){
        $("#main").queue(function() {
          moveEntity(message, this);
        })
      }

      if (message['success']) {
        $("#main").queue(function() {
          notifyEndSimulation(message, this);
        })
      }
    };

    var webSocket = new WebSocket("ws://localhost:5000/api");
    // TODO reorganise
    $("#run_simulation").button().on('click', function(e) {
      dream_instance.readGeneralPropertiesDialog()
      $("#loading_spinner").show();
      $("#run_simulation").button('disable');
      webSocket.onmessage = onWebSocketMessage

      var msg = JSON.stringify(dream_instance.getData());
      webSocket.send(msg);
      return false;
    });

  });
})(jQuery);
