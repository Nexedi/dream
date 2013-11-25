/**
 * @project jQuery.sheet() The Ajax Spreadsheet - http://code.google.com/p/jquerysheet/
 * @author RobertLeePlummerJr@gmail.com
 * $Id: jquery.sheet.dts.js 717 2013-02-11 14:52:30Z robertleeplummerjr@gmail.com $
 * Licensed under MIT
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

(function($) {
	/**
	 * @namespace
	 * @name dts
	 * @type {Object}
	 * @memberOf jQuery.sheet
	 */
	jQuery.sheet.dts = {
		/**
		 * @memberOf jQuery.sheet.dts
		 * @name toTables
		 * @namespace
		 */
		toTables: {

			/**
			 * Create a table from json
			 * @param {Array} json array of spreadsheets - schema:
			 * [{ // sheet 1, can repeat
			 *  "title": "Title of spreadsheet",
			 *  "metadata": {
			 *      "widths": [
			 *          "120px", //widths for each column, required
			 *          "80px"
			 *      ]
			 *  },
			 *  "rows": [
			 *      { // row 1, repeats for each column of the spreadsheet
			 *          "height": "18px", //optional
			 *          "columns": [
			 *              { //column A
			 *                  "class": "css classes", //optional
			 *                  "formula": "=cell formula", //optional
			 *                  "value": "value", //optional
			 *                  "style": "css cell style" //optional
			 *              },
			 *              {} //column B
			 *          ]
			 *      },
			 *      { // row 2
			 *          "height": "18px", //optional
			 *          "columns": [
			 *              { // column A
			 *                  "class": "css classes", //optional
			 *                  "formula": "=cell formula", //optional
			 *                  "value": "value", //optional
			 *                  "style": "css cell style" //optional
			 *              },
			 *              {} // column B
			 *          ]
			 *      }
			 *  ]
			 * }]
			 * @returns {*|jQuery|HTMLElement} a simple html table
			 * @methodOf jQuery.sheet.dts.toTables
			 * @name json
			 */
			json: function(json) {

				var tables = $([]);

				$.each(json, function() {
					var table = $('<table />');
					if (this['title']) table.attr('title', this['title'] || '');

					tables = tables.add(table);

					$.each(this['rows'], function() {
						if (this['height']) {
							var tr = $('<tr />')
								.attr('height', this['height'])
								.css('height', this['height'])
								.appendTo(table);
						}
						$.each(this['columns'], function() {
							var td = $('<td />')
								.appendTo(tr);

							if (this['class']) td.attr('class', this['class'] || '');
							if (this['style']) td.attr('style', this['style'] || '');
							if (this['formula']) td.data('formula', (this['formula'] ? '=' + this['formula'] : ''))
							if (this['value']) td.html(this['value'] || '')
						});
					});

					if (!this['metadata']) return;
					if (this['metadata']['widths']) {
						var colgroup = $('<colgroup />')
							.prependTo(table);
						for(var width in this['metadata']['widths']) {
							var col = $('<col />')
								.attr('width', this['metadata']['widths'][width])
								.css('width', this['metadata']['widths'][width])
								.appendTo(colgroup);
						}
					}
					if (this['metadata']['frozenAt']) {
						if (this['metadata']['frozenAt']['row']) {
							table.data('frozenatrow', this['metadata']['frozenAt']['row']);
						}
						if (this['metadata']['frozenAt']['col']) {
							table.data('frozenatcol', this['metadata']['frozenAt']['col']);
						}
					}
				});

				return tables;
			},

			/**
			 *
			 * @param {String|jQuery|HTMLElement} xml - schema:
			 * &lt;spreadsheets&gt;
			 *     &lt;spreadsheet title="spreadsheet title"&gt;
			 *         &lt;metadata&gt;
			 *             &lt;widths&gt;
			 *                 &lt;width&gt;120px&lt;/width&gt;
			 *                 &lt;width&gt;80px&lt;/width&gt;
			 *             &lt;/widths&gt;
			 *         &lt;/metadata&gt;
			 *         &lt;rows&gt;
			 *             &lt;row height="15px"&gt;
			 *                  &lt;columns&gt;
			 *                      &lt;column&gt;
			 *                          &lt;formula&gt;=cell formula&lt;/formula&gt;
			 *                          &lt;value&gt;cell value&lt;/value&gt;
			 *                          &lt;style&gt;cells style&lt;/style&gt;
			 *                          &lt;class&gt;cells class&lt;/class&gt;
			 *                      &lt;/column&gt;
			 *                      &lt;column&gt;&lt;/column&gt;
			 *                  &lt;/columns&gt;
			 *              &lt;/row&gt;
			 *             &lt;row height="15px"&gt;
			 *                  &lt;columns&gt;
			 *                      &lt;column&gt;
			 *                          &lt;formula&gt;=cell formula&lt;/formula&gt;
			 *                          &lt;value&gt;cell value&lt;/value&gt;
			 *                          &lt;style&gt;cells style&lt;/style&gt;
			 *                          &lt;class&gt;cells class&lt;/class&gt;
			 *                      &lt;/column&gt;
			 *                      &lt;column&gt;&lt;/column&gt;
			 *                  &lt;/columns&gt;
			 *              &lt;/row&gt;
			 *         &lt;/rows&gt;
			 *     &lt;/spreadsheet&gt;
			 * &lt;/spreadsheets&gt;
			 * @returns {*|jQuery|HTMLElement} a simple html table
			 * @name xml
			 * @methodOf jQuery.sheet.dts.toTables
			 */
			xml: function(xml) {
				xml = $.parseXML(xml);

				var tables = $([]);

				$.each(xml.childNodes, function(i, spreadsheets) {
					$.each(this.childNodes, function(j,  spreadsheet) {
						var table = $('<table />').attr('title', (this.attributes['title'] ? this.attributes['title'].nodeValue : '')),
							colgroup = $('<colgroup/>').appendTo(table),
							tbody = $('<tbody />').appendTo(table);

						tables = tables.add(table);

						$.each(this.childNodes, function(k, rows){ //rows
							switch (this.nodeName.toLowerCase()) {
								case 'rows':
									$.each(this.childNodes, function(l, row) { //row
										switch (this.nodeName.toLowerCase()) {
											case 'row':
												var tr = $('<tr/>').appendTo(tbody);

												if (this.attributes['height']) {
													tr
														.css('height', (this.attributes['height'] ? this.attributes['height'].nodeValue : ''))
														.attr('height', (this.attributes['height'] ? this.attributes['height'].nodeValue : ''));
												}

												$.each(this.childNodes, function(m, columns) {
													switch (this.nodeName.toLowerCase()) {
														case 'columns':
															$.each(this.childNodes, function(n, column) {
																switch (this.nodeName.toLowerCase()) {
																	case 'column':
																		var td = $('<td />').appendTo(tr);
																		$.each(this.childNodes, function(p, attr) { //formula or value or style
																			switch (this.nodeName.toLowerCase()) {
																				case 'formula':
																					td.data('formula', '=' + (this.textContent || this.text));
																					break
																				case 'value':
																					td.html(this.textContent || this.text);
																					break;
																				case 'style':
																					td.attr('style', this.textContent || this.text);
																					break;
																				case 'class':
																					td.attr('class', this.textContent || this.text);
																			}
																		});
																		break;
																}
															});
													}
												});

												break;

										}
									});
									break;
								case 'metadata':
									$.each(this.childNodes, function() {
										switch (this.nodeName.toLowerCase()) {
											case 'frozenat':
												$.each(this.childNodes, function() {
													switch (this.nodeName.toLowerCase()) {
														case 'row':
															table.data('frozenatrow', (this.textContent || this.text) * 1);
															break;
														case 'col':
															table.data('frozenatcol', (this.textContent || this.text) * 1);
															break;
													}
												});
												break;
											case 'widths':
												$.each(this.childNodes, function() {
													switch (this.nodeName.toLowerCase()) {
														case 'width':
															$('<col/>')
																.attr('width', this.textContent || this.text)
																.css('width', this.textContent || this.text)
																.appendTo(colgroup);
															break;
													}
												});
												break;
										}
									});
									break;
							}
						});
					});
				});

				return tables;
			}
		},

		/**
		 * @namespace
		 * @name fromTables
		 * @memberOf jQuery.sheet.dts
		 */
		fromTables: {
			/**
			 * Create a table from json
			 * @param {Object} jS, required, the jQuery.sheet instance
			 * @returns {Array}  - schema:
			 * [{ // sheet 1, can repeat
			 *  "title": "Title of spreadsheet",
			 *  "metadata": {
			 *      "widths": [
			 *          "120px", //widths for each column, required
			 *          "80px"
			 *      ]
			 *  },
			 *  "rows": [
			 *      { // row 1, repeats for each column of the spreadsheet
			 *          "height": "18px", //optional
			 *          "columns": [
			 *              { //column A
			 *                  "class": "css classes", //optional
			 *                  "formula": "=cell formula", //optional
			 *                  "value": "value", //optional
			 *                  "style": "css cell style" //optional
			 *              },
			 *              {} //column B
			 *          ]
			 *      },
			 *      { // row 2
			 *          "height": "18px", //optional
			 *          "columns": [
			 *              { // column A
			 *                  "class": "css classes", //optional
			 *                  "formula": "=cell formula", //optional
			 *                  "value": "value", //optional
			 *                  "style": "css cell style" //optional
			 *              },
			 *              {} // column B
			 *          ]
			 *      }
			 *  ]
			 * }]
			 * @methodOf jQuery.sheet.dts.fromTables
			 * @name json
			 */
			json: function(jS) {
				var output = [], i = 1 * jS.i;

				for (var sheet in jS.spreadsheets) {
					jS.i = sheet;
					jS.evt.cellEditDone();
					var metadata = [];
					var spreadsheet = {
						"title": (jS.obj.sheet().attr('title') || ''),
						"rows": [],
						"metadata": {
							"widths": [],
							"frozenAt": $.extend({}, jS.frozenAt())
						}
					};
					output.push(spreadsheet);

					for (var row in jS.spreadsheets[sheet]) {
						if (row == 0) continue;
						var parentAttr = jS.spreadsheets[sheet][row][1].td[0].parentNode.attributes,
							Row = {
								"height": null,
								"columns": [],
								"height": (parentAttr['height'] ? parentAttr['height'].value : jS.s.colMargin + 'px')
							};
						spreadsheet.rows.push(Row);

						for (var column in jS.spreadsheets[sheet][row]) {
							if (column == 0) continue;
							var cell = jS.spreadsheets[sheet][row][column],
								Column = {},
								attr = cell.td[0].attributes,
								cl = (attr['class'] ? $.trim(
									(attr['class'].value || '')
										.replace(jS.cl.uiCellActive , '')
										.replace(jS.cl.uiCellHighlighted, '')
								) : ''),
								parent = cell.td[0].parentNode;

							Row.columns.push(Column);

							if (!Row["height"]) {
								Row["height"] = (parent.attributes['height'] ? parent.attributes['height'].value : jS.s.colMargin + 'px');
							}

							if (cell['formula']) Column['formula'] = cell['formula'];
							if (cell['value']) Column['value'] = cell['value'];
							if (attr['style'] && attr['style'].value) Column['style'] = attr['style'].value;

							if (cl.length) {
								Column['class'] = cl;
							}

							if (row * 1 == 1) {
								spreadsheet.metadata.widths.push($(jS.col(null, column)).css('width'));
							}
						}
					}
				}
				jS.i = i;

				return output;
			},

			/**
			 * Create a table from xml
			 * @param {Object} jS, required, the jQuery.sheet instance
			 * @returns {String} - schema:
			 * &lt;spreadsheets&gt;
			 *     &lt;spreadsheet title="spreadsheet title"&gt;
			 *         &lt;metadata&gt;
			 *             &lt;widths&gt;
			 *                 &lt;width&gt;120px&lt;/width&gt;
			 *                 &lt;width&gt;80px&lt;/width&gt;
			 *             &lt;/widths&gt;
			 *         &lt;/metadata&gt;
			 *         &lt;rows&gt;
			 *             &lt;row height="15px"&gt;
			 *                  &lt;columns&gt;
			 *                      &lt;column&gt;
			 *                          &lt;formula&gt;=cell formula&lt;/formula&gt;
			 *                          &lt;value&gt;cell value&lt;/value&gt;
			 *                          &lt;style&gt;cells style&lt;/style&gt;
			 *                          &lt;class&gt;cells class&lt;/class&gt;
			 *                      &lt;/column&gt;
			 *                      &lt;column&gt;&lt;/column&gt;
			 *                  &lt;/columns&gt;
			 *              &lt;/row&gt;
			 *             &lt;row height="15px"&gt;
			 *                  &lt;columns&gt;
			 *                      &lt;column&gt;
			 *                          &lt;formula&gt;=cell formula&lt;/formula&gt;
			 *                          &lt;value&gt;cell value&lt;/value&gt;
			 *                          &lt;style&gt;cells style&lt;/style&gt;
			 *                          &lt;class&gt;cells class&lt;/class&gt;
			 *                      &lt;/column&gt;
			 *                      &lt;column&gt;&lt;/column&gt;
			 *                  &lt;/columns&gt;
			 *              &lt;/row&gt;
			 *         &lt;/rows&gt;
			 *     &lt;/spreadsheet&gt;
			 * &lt;/spreadsheets&gt;
			 * @methodOf jQuery.sheet.dts.fromTables
			 * @name xml
			 */
			xml: function(jS) {
				var output = '<?xml version="1.0" encoding="UTF-8"?><spreadsheets xmlns="http://www.w3.org/1999/xhtml">',
					i = 1 * jS.i;

				for(var sheet in jS.spreadsheets) {
					jS.i = sheet;
					jS.evt.cellEditDone();
					var frozenAt = $.extend({}, jS.frozenAt()),
						widths = [];

					output += '<spreadsheet title="' + (jS.obj.sheet().attr('title') || '') + '">';

					output += '<rows>';
					for(var row in jS.spreadsheets[sheet]) {
						if (row == 0) continue;
						var parentAttr = jS.spreadsheets[sheet][row][1].td[0].parentNode.attributes;
						output += '<row height="' + (parentAttr['height'] ? parentAttr['height'].value : jS.s.colMargin + 'px') + '">';
						output += '<columns>';
						for(var column in jS.spreadsheets[sheet][row]) {
							if (column == 0) continue;

							var cell = jS.spreadsheets[sheet][row][column],
								attr = cell.td[0].attributes,
								cl = (attr['class'] ? $.trim(
									(attr['class'].value || '')
										.replace(jS.cl.uiCellActive, '')
										.replace(jS.cl.uiCellHighlighted, '')
								) : '');

							output += '<column>';

							if (cell.formula) output += '<formula>' + cell.formula + '</formula>';
							if (cell.value) output += '<value>' + cell.value + '</value>';
							if (attr['style']) output += '<style>' + attr['style'].value + '</style>';
							if (cl) output += '<class>' + cl + '</class>';

							output += '</column>';

							if (row * 1 == 1) {
								widths[column] = '<width>' + $(jS.col(null, column)).css('width') + '</width>';
							}
						}
						output += '</columns>';
						output += '</row>';
					}
					output += '</rows>';

					output += '<metadata>' +
						(
							frozenAt.row || frozenAt.col ?
								'<frozenAt>' +
									(frozenAt.row ? '<row>' + frozenAt.row + '</row>' : '') +
									(frozenAt.col ? '<col>' + frozenAt.col + '</col>' : '') +
								'</frozenAt>' :
								''
						) +
						'<widths>' + widths.join('') + '</widths>' +
					'</metadata>';

					output += '</spreadsheet>';
				}

				output += '</spreadsheets>';

				jS.i = i;
				return output;
			}
		}
	};
})(jQuery);