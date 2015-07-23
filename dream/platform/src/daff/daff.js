/*global jQuery, rJS, window, JSON, daff */

(function (window, $, rJS, JSON, daff) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (content) {
      var flags, highlighter, diff2html, table_diff, table_diff_html,
        data_diff = [],
        data = JSON.parse(content),        
        table1 = new daff.TableView(data[0]),
        table2 = new daff.TableView(data[1]),
        alignment = daff.compareTables(table1,table2).align();
        table_diff = new daff.TableView(data_diff);

        flags = new daff.CompareFlags();
        highlighter = new daff.TableDiff(alignment,flags);
        highlighter.hilite(table_diff);
        diff2html = new daff.DiffRender();
        diff2html.render(table_diff);
        table_diff_html = diff2html.html();

      return this.getElement()
        .push(function (element) {
          $(element).addClass("highlighter").html(table_diff_html);
        });
    });
}(window, jQuery, rJS, JSON, daff));
