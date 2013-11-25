/**
 * @project jQuery.sheet() The Ajax Spreadsheet - http://code.google.com/p/jquerysheet/
 * @author RobertLeePlummerJr@gmail.com
 * $Id: jquery.sheet.js 717 2013-02-11 14:52:30Z robertleeplummerjr@gmail.com $
 * Licensed under MIT
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

/**
 * @namespace
 * @name jQuery.fn
 */
jQuery.fn.extend({
	/**
	 * @description
	 * The jQuery.sheet plugin
	 * Supports the following jQuery events
	 *
	 * sheetAddRow - occurs just after a row has been added
	 *  arguments: e (jQuery event), jS, i (row index), isBefore, qty
	 *      example:
	 *          $(obj).sheet({
	 *              sheetAddRow: function(e, jS, i, isBefore, qty) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetAddRow', function(e, jS, i, isBefore, qty) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetAddColumn - occurs just after a column has been added
	 *      arguments: e (jQuery event), jS, i (column index), isBefore, qty
	 *      example:
	 *          $(obj).sheet({
	 *              sheetAddColumn: function(e, jS, i, isBefore, qty) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetAddColumn', function(e, jS, i, isBefore, qty) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetSwitch - occurs after a spreadsheet has been switched
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (spreadsheet index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetSwitch: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetSwitch', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetRename - occurs just after a spreadsheet is renamed, to obtain new title jS.obj.sheet().attr('title');
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (spreadsheet index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetRename: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetRename', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetTabSortStart - occurs at the beginning of a sort for moving a spreadsheet around in order
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), E (jQuery sortable event), ui, (jQuery ui event)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetTabSortStart: function(e, jS, E, ui) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetTabSortStart', function(e, jS, E, ui) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetTabSortUpdate - occurs after a sort of a spreadsheet has been completed
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), E (jQuery sotable event), ui, (jQuery ui event), i (original index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetTabSortUpdate: function(e, jS, E, ui) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetTabSortUpdate', function(e, jS, E, ui) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetFormulaKeydown - occurs just after keydown on either inline or static formula
	 *      arguments: e (jQuery event)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetFormulaKeydown: function(e) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetFormulaKeydown') {
	 *
	 *          })
	 *          .sheet();
	 * sheetCellEdit - occurs just before a cell has been a cell is started to edit
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), cell (jQuery.sheet.instance.spreadsheet cell)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetCellEdit: function(e, jS, cell) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetCellEdit', function(e, jS, cell) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetCellEdited - occurs just after a cell has been updated
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), cell (jQuery.sheet.instance.spreadsheet cell)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetCellEdited: function(e, jS, cell) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetCellEdited', function(e, jS, cell) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetCalculation - occurs just after a spreadsheet has been fully calculated
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetCalculation: function(e, jS) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetCalculation', function(e, jS) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetAdd - occurs just after a spreadsheet has been added
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (new sheet index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetAdd: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetAdd', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetDelete - occurs just after a spreadsheet has been deleted
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (old sheet index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetDelete: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetDelete', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetDeleteRow - occurs just after a row has been deleted
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (old row index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetDeleteRow: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetDeleteRow', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetDeleteColumn - occurs just after a column as been deleted
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (old column index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetDeleteColumn: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetDeleteColumn', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetOpen - occurs just after a single sheet within a set of sheets has been opened, this is triggered when calling sheet, so it needs to be bound beforehand
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), i (new sheet index)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetOpen: function(e, jS, i) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetOpen', function(e, jS, i) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetAllOpened - occurs just after all sheets have been loaded and complete user interface has been created, this is triggered when calling sheet, so it needs to be bound beforehand
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetAllOpened: function(e, jS) {
	 *
	 *              }
	 *          });
	 *      or:
	 *          $(obj).bind('sheetAllOpened', function(e, jS) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetSave - an assistance event called when calling jS.toggleState(), but not tied to anything internally
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), tables (tables from spreadsheet)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetSave: function(e, jS, tables) {
	 *
	 *              });
	 *          }
	 *      or:
	 *          $(obj).bind('sheetSave', function(e, jS, tables) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * sheetFullScreen - triggered when the sheet goes full screen
	 *      arguments: e (jQuery event), jS (jQuery.sheet instance), isFullScreen (boolean, true if full screen, false if not)
	 *      example:
	 *          $(obj).sheet({
	 *              sheetFullScreen: function(e, jS, isFullScreen) {
	 *
	 *              });
	 *          }
	 *      or:
	 *          $(obj).bind('sheetFullScreen', function(e, jS, isFullScreen) {
	 *
	 *          })
	 *          .sheet();
	 *
	 * @name sheet
	 * @param {Object} settings supports the following properties/methods:
	 *
	 * editable {Boolean}, default true, Makes the sheet editable or viewable
	 *
	 * editableNames {Boolean}, default true, Allows sheets to have their names changed, depends on settings.editable being true
	 *
	 * barMenus {Boolean}, default true, Turns bar menus on/off
	 *
	 * freezableCells {Boolean}, default true, Turns ability to freeze cells on/off
	 *
	 * allowToggleState {Boolean}, default true, allows the spreadsheet to be toggled from write/read
	 *
	 * newColumnWidth {Integer}, default 120, width of new columns
	 *
	 * title {String|Function}, title of spreadsheet, if function, expects string and is sent jS
	 *
	 * menuRight {String|Function}, default '', if function expects string and is sent jS. If ul object as string, will attempt to create menu
	 *
	 * menuLeft {String|Function}, default '', if function expects string and is sent jS. If ul object as string, will attempt to create menu
	 *
	 * calcOff {Boolean} default false, turns turns off ability to calculate
	 *
	 * log {Boolean} turns on/off debug mode
	 *
	 * lockFormulas {Boolean} default false, turns on/off the ability to edit formulas
	 *
	 * colMargin {Integer} default 18, size of height of new cells, and width of cell bars
	 *
	 * boxModelCorrection {Integer} default 2, if box model is detected, it adds these pixels to ensure the size of the spreadsheet controls are correct
	 *
	 * formulaFunctions {Object} default {}, Additional functions for formulas. Will overwrite default functions if named the same.
	 *      Javascript Example:
	 *          $(obj).sheet({
	 *              formulaFunctions: {
	 *                  NEWFUNCTION: function(arg1, arg2) {
	 *                      //this = the parser's cell object object
	 *                      return 'string'; //can return a string
	 *                      return { //can also return an object {value: '', html: ''}
	 *                          value: 'my value seen by other cells or if accessed directly',
	 *                          html: $('What the end user will see on the cell this is called in')
	 *                      }
	 *                  }
	 *              }
	 *          });
	 *
	 *      Formula Example:
	 *          =NEWFUNCTION(A1:B1, C3);
	 *
	 * formulaVariables {Object} default {}, Additional variables that formulas can access.
	 *      Javascript Example:
	 *          $(obj).sheet({
	 *              formulaVariables: {
	 *                  newVariable: 100
	 *              }
	 *          });
	 *
	 *      Formula Example (will output 200)
	 *          =newVariable + 100
	 *
	 * cellSelectModel {String} default 'excel', accepts 'excel', 'oo', or 'gdrive', makes the select model act differently
	 *
	 * autoAddCells {Boolean} default true, allows you to add cells by selecting the last row/column and add cells by pressing either tab (column) or enter (row)
	 *
	 * resizableCells {Boolean} default true, turns resizing on and off for cells, depends on jQuery ui
	 *
	 * resizableSheet {Boolean} default true, turns resizing on and off for sheet, depends on jQuery ui
	 *
	 * autoFiller {Boolean} default true, turns on/off the auto filler, the little square that follows the active cell around that you can drag and fill the values of other cells in with.
	 *
	 * minSize {Object} default {rows: 1, cols: 1}, the minimum size of a spreadsheet
	 *
	 * alertFormulaErrors {Boolean} default false, if true triggers jS.alertFormulaError, which alerts the end user of an error via an alert
	 *
	 * error {Function} default function(e) { return e.error; }, is triggered on errors from the formula engine
	 *
	 * encode {Function} default is a special characters handler for strings only, is a 1 way encoding of the html if entered manually by the editor.  If you want to use html with a function, return an object rather than a string
	 *
	 * frozenAt {Object} default [{row: 0,col: 0}], Gives the ability to freeze cells at a certain row/col
	 *
	 * contextmenuTop {Object} default is standard list of commands for context menus when right click or click on menu dropdown
	 *      Javascript example:
	 *          {
	 *              "What I want my command to say": function() {}
	 *          }
	 *
	 * contextmenuLeft {Object} default is standard list of commands for context menus when right click
	 *      Javascript example:
	 *          {
	 *              "What I want my command to say": function() {}
	 *          }
	 *
	 * contextmenuCell {Object} default is standard list of commands for context menus when right click or click on menu dropdown
	 *      Javascript example:
	 *          {
	 *              "What I want my command to say": function() {}
	 *          }
	 *
	 * hiddenRows {Array} default [], Hides certain rows from being displayed initially. [sheet Index][row index]. example: [[1]] hides first row in first spreadsheet; [[],[1]] hides first row in second spreadsheet
	 *
	 * hiddenColumns {Array} default [], Hides certain columns from being displayed initially. [sheet Index][column index]. example: [[1]] hides first column in first spreadsheet; [[],[1]] hides first column in second spreadsheet
	 *
	 * @methodOf jQuery.fn
	 * @namespace
	 *
	 */
	sheet:function (settings) {
		settings = settings || {};
		jQuery(this).each(function () {
			var me = jQuery(this),
				defaults = {
					editable:true,
					editableNames:true,
					barMenus:true,
					freezableCells:true,
					allowToggleState:true,
					menuLeft:null,
					newColumnWidth:120,
					title:null,
					menuRight:null,
					calcOff:false,
					log:false,
					lockFormulas:false,
					parent:me,
					colMargin:18,
					boxModelCorrection:2,
					formulaFunctions:{},
					formulaVariables:{},
					cellSelectModel:'excel',
					autoAddCells:true,
					resizableCells:true,
					resizableSheet:true,
					autoFiller:true,
					minSize:{rows:1, cols:1},
					alertFormulaErrors:false,
					error:function (e) {
						return e.error;
					},
					encode:function (val) {
						switch (typeof val) {
							case 'object':
								return val;
							case 'number':
								return Globalize.format(val).replace(/[\.,]00$/, "");
						}

						if (!val) {
							return val || '';
						}
						if (!val.replace) {
							return val || '';
						}
						var num = $.trim(val) * 1;
						if (!isNaN(num)) {
							return Globalize.format(num).replace(/[\.,]00$/, "");
						}

						return val
							.replace(/&/gi, '&amp;')
							.replace(/>/gi, '&gt;')
							.replace(/</gi, '&lt;')
							.replace(/\n/g, '\n<br>')
							.replace(/\t/g, '&nbsp;&nbsp;&nbsp ')
							.replace(/  /g, '&nbsp; ');
					},
					frozenAt:[],
					contextmenuTop:{
						"Toggle freeze columns to here":function (jS) {
							var col = jS.getTdLocation(jS.obj.cellActive()).col;
							jS.frozenAt().col = (jS.frozenAt().col == col ? 0 : col);
						},
						"Insert column after":function (jS) {
							jS.controlFactory.addColumn(jS.colLast);
							return false;
						},
						"Insert column before":function (jS) {
							jS.controlFactory.addColumn(jS.colLast, true);
							return false;
						},
						"Add column to end":function (jS) {
							jS.controlFactory.addColumn();
							return false;
						},
						"Delete this column":function (jS) {
							jS.deleteColumn();
							return false;
						},
						"Hide column":function (jS) {
							jS.toggleHide.column();
							return false;
						}
					},
					contextmenuLeft:{
						"Toggle freeze rows to here":function (jS) {
							var row = jS.getTdLocation(jS.obj.cellActive()).row;
							jS.frozenAt().row = (jS.frozenAt().row == row ? 0 : row);
						},
						"Insert row after":function (jS) {
							jS.controlFactory.addRow(jS.rowLast);
							return false;
						},
						"Insert row before":function (jS) {
							jS.controlFactory.addRow(jS.rowLast, true);
							return false;
						},
						"Add row to end":function (jS) {
							jS.controlFactory.addRow();
							return false;
						},
						"Delete this row":function (jS) {
							jS.deleteRow();
							return false;
						},
						"Hide row":function (jS) {
							jS.toggleHide.row();
							return false;
						}
					},
					contextmenuCell:{
						"Copy":false,
						"Cut":false,
						"Insert column after":function (jS) {
							jS.controlFactory.addColumn(jS.colLast);
							return false;
						},
						"Insert column before":function (jS) {
							jS.controlFactory.addColumn(jS.colLast, true);
							return false;
						},
						"Add column to end":function (jS) {
							jS.controlFactory.addColumn();
							return false;
						},
						"Delete this column":function (jS) {
							jS.deleteColumn();
							return false;
						},
						"line1":"line",
						"Insert row after":function (jS) {
							jS.controlFactory.addRow();
							return false;
						},
						"Insert row before":function (jS) {
							jS.controlFactory.addRow(jS.rowLast, true);
							return false;
						},
						"Add row to end":function (jS) {
							jS.controlFactory.addRow();
							return false;
						},
						"Delete this row":function (jS) {
							jS.deleteRow();
							return false;
						},
						"line2":'line',
						"Add spreadsheet":function (jS) {
							jS.addSheet('5x10');
						},
						"Delete spreadsheet":function (jS) {
							jS.deleteSheet();
						}
					},
					hiddenRows:[],
					hiddenColumns:[],
					cellStartingHandlers: {
						'$':function(val, ch) {
							this.formula = '';
							this.value = val;
							this.valueOverride = jFN.DOLLAR.apply(this, [val.substring(1).replace(jS.s.numberGroupingChar, ''), 2, ch || '$']).value;
							this.td
								.removeData('formula')
								.html(val);
						},
						'£':function(val) {
							jS.s.cellStartingHandlers['$'].apply(this, [val, '£']);
						}
					},
					radixPointChar: '.',
					numberGroupingChar: ','
				},
				events = jQuery.sheet.events;

			//destroy already existing spreadsheet
			var jS = me.getSheet();
			if (jS) {
				var tables = me.children().detach();
				jS.kill();
				me.html(tables);

				for (var i in events) {
					if (settings[events[i]]) me.unbind(events[i]);
				}
			}

			for (var i in events) {
				if (settings[events[i]]) me.bind(events[i], settings[events[i]]);
			}

			if (!jQuery.sheet.instance.length) jQuery.sheet.instance = $([]);

			jS = jQuery.sheet.createInstance(jQuery, jQuery.extend(defaults, settings), jQuery.sheet.instance.length);
			jQuery.sheet.instance = jQuery.sheet.instance.add(jS);
		});
		return this;
	},

	/**
	 * @memberOf jQueryPlugins
	 * @returns {*}
	 */
	disableSelectionSpecial:function () {
		this.each(function () {
			this.onselectstart = function () {
				return false;
			};
			this.unselectable = "on";
			jQuery(this).css('-moz-user-select', 'none');
		});
		return this;
	},

	/**
	 * @memberOf jQueryPlugins
	 * @returns {*}
	 */
	getSheet:function () {
		return jQuery(this).data('sheetInstance');
	},

	/**
	 * Get cell value
	 * @memberOf jQueryPlugins
	 * @param row
	 * @param col
	 * @param sheet
	 * @returns {*}
	 */
	getCellValue:function (row, col, sheet) {
		var jS = jQuery(this).getSheet();
		sheet = (sheet ? sheet : 0);
		try {
			return jS.updateCellValue(sheet, row, col);
		} catch (e) {
			return "";
		}
	},

	/**
	 * Set cell value
	 * @memberOf jQueryPlugins
	 * @param value
	 * @param row
	 * @param col
	 * @param sheet
	 */
	setCellValue:function (value, row, col, sheet) {
		var jS = jQuery(this).getSheet();
		sheet = (sheet ? sheet : 0);
		try {
			jS.spreadsheets[sheet][row][col].value = value;
			return jS.updateCellValue(sheet, row, col);
		} catch (e) {
		}
	},

	/**
	 * Set cell formula
	 * @memberOf jQueryPlugins
	 * @param formula
	 * @param row
	 * @param col
	 * @param sheet
	 */
	setCellFormula:function (formula, row, col, sheet) {
		var jS = jQuery(this).getSheet();
		sheet = (sheet ? sheet : 0);
		try {
			jS.spreadsheets[sheet][row][col].formula = formula;
			return jS.updateCellValue(sheet, row, col);
		} catch (e) {
		}
	},

	/**
	 * Set cell html
	 * @memberOf jQueryPlugins
	 * @param html
	 * @param row
	 * @param col
	 * @param sheet
	 */
	setCellHtml:function (html, row, col, sheet) {
		var jS = jQuery(this).getSheet();
		sheet = (sheet ? sheet : 0);
		try {
			jS.spreadsheets[sheet][row][col].html = [html];
			return jS.updateCellValue(sheet, row, col);
		} catch (e) {
		}
	},

	/**
	 * Detect if spreadsheet is full screen
	 * @memberOf jQueryPlugins
	 * @return {Boolean}
	 */
	isSheetFullScreen:function () {
		var jS = $(this).getSheet();
		if (jS.obj.fullScreen().is(':visible')) {
			return true;
		} else {
			return false;
		}
	},

	/**
	 * Get inputs serialized from spreadsheet type_sheet-index_row-index_column-index_instance-index (dropdown_0_1_1_0 = sheet 1, row 1, column A, instance 0
	 * @param {Boolean} array, return serialized as array (true) or string (false, default false
	 * @methodOf jQueryPlugins
	 * @returns {*}
	 */
	serializeCellInputs:function (array) {
		var jS = $(this).getSheet(),
			inputs = jS.obj.sheets().find(':input');
		if (array) {
			return inputs.serializeArray();
		} else {
			return inputs.serialize();
		}
	}
});

/**
 * @namespace
 * @type {Object}
 */
jQuery.sheet = {
	/**
	 * Array of instances of jQuery.sheet, generally short-handed to jS
	 * @namespace
	 * @memberOf jQuery.sheet
	 */
	instance:[],

	dependencies:{
		coreCss:{css:'jquery.sheet.css'},
		globalize:{script:'plugins/globalize.js'},
		formulaParser:{script:'parser/formula/formula.js'},
		tsvParser:{script:'parser/tsv/tsv.js'},
		mousewheel:{script:'plugins/jquery.mousewheel.min.js'},
		nearest:{script:'plugins/jquery.nearest.min.js'}
	},
	optional:{
		globalizeCultures:{script:'plugins/globalize.cultures.js'},
		raphael:{script:'plugins/raphael-min.js'},
		gRaphael:{script:'plugins/g.raphael-min.js'},
		colorPicker:{css:'plugins/jquery.colorPicker.css'},
		colorPicker:{script:'plugins/jquery.colorPicker.min.js'},
		elastic:{script:'plugins/jquery.elastic.min.js'},
		advancedfn:{script:'plugins/jquery.sheet.advancedfn.js'},
		financefn:{script:'plugins/jquery.sheet.financefn.js'},
		dts:{script:'plugins/jquery.sheet.dts.js'},
		zeroclipboard:{script:'plugins/ZeroClipboard.js'}
	},

	/**
	 * events list
	 * @memberOf jQuery.sheet
	 */
	events:['sheetAddRow', 'sheetAddColumn', 'sheetSwitch', 'sheetRename', 'sheetTabSortStart', 'sheetTabSortUpdate', 'sheetCellEdit', 'sheetCellEdited', 'sheetCalculation', 'sheetAdd', 'sheetDelete', 'sheetDeleteRow', 'sheetDeleteColumn', 'sheetOpen', 'sheetAllOpened', 'sheetSave', 'sheetFullScreen', 'sheetFormulaKeydown'],

	preLoad:function (path, settings) {
		path = path || '';
		settings = $.extend({
			skip: ['globalizeCultures']
		},settings)


		var g = function () {
			if (this.script) {
				document.write('<script src="' + path + this.script + '"></script>');
			} else if (this.css) {
				document.write('<link rel="stylesheet" type="text/css" href="' + path + this.css + '"></link>');
			}
		};

		for(var i in settings.skip) {
			if (this.dependencies[settings.skip[i]]) {
				this.dependencies[settings.skip[i]] = null;
			}
			if (this.optional[settings.skip[i]]) {
				this.optional[settings.skip[i]] = null;
			}
		}

		$.each(this.dependencies, function () {
			g.apply(this);
		});

		$.each(this.optional, function () {
			g.apply(this);
		});
	},


	repeat:function (str, num) {
		var result = '';
		while (num > 0) {
			if (num & 1) result += str;
			num >>= 1, str += str;
		}
		return result;
	},


	nthCss:function (elementName, parentSelectorString, me, indexes, min, css) {
		var style = [];
		css = css || '{display: none;}';
		if (me.styleSheet) { //IE compatibility
			for (var index in indexes) {
				if (indexes[index] > min) {
					style.push(parentSelectorString + ' ' + elementName + ':first-child' + jQuery.sheet.repeat('+' + elementName, indexes[index] - 1));
				}
			}
			if (style.length) {
				return style.join(',') + css;
			}
		} else {
			for (var index in indexes) {
				if (indexes[index] > min) {
					style.push(parentSelectorString + ' ' + elementName + ':nth-child(' + indexes[index] + ')');
				}
			}
			if (style.length) {
				return style.join(',') + css;
			}
		}

		return '';
	},

	/**
	 * The instance creator of jQuery.sheet
	 * @methodOf jQuery.sheet
	 * @param {Object} $ jQuery
	 * @param {Object} s settings from jQuery.fn.sheet
	 * @param {Integer} I the index of the instance
	 * @returns {Object} jS jQuery sheet instance
	 */
	createInstance:function ($, s, I) {

		/**
		 * A single instance of a spreadsheet, shorthand, also accessible from jQuery.sheet.instance[index]
		 * @name jS
		 * @namespace
		 * @type {Object}
		 */
		var jS = {
			/**
			 * Current version of jQuery.sheet
			 * @memberOf jS
			 * @name version
			 * @type {String}
			 */
			version:'3.0',

			/**
			 * The active sheet index within the a set of sheets
			 * @memberOf jS
			 * @name i
			 * @type {Integer}
			 */
			i:0,

			/**
			 * The instance index
			 * @memberOf jS
			 * @name I
			 * @type {Integer}
			 */
			I:I,

			/**
			 * The current count of sheet's within the instance
			 * @memberOf jS
			 * @name sheetCount
			 * @type {Integer}
			 */
			sheetCount:0,

			/**
			 * The current scrolled area, col.start, col.end, row.start, row.end
			 * @memberOf jS
			 * @named scrolledArea
			 */
			scrolledArea:[],

			/**
			 * The internal storage array of the spreadsheets for an instance, constructed as array 3 levels deep, spreadsheet, rows, cells, can easily be used for custom exporting/saving
			 * @memberOf jS
			 * @name spreadsheets
			 * @type {Array}
			 */
			spreadsheets:[],

			/**
			 * Internal storage array of controls for an instance
			 * @memberOf jS
			 * @name controls
			 */
			controls:{
				autoFiller:[],
				bar:{
					helper:[],
					corner:[],
					x:{
						controls:[],
						handleFreeze:[],
						menu:[],
						menuParent:[],
						parent:[],
						scroll:[],
						td:[],
						tds:function () {
							var tds = $([]);
							for (var i in this.td[jS.i]) {
								tds = tds.add(this.td[jS.i][i]);
							}
							return tds;
						}
					},
					y:{
						controls:[],
						handleFreeze:[],
						menu:[],
						parent:[],
						scroll:[],
						td:[],
						tds:function () {
							var tds = $([]);
							for (var i in this.td[jS.i]) {
								tds = tds.add(this.td[jS.i][i]);
							}
							return tds;
						}
					}
				},
				barMenuLeft:[],
				barMenuTop:[],
				barLeft:[],
				barTop:[],
				barTopParent:[],
				chart:[],
				cellMenu:[],
				enclosure:[],
				enclosures:null,
				formula:null,
				fullScreen:[],
				header:null,
				inPlaceEdit:[],
				label:null,
				menuLeft:[],
				menuRight:[],
				pane:[],
				panes:null,
				scroll:[],
				scrolls:null,
				sheet:[],
				sheets:null,
				tab:[],
				tabContainer:null,
				tabs:null,
				title:null,
				toggleHide:{
					x:[],
					y:[]
				},
				ui:null
			},

			/**
			 * Object selectors for interacting with a spreadsheet, dynamically id'd from both sheet index and instance index
			 * @memberOf jS
			 * @name obj
			 * @type {Object}
			 */
			obj:{
				autoFiller:function () {
					return jS.controls.autoFiller[jS.i] || $([]);
				},
				barCorner:function () {
					return jS.controls.bar.corner[jS.i] || $([]);
				},
				barHelper:function () {
					return jS.controls.bar.helper[jS.i] || (jS.controls.bar.helper[jS.i] = $([]));
				},
				barLeft:function (i) {
					return (jS.controls.bar.y.td[jS.i] && jS.controls.bar.y.td[jS.i][i] ? jS.controls.bar.y.td[jS.i][i] : $([]));
				},
				barLeftControls:function () {
					return jS.controls.bar.y.controls[jS.i] || $([]);
				},
				barLefts:function () {
					return jS.controls.bar.y.tds();
				},
				barHandleFreezeLeft:function () {
					return jS.controls.bar.y.handleFreeze[jS.i] || $([]);
				},
				barMenuLeft:function () {
					return jS.controls.bar.y.menu[jS.i] || $([]);
				},
				barTop:function (i) {
					return (jS.controls.bar.x.td[jS.i] && jS.controls.bar.x.td[jS.i][i] ? jS.controls.bar.x.td[jS.i][i] : $([]));
				},
				barTopControls:function () {
					return jS.controls.bar.x.controls[jS.i] || $([]);
				},
				barTops:function () {
					return jS.controls.bar.x.tds();
				},
				barTopParent:function () {
					return jS.controls.bar.x.parent[jS.i] || $([]);
				},
				barHandleFreezeTop:function () {
					return jS.controls.bar.x.handleFreeze[jS.i] || $([]);
				},
				barMenuParentTop:function () {
					return jS.controls.bar.x.menuParent[jS.i] || $([]);
				},
				barMenuTop:function () {
					return jS.controls.bar.x.menu[jS.i] || $([]);
				},
				cellActive:function () {
					return jS.cellLast.td || $([]);
				},
				cellMenu:function () {
					return jS.controls.cellMenu[jS.i] || $([]);
				},
				cellHighlighted:function () {
					return jS.highlightedLast.td || $([]);
				},
				chart:function () {
					return jS.controls.chart[jS.i] || $([]);
				},
				enclosure:function () {
					return jS.controls.enclosure[jS.i] || $([]);
				},
				enclosures:function () {
					return jS.controls.enclosures || $([]);
				},
				formula:function () {
					return jS.controls.formula || $([]);
				},
				fullScreen:function () {
					return jS.controls.fullScreen[jS.i] || $([]);
				},
				header:function () {
					return jS.controls.header || $([]);
				},
				menuRight:function () {
					return jS.controls.menuRight[jS.i] || $([]);
				},
				inPlaceEdit:function () {
					return jS.controls.inPlaceEdit[jS.i] || $([]);
				},
				label:function () {
					return jS.controls.label || $([]);
				},
				menuLeft:function () {
					return jS.controls.menuLeft[jS.i] || $([]);
				},
				pane:function () {
					return jS.controls.pane[jS.i] || $([]);
				},
				panes:function () {
					return jS.controls.panes || $([]);
				},
				parent:function () {
					return s.parent;
				},
				scrollStyleX:function () {
					return jS.controls.bar.x.scroll[jS.i] || $([]);
				},
				scrollStyleY:function () {
					return jS.controls.bar.y.scroll[jS.i] || $([]);
				},
				scroll:function () {
					return jS.controls.scroll[jS.i] || $([]);
				},
				scrolls:function () {
					return jS.controls.scrolls || $([]);
				},
				sheet:function () {
					return jS.controls.sheet[jS.i] || $([]);
				},
				sheets:function () {
					return jS.controls.sheets || $([]);
				},
				tab:function () {
					return jS.controls.tab[jS.i] || $([]);
				},
				tabs:function () {
					return jS.controls.tabs || $([]);
				},
				tabContainer:function () {
					return jS.controls.tabContainer || $([]);
				},
				toggleHideStyleX:function () {
					return jS.controls.toggleHide.x[jS.i] || $([]);
				},
				toggleHideStyleY:function () {
					return jS.controls.toggleHide.y[jS.i] || $([]);
				},
				title:function () {
					return jS.controls.title || $([]);
				},
				ui:function () {
					return jS.controls.ui || $([]);
				}
			},

			/**
			 * Internal id's of objects, dynamically id'd from both sheet index and instance index
			 * @memberOf jS
			 * @name id
			 * @type {Object}
			 */
			id:{
				sheet:'jS_' + I + '_'
			},

			/**
			 * Internal css classes of objects
			 * @memberOf jS
			 * @name cl
			 * @type {Object}
			 */
			cl:{
				/*
				 cl = class references
				 */
				autoFiller:'jSAutoFiller',
				autoFillerHandle:'jSAutoFillerHandle',
				autoFillerCover:'jSAutoFillerCover',
				barCorner:'jSBarCorner',
				barController:'jSBarController',
				barHelper:'jSBarHelper',
				barLeft:'jSBarLeft',
				barHandleFreezeLeft:'jSBarHandleFreezeLeft',
				barTop:'jSBarTop',
				barHandleFreezeTop:'jSBarHandleFreezeTop',
				barTopParent:'jSBarTopParent',
				chart:'jSChart',
				formula:'jSFormula',
				formulaParent:'jSFormulaParent',
				header:'jSHeader',
				fullScreen:'jSFullScreen',
				inPlaceEdit:'jSInPlaceEdit',
				menu:'jSMenu',
				menuFixed:'jSMenuFixed',
				parent:'jSParent',
				scroll:'jSScroll',
				sheet:'jS',
				label:'jSLoc',
				pane:'jSEditPane',
				tab:'jSTab',
				tabContainer:'jSTabContainer',
				title:'jSTitle',
				enclosure:'jSEnclosure',
				ui:'jSUI',
				uiAutoFiller:'ui-state-active',
				uiBar:'ui-widget-header',
				uiBarHighlight:'ui-state-active',
				uiBarHandleFreezeLeft:'ui-state-default',
				uiBarHandleFreezeTop:'ui-state-default',
				uiBarMenuTop:'ui-state-default',
				uiCellActive:'ui-state-active',
				uiCellHighlighted:'ui-state-highlight',
				uiControl:'ui-widget-header ui-corner-top',
				uiControlTextBox:'ui-widget-content',
				uiFullScreen:'ui-widget-content ui-corner-all',
				uiInPlaceEdit:'ui-state-highlight',
				uiMenu:'ui-widget-header',
				uiMenuUl:'ui-widget-header',
				uiMenuLi:'ui-widget-header',
				uiParent:'ui-widget-content ui-corner-all',
				uiSheet:'ui-widget-content',
				uiTab:'ui-widget-header',
				uiTabActive:'ui-state-highlight'
			},

			/**
			 * Messages for user interface
			 * @memberOf jS
			 * @name msg
			 * @type {Object}
			 */
			msg:{
				addRowMulti:"How many rows would you like to add?",
				addColumnMulti:"How many columns would you like to add?",
				cellFind:"What are you looking for in this spreadsheet?",
				cellNoFind:"No results found.",
				dragToFreezeCol:"Drag to freeze column",
				dragToFreezeRow:"Drag to freeze row",
				newSheet:"What size would you like to make your spreadsheet? Example: '5x10' creates a sheet that is 5 columns by 10 rows.",
				openSheet:"Are you sure you want to open a different sheet?  All unsaved changes will be lost.",
				toggleHideRow:"No row selected.",
				toggleHideColumn:"Now column selected.",
				loopDetected:"Loop Detected",
				newSheetTitle:"What would you like the sheet's title to be?",
				notFoundColumn:"Column not found",
				notFoundRow:"Row not found",
				notFoundSheet:"Sheet not found",
				setCellRef:"Enter the name you would like to reference the cell by.",
				sheetTitleDefault:"Spreadsheet {index}"
			},

			/**
			 * Deletes a jQuery sheet instance
			 * @methodOf jS
			 * @name kill
			 */
			kill:function () {
				$document.unbind('keydown');
				jS.obj.fullScreen().remove();
				jS.obj.inPlaceEdit().trigger('destroy');
				s.parent
					.removeClass(jS.cl.uiParent)
					.html('')
					.removeData('sheetInstance');

				for (var i in $.sheet.events) {
					s.parent.unbind($.sheet.events[i]);
				}

				$.sheet.instance[I] = null;
				jS = null;
			},

			/**
			 * Event trigger for jQuery sheet, wraps jQuery's trigger event to always return jS
			 * @param {String} eventType event type
			 * @param {Array} extraParameters optional
			 * @methodOf jS
			 * @name trigger
			 */
			trigger:function (eventType, extraParameters) {
				//wrapper for $ trigger of parent, in case of further mods in the future
				extraParameters = extraParameters || [];
				s.parent.trigger(eventType, [jS].concat(extraParameters));
			},

			/**
			 * Returns all spreadsheets within an instance as an array, builds it if it doesn't exist
			 * @param forceRebuild
			 * @returns {Array|spreadsheets}
			 * @methodOf jS
			 * @name spreadsheetsToArray
			 */
			spreadsheetsToArray:function (forceRebuild) {
				if (forceRebuild || jS.spreadsheets.length == 0) {
					jS.cycleCellsAll(function (sheet, row, col) {
						var td = $(this);
						jS.createCell(td, sheet, row, col, td.text(), td.data('formula'));
					});
				}
				return jS.spreadsheets;
			},

			/**
			 * Returns singe spreadsheet from a set of spreadsheets within as instance, builds if it doesn't exist
			 * @param {Boolean} forceRebuild Enforces the spreadsheet to be rebuilt
			 * @param {Integer} i Spreadsheet index
			 * @methodOf jS
			 * @name spreadsheetToArray
			 */
			spreadsheetToArray:function (forceRebuild, i) {
				i = (i ? i : jS.i);
				if (forceRebuild || !jS.spreadsheets[i]) {
					jS.cycleCells(function (sheet, row, col) {
						var td = $(this);
						jS.createCell(td, sheet, row, col, td.text(), td.data('formula'));
					});
				}
			},

			/**
			 * Creates a single cell within
			 * @param {jQuery|HTMLElement} td td object
			 * @param {Integer} sheet
			 * @param {Integer} row
			 * @param {Integer} col
			 * @param {String} value
			 * @param {String} formula
			 * @param {Integer} calcCount
			 * @param {Date} calcLast
			 * @param {Date} calcDependenciesLast
			 * @returns {Object} cell
			 * @methodOf jS
			 * @name createCell
			 */
			createCell:function (td, sheet, row, col, value, formula, calcCount, calcLast, calcDependenciesLast) {
				//first create cell
				if (!jS.spreadsheets[sheet]) jS.spreadsheets[sheet] = [];
				if (!jS.spreadsheets[sheet][row]) jS.spreadsheets[sheet][row] = [];

				jS.spreadsheets[sheet][row][col] = {
					td:td,
					formula:formula || '',
					value:value || '',
					calcCount:calcCount || 0,
					calcLast:calcLast || -1,
					calcDependenciesLast:calcDependenciesLast || -1,
					html:[],
					sheet:sheet
				};

				//now create row
				if (!jS.controls.bar.y.td[sheet]) jS.controls.bar.y.td[sheet] = [];
				if (!jS.controls.bar.y.td[sheet][row]) {
					jS.controls.bar.y.td[sheet][row] = td.parent().children().first();
				}

				//now create column
				if (!jS.controls.bar.x.td[sheet]) jS.controls.bar.x.td[sheet] = [];
				if (!jS.controls.bar.x.td[sheet][col]) {
					jS.controls.bar.x.td[sheet][col] = $(td[0].parentNode.parentNode.children[0].children[col]);
				}

				//return cell
				return jS.spreadsheets[sheet][row][col];
			},

			/**
			 * Tracks which spreadsheet is active to intercept keystrokes for navigation
			 * @type {Boolean}
			 * @memberOf jS
			 * @name nav
			 */
			nav:false,

			/**
			 * Turns off all intercept keystroke navigation instances, with exception of supplied instance index
			 * @param {Integer} nav Instance index
			 * @methodOf jS
			 * @name setNav
			 */
			setNav:function (nav) {
				$.sheet.instance.each(function () {
					this.nav = false;
				});

				jS.nav = nav;
			},

			/**
			 * Creates the different objects required by sheets
			 * @memberOf jS
			 * @name controlFactory
			 * @type {Object}
			 * @namespace
			 */
			controlFactory:{
				/**
				 * Creates multi rows
				 * @param {Integer} i, optional, row index
				 * @param {Integer} qty the number of cells you'd like to add, if not specified, a dialog will ask
				 * @param {Boolean} isBefore places cells before the selected cell if set to true, otherwise they will go after, or at end
				 * @param {Boolean} skipFormulaReparse re-parses formulas if needed
				 * @methodOf jS.controlFactory
				 * @name addRowMulti
				 */
				addRowMulti:function (i, qty, isBefore, skipFormulaReparse) {
					if (!qty) {
						qty = prompt(jS.msg.addRowMulti);
					}
					if (qty) {
						if (!isNaN(qty)) {
							jS.controlFactory.addCells(i, isBefore, parseInt(qty), 'row', skipFormulaReparse);
							jS.trigger('sheetAddRow', [i, isBefore, qty]);
						}
					}
				},

				/**
				 * Creates multi columns
				 * @param {Integer} i, optional, column index
				 * @param {Integer} qty the number of cells you'd like to add, if not specified, a dialog will ask
				 * @param {Boolean} isBefore places cells before the selected cell if set to true, otherwise they will go after, or at end
				 * @param {Boolean} skipFormulaReparse re-parses formulas if needed
				 * @methodOf jS.controlFactory
				 * @name addColumnMulti
				 */
				addColumnMulti:function (i, qty, isBefore, skipFormulaReparse) {
					if (!qty) {
						qty = prompt(jS.msg.addColumnMulti);
					}
					if (qty) {
						if (!isNaN(qty)) {
							jS.controlFactory.addCells(i, isBefore, parseInt(qty), 'col', skipFormulaReparse);
							jS.trigger('sheetAddColumn', [i, isBefore, qty]);
						}
					}
				},

				/**
				 * Creates cells for sheet and the bars that go along with them
				 * @param {Integer} i optional, index where cells should be added, if null, cells go to end
				 * @param {Boolean} isBefore places cells before the selected cell if set to true, otherwise they will go after, or at end;
				 * @param {Integer} qty how many rows/columsn to add
				 * @param {String} type "row" or "col", default "col"
				 * @param {Boolean} skipFormulaReparse re-parses formulas if needed
				 * @methodOf jS.controlFactory
				 * @name addCells
				 */
				addCells:function (i, isBefore, qty, type, skipFormulaReparse) {
					//hide the autoFiller, it can get confused
					jS.autoFillerHide();

					jS.setDirty(true);
					jS.setChanged(true);
					jS.obj.barHelper().remove();

					var sheet = jS.obj.sheet(),
						sheetWidth = sheet.width(),
						isLast = false,
						o;

					//jS.evt.cellEditAbandon();

					qty = qty || 1;
					type = type || 'col';

					if (i == u) {
						i = (type == 'row' ? jS.sheetSize().rows : jS.sheetSize().cols);
						isLast = true;
					}

					switch (type) {
						case "row":
							o = {
								cells:function () {
									//table / tbody / tr / td
									var cells = jS.rowTds(sheet, i);
									if (!cells || !cells[0]) return [];
									return cells[0].parentNode;
								},
								col:function () {
									return '';
								},
								size:function () {
									var cells = o.cells();
									return cells.children.length - 1;
								},
								loc:function () {
									var cells = o.cells();
									return jS.getTdLocation(cells.children[0]);
								},
								newCells:function () {
									var j = o.size(),
										newCells = '';

									for (var i = 0; i <= j; i++) {
										if (i == 0) {
											newCells += '<td class="' + jS.cl.barLeft + ' ' + jS.cl.barLeft + '_' + jS.i + ' ' + jS.cl.uiBar + '" data-entity="left" data-type="bar">';
										} else {
											newCells += '<td />';
										}
									}

									return '<tr style="height: ' + s.colMargin + 'px;">' + newCells + '</tr>';
								},
								newCol:'',
								offset:{row:qty, col:0},
								start:function () {
									return {row:(isBefore ? i : i + qty)};
								},
								createCells:function (tr) {
									tr.each(function (row) {
										var tds = $(this).children(),
											offset = (isBefore ? 0 : 1) + i;
										jS.spreadsheets[jS.i].splice(row + offset, 0, []);
										tds.each(function (col) {
											var obj = jS.controls.bar.y.td[jS.i];
											if (col == 0) {//skip bar
												jS.controls.bar.y.td[jS.i].splice(row + offset, 0, $(this));
											} else {
												jS.createCell($(this), jS.i, row + offset, col);
											}
										});
									});

									jS.refreshRowLabels(i);
								}
							};
							break;
						case "col":
							o = {
								cells:function () {
									var cellStart = jS.rowTds(sheet, 1)[i],
										lastRow = jS.rowTds(sheet),
										cellEnd = lastRow[lastRow.length - 1],

										loc1 = jS.getTdLocation(cellStart),
										loc2 = jS.getTdLocation(cellEnd),

									//we get the first cell then get all the other cells directly... faster ;)
										cells = $([]);

									cells = cells.add(jS.obj.barTop(loc1.col));
									for (var j = 1; j <= loc2.row; j++) {
										cells = cells.add(jS.getTd(jS.i, j, loc1.col));
									}

									return cells;
								},
								col:function () {
									return jS.col(sheet, i);
								},
								newCol:'<col />',
								loc:function (cells) {
									cells = (cells ? cells : o.cells());
									return jS.getTdLocation(cells.first());
								},
								newCells:function () {
									return '<td />';
								},
								offset:{row:0, col:qty},
								start:function () {
									return {col:(isBefore ? i : i + qty)};
								},
								createCells:function (tds, cols) {
									cols.width(jS.s.newColumnWidth);
									var rows = jS.rows(sheet);
									for (var row = 0; row < rows.length; row++) {
										var col = (isBefore ? 0 : 1) + i,
											colMax = col + qty;
										for (col; col < colMax; col++) {
											var td = $(sheet[0].children[1].children[row].children[col]);
											if (row == 0) {
												jS.controls.bar.x.td[jS.i].splice(col, 0, td);
												td
													.addClass(jS.cl.barTop + ' ' + jS.cl.barTop + '_' + jS.i + ' ' + jS.cl.uiBar)
													.data('type', 'bar')
													.data('entity', 'top')
													.text(jSE.columnLabelString(col));
											} else {
												jS.spreadsheets[jS.i][row].splice(col, 0, {});
												jS.createCell(td, jS.i, row, col);
											}
										}
									}

									jS.refreshColumnLabels(i);
								}
							};
							break;
					}

					var cells = $(o.cells()),
						loc = o.loc(cells),
						col = o.col(),

						newCell = o.newCells(),
						newCol = o.newCol,

						newCols = '',
						newCells = '';

					for (var j = 0; j < qty; j++) { //by keeping these variables strings temporarily, we cut down on using system resources
						newCols += newCol;
						newCells += newCell;
					}

					newCols = $(newCols);
					newCells = $(newCells);

					if (isBefore) {
						cells.before(newCells);
						$(col).before(newCols);
					} else {
						cells.after(newCells);
						$(col).after(newCols);
					}

					o.createCells(newCells, newCols);

					if (!skipFormulaReparse && isLast != true) {
						//offset formulas
						jS.offsetFormulas(loc, o.offset, isBefore);
					}

					jS.obj.pane().trigger('resizeScroll');
				},

				/**
				 * creates single row
				 * @param {Integer} i, optional, row index
				 * @param {Boolean} isBefore places cells before the selected cell if set to true, otherwise they will go after, or at end
				 * @methodOf jS.controlFactory
				 * @name addRow
				 */
				addRow:function (i, isBefore) {
					jS.controlFactory.addCells(i, isBefore, 1, 'row');
					jS.trigger('sheetAddRow', [i, isBefore, 1]);
				},

				/**
				 * creates single column
				 * @param {Integer} i, optional, column index
				 * @param {Boolean} isBefore places cells before the selected cell if set to true, otherwise they will go after, or at end
				 * @methodOf jS.controlFactory
				 * @name addColumn
				 */
				addColumn:function (i, isBefore) {
					jS.controlFactory.addCells(i, isBefore, 1, 'col');
					jS.trigger('sheetAddColumn', [i, isBefore, 1]);
				},

				/**
				 * Creates all the bars to the left of the spreadsheet, if they exist, they are first removed
				 * @param {jQuery|HTMLElement} sheet Table of spreadsheet
				 * @methodOf jS.controlFactory
				 * @name barLeft
				 */
				barLeft:function (sheet) {
					jS.obj.barLefts().remove();

					//table / tbody / tr
					sheet.children('tbody').children('tr').each(function (i) {
						if (i > 0) {//top loads first, then we load barleft, the first cell is corner
							$(this).prepend('<td  />');
						}
					});
				},

				/**
				 * Creates all the bars to the top of the spreadsheet on colgroup col elements, if they exist, they are first removed
				 * @param {jQuery|HTMLElement} sheet Table of spreadsheet
				 * @methodOf jS.controlFactory
				 * @name barTop
				 */
				barTop:function (sheet) {
					var colgroup = sheet.children('colgroup'),
						col = $('<col />')
							.attr('width', s.colMargin)
							.css('width', s.colMargin + 'px')
							.prependTo(colgroup);

					jS.obj.barTops().remove();
					var barTopParent = $('<tr class="' + jS.cl.barTopParent + '" />');
					jS.controls.barTopParent[jS.i] = barTopParent;

					var parent = sheet.children('tbody').children('tr:first');

					//corner
					barTopParent.append('<td />');

					parent.children('td').each(function (i) {
						barTopParent.append('<td />');
					});

					barTopParent.insertBefore(parent);

					return barTopParent;
				},

				/**
				 * Creates the draggable objects for freezing cells
				 * @type {Object}
				 * @memberOf jS.controlFactory
				 * @name barHandleFreeze
				 * @namespace
				 */
				barHandleFreeze:{

					/**
					 * @param {jQuery|HTMLElement} pane
					 * @returns {Boolean}
					 * @methodOf jS.controlFactory.barHandleFreeze
					 * @name top
					 */
					top:function (pane) {
						if (jS.isBusy()) return false;
						if (!(jS.scrolledTo().col.end <= (jS.frozenAt().col + 1))) return false;

						jS.obj.barHelper().remove();

						var bar = jS.obj.barTop(jS.frozenAt().col + 1),
							pos = bar.position(),
							handle = $('<div class="' + jS.cl.uiBarHandleFreezeTop + ' ' + jS.cl.barHelper + ' ' + jS.cl.barHandleFreezeTop + '" />')
								.height(s.colMargin + s.boxModelCorrection)
								.css('top', pos.top + 'px')
								.css('left', pos.left + 'px')
								.attr('title', jS.msg.dragToFreezeCol)
								.prependTo(pane);

						jS.controls.bar.helper[jS.i] = jS.obj.barHelper().add(handle);
						jS.controls.bar.x.handleFreeze[jS.i] = handle;

						jS.draggable(handle, {
							axis:'x',
							start:function () {
								jS.setBusy(true);
							},
							stop:function (e, ui) {
								jS.setBusy(false);
								jS.setDirty(true);
								var target = jS.nearest(handle, jS.controls.bar.x.tds());
								jS.obj.barHelper().remove();
								jS.frozenAt().col = jS.getTdLocation(target).col - 1;
								jS.evt.scroll.start('x', pane);
							},
							containment:'parent'
						});
					},

					/**
					 *
					 * @param {jQuery|HTMLElement} pane
					 * @returns {Boolean}
					 * @methodOf jS.controlFactory.barHandleFreeze
					 * @name left
					 */
					left:function (pane) {
						if (jS.isBusy()) return false;
						if (!(jS.scrolledTo().row.end <= (jS.frozenAt().row + 1))) return false;

						jS.obj.barHelper().remove();

						var bar = jS.obj.barLeft(jS.frozenAt().row + 1),
							pos = bar.position(),
							handle = $('<div class="' + jS.cl.uiBarHandleFreezeLeft + ' ' + jS.cl.barHelper + ' ' + jS.cl.barHandleFreezeLeft + '" />')
								.width(s.colMargin)
								.css('top', pos.top + 'px')
								.css('left', pos.left + 'px')
								.attr('title', jS.msg.dragToFreezeRow)
								.prependTo(pane);

						jS.controls.bar.helper[jS.i] = jS.obj.barHelper().add(handle);
						jS.controls.bar.y.handleFreeze[jS.i] = handle;

						jS.draggable(handle, {
							axis:'y',
							start:function () {
								jS.setBusy(true);
							},
							stop:function (e, ui) {
								jS.setBusy(false);
								jS.setDirty(true);
								var target = jS.nearest(handle, jS.controls.bar.y.tds());
								jS.obj.barHelper().remove();
								jS.frozenAt().row = jS.getTdLocation(target).row - 1;
								jS.evt.scroll.start('y', pane);
							},
							containment:'parent'
						});
					},

					/**
					 * @methodOf jS.controlFactory.barHandleFreeze
					 * @name corner
					 */
					corner:function () {
					}
				},

				/**
				 *
				 * Creates menus for contextual menus and top bar button
				 * @param bar
				 * @param menuItems
				 * @returns {jQuery|HTMLElement}
				 * @memberOf jS.controlFactory
				 * @name makeMenu
				 */
				makeMenu:function (bar, menuItems) {
					var menu;

					switch (bar) {
						case "top":
							menu = $('<div class="' + jS.cl.uiMenu + ' ' + jS.cl.menu + '" />');
							jS.controls.bar.x.menu[jS.i] = menu;
							break;
						case "left":
							menu = $('<div class="' + jS.cl.uiMenu + ' ' + jS.cl.menu + '" />');
							jS.controls.bar.y.menu[jS.i] = menu;
							break;
						case "cell":
							menu = $('<div class="' + jS.cl.uiMenu + ' ' + jS.cl.menu + '" />');
							jS.controls.cellMenu[jS.i] = menu;
							break;
					}

					menu
						.mouseleave(function () {
							menu.hide();
						})
						.appendTo($body)
						.hide();

					for (var msg in menuItems) {
						if (menuItems[msg]) {
							if ($.isFunction(menuItems[msg])) {
								$('<div />')
									.text(msg)
									.data('msg', msg)
									.click(function () {
										menuItems[$(this).data('msg')].apply(this, [jS]);
										return false;
									})
									.appendTo(menu);

							} else if (menuItems[msg] == 'line') {
								$('<hr />').appendTo(menu);
							}
						}
					}

					return menu;
				},

				/**
				 * Creates items within menus using jQuery.sheet.instance.msg
				 * @memberOf jS.controlFactory
				 * @namespace
				 * @name barMenu
				 */
				barMenu:{

					/**
					 * @param {Object} e jQuery event
					 * @param {Integer} i column
					 * @param {jQuery|HTMLElement} target
					 * @returns {*}
					 * @methodOf jS.controlFactory.barMenu
					 * @name top
					 */
					top:function (e, i, target) {
						if (jS.isBusy()) return false;
						var menu = jS.obj.barMenuTop().hide();

						if (!menu.length) {
							menu = jS.controlFactory.makeMenu('top', s.contextmenuTop);
						}

						if (!target) {
							menu
								.css('left', (e.pageX - 5) + 'px')
								.css('top', (e.pageY - 5) + 'px')
								.show();
							return menu;
						}

						var barMenuParentTop = jS.obj.barMenuParentTop().hide();

						if (!barMenuParentTop.length) {

							barMenuParentTop = $('<div class="' + jS.cl.uiBarMenuTop + ' ' + jS.cl.barHelper + '">' +
								'<span class="ui-icon ui-icon-triangle-1-s" /></span>' +
								'</div>')
								.mousedown(function (e) {
									barMenuParentTop.parent()
										.mousedown()
										.mouseup();

									var offset = barMenuParentTop.offset();

									menu
										.css('left', (e.pageX - 5) + 'px')
										.css('top', (e.pageY - 5) + 'px')
										.show();
								})
								.blur(function () {
									if (menu) menu.hide();
								})
								.css('padding-left', target.position().left + target.width() - s.colMargin)
								.bind('destroy', function () {
									barMenuParentTop.remove();
									jS.controls.bar.x.menuParent[jS.i] = null;
								});

							jS.controls.bar.x.menuParent[jS.i] = barMenuParentTop;
						}

						barMenuParentTop
							.prependTo(target)
							.show();
					},

					/**
					 *
					 * @param e
					 * @param i
					 * @returns {Boolean}
					 * @methodOf jS.controlFactory.barMenu
					 * @name left
					 */
					left:function (e, i) {
						if (jS.isBusy()) return false;
						jS.obj.barMenuLeft().hide();

						if (i) jS.obj.barHandleFreezeLeft().remove();
						var menu;

						menu = jS.obj.barMenuLeft();

						if (!menu.length) {
							menu = jS.controlFactory.makeMenu('left', s.contextmenuLeft);
						}

						menu
							.css('left', (e.pageX - 5) + 'px')
							.css('top', (e.pageY - 5) + 'px')
							.show();

						return true;
					},

					/**
					 * @methodOf jS.controlFactory.barMenu
					 * @name corner
					 */
					corner:function () {
					}
				},


				/**
				 * Creates contextual menus for cells (a right click menu)
				 * @param {Object} e jQuery event
				 * @returns {Boolean}
				 * @methodOf jS.controlFactory
				 * @name cellMenu
				 */
				cellMenu:function (e) {
					if (jS.isBusy()) return false;
					jS.obj.cellMenu().hide();

					var menu = jS.obj.cellMenu();

					if (!menu.length) {
						menu = jS.controlFactory.makeMenu('cell', s.contextmenuCell);
					}

					menu
						.css('left', (e.pageX - 5) + 'px')
						.css('top', (e.pageY - 5) + 'px')
						.show();
				},


				/**
				 * Creates the control/container for everything above the spreadsheet, removes them if they already exist
				 * @methodOf jS.controlFactory
				 * @name header
				 */
				header:function () {
					jS.obj.header().remove();
					jS.obj.tabContainer().remove();

					var header = jS.controls.header = $('<div class="' + jS.cl.header + '"></div>'),
						firstRow = $('<table><tr /></table>').prependTo(header),
						firstRowTr = $('<tr />');

					if (s.title) {
						if ($.isFunction(s.title)) {
							s.title = jS.title(jS, I);
						}
						firstRowTr.append(jS.controls.title = $('<td class="' + jS.cl.title + '" />').html(s.title));
					}

					//Sheet Menu Control
					function makeMenu(menu) {
						if ($.isFunction(menu)) {
							menu = $(menu(jS));
						} else {
							menu = $(menu);
						}

						if (menu.is('ul')) {
							menu
								.find("ul").hide()
								.addClass(jS.cl.uiMenuUl);

							menu
								.find("li")
								.addClass(jS.cl.uiMenuLi)
								.hover(function () {
									$(this).find('ul:first')
										.hide()
										.show();
								}, function () {
									$(this).find('ul:first')
										.hide();
								});
						}
						return menu;
					}

					if (jS.isSheetEditable()) {
						if (s.menuLeft) {
							jS.controls.menuLeft[jS.i] = $('<td class="' + jS.cl.menu + ' ' + jS.cl.menuFixed + '" />')
								.append(makeMenu(s.menuLeft))
								.prependTo(firstRowTr);

							jS.controls.menuLeft[jS.i].find('img').load(function () {
								jS.sheetSyncSize();
							});
						}

						if (s.menuRight) {
							jS.controls.menuRight[jS.i] = $('<td class="' + jS.cl.menu + ' ' + jS.cl.menuFixed + '" />')
								.append(makeMenu(s.menuRight))
								.appendTo(firstRowTr);

							jS.controls.menuRight[jS.i].find('img').load(function () {
								jS.sheetSyncSize();
							});
						}

						var label = $('<td class="' + jS.cl.label + '"></td>');
						jS.controls.label = label;

						//Edit box menu
						var formula = $('<textarea class="' + jS.cl.formula + '"></textarea>')
							.keydown(jS.evt.keydownHandler.formulaKeydown)
							.keyup(function () {
								jS.obj.inPlaceEdit().val(jS.obj.formula().val());
							})
							.change(function () {
								jS.obj.inPlaceEdit().val(jS.obj.formula().val());
							})
							.bind('paste', jS.evt.pasteOverCells)
							.focus(function () {
								jS.setNav(false);
							})
							.focusout(function () {
								jS.setNav(true);
							})
							.blur(function () {
								jS.setNav(true);
							});
						jS.controls.formula = formula;


						var secondRow = $('<table cellpadding="0" cellspacing="0" border="0"></table>')
							.appendTo(header)
							.append(
								$('<tr></tr>')
									.append(label)
									.append($('<td class="' + jS.cl.formulaParent + '"></td>').append(formula))
						);


						// resizable formula area - a bit hard to grab the handle but is there!
						var formulaResizeParent = $('<span />');
						jS.resizableSheet(jS.obj.formula().wrap(formulaResizeParent).parent(), {
							minHeight:jS.obj.formula().height(),
							maxHeight:78,
							handles:'s',
							resize:function (e, ui) {
								jS.obj.formula().height(ui.size.height);
								jS.sheetSyncSize();
							}
						});

						$.sheet.instance.each(function () {
							this.nav = false;
						});

						jS.setNav(true);

						$document
							.keydown(jS.evt.keydownHandler.documentKeydown);
					}

					firstRowTr.appendTo(firstRow);

					return header;
				},

				/**
				 * Creates the user interface for spreadsheets
				 * @methodOf jS.controlFactory
				 * @name ui
				 */
				ui:function () {
					return jS.controls.ui = $('<div class="' + jS.cl.ui + '">');
				},


				/**
				 * Creates the tab interface for spreadsheets
				 * @methodOf jS.controlFactory
				 * @name tabContainer
				 */
				tabContainer:function () {
					var tabContainer = jS.controls.tabContainer = $('<div class="' + jS.cl.tabContainer + '"></div>')
						.mousedown(function (e) {
							var i = $(e.target).data('i') * 1;
							if (i >= 0) {
								jS.trigger('sheetSwitch', [i]);
							}
							return false;
						})
						.dblclick(function (e) {
							var i = $(e.target).data('i') * 1;
							if (i >= 0) {
								jS.trigger('sheetRename', [$(e.target).data('i') * 1]);
							}
							return false;
						});


					if (jS.isSheetEditable()) {
						var addSheet = $('<span class="' + jS.cl.uiTab + ' ui-corner-bottom" title="Add a spreadsheet" data-i="-1">+</span>')
							.click(function () {
								jS.addSheet({
									rows:25,
									cols:10
								});
							})
							.appendTo(tabContainer);

						if ($.fn.sortable) {
							var startPosition;

							tabContainer.sortable({
								placeholder:'ui-state-highlight',
								axis:'x',
								forceHelperSize:true,
								forcePlaceholderSize:true,
								opacity:0.6,
								cancel:'span[i="-1"]',
								start:function (e, ui) {
									startPosition = ui.item.index();
									jS.trigger('sheetTabSortStart', [e, ui]);
								},
								update:function (e, ui) {
									jS.trigger('sheetTabSortUpdate', [e, ui, startPosition]);
								}
							});
						}
					} else {
						$('<span />').appendTo(tabContainer);
					}

					return tabContainer;
				},

				/**
				 * Creates the scrolling system used by each spreadsheet
				 * @param enclosure
				 * @param pane
				 * @param sheet
				 * @methodOf jS.controlFactory
				 * @name scroll
				 */
				scroll:function (enclosure, pane, sheet) {
					var scroll = jS.controls.scroll[jS.i] = $('<div class="' + jS.cl.scroll + '">' +
							'<div></div>' +
						'</div>')
						.scroll(function () {
							if (!jS.isBusy()) {
								jS.evt.scroll.scrollTo({axis:'x', pixel:this.scrollLeft}, 0);
								jS.evt.scroll.scrollTo({axis:'y', pixel:this.scrollTop}, 0);

								jS.autoFillerGoToTd();
							}
						})
						.prependTo(enclosure)
						.disableSelectionSpecial()
						.mousedown(function () {
							jS.obj.barHelper().remove();
						}),
						x = 0,y = 0;
					jS.controls.scrolls = jS.obj.scrolls().add(scroll);

					var scrollChild = scroll.children(),
						scrollStyleX = jS.controls.bar.x.scroll[jS.i] = $('<style type="text/css"></style>')
							.bind('updateStyle', function (e, indexes, styleOverride) {
								indexes = indexes || [];

								if (indexes.length == x) return;
								x = indexes.length;

								var style = styleOverride || $.sheet.nthCss('col', '#' + jS.id.sheet + jS.i, this, indexes, jS.frozenAt().col + 1) +
									$.sheet.nthCss('td', '#' + jS.id.sheet + jS.i + ' ' + 'tr', this, indexes, jS.frozenAt().col + 1);

								if (this.styleSheet) {
									this.styleSheet.cssText = style;
								} else {
									scrollStyleX.text(style);
								}

								jS.scrolledTo();
								jS.scrolledArea[jS.i].col.start = indexes[0] || 1;
								jS.scrolledArea[jS.i].col.end = indexes.pop() || 1;

								jS.obj.barHelper().remove();
							}),
						scrollStyleY = jS.controls.bar.y.scroll[jS.i] = $('<style type="text/css"></style>')
							.bind('updateStyle', function (e, indexes, styleOverride) {
								indexes = indexes || [];

								if (indexes.length == y) return;
								y = indexes.length;

								var style = styleOverride || $.sheet.nthCss('tr', '#' + jS.id.sheet + jS.i, this, indexes, jS.frozenAt().row + 1);

								if (this.styleSheet) { //IE compatibility
									this.styleSheet.cssText = style;
								} else {
									scrollStyleY.text(style);
								}

								jS.scrolledTo();
								jS.scrolledArea[jS.i].row.start = indexes[0] || 1;
								jS.scrolledArea[jS.i].row.end = indexes.pop() || 1;

								jS.obj.barHelper().remove();
							});

					var xStyle, yStyle;

					function styleString(o) {
						if (o && o[0] && o[0].styleSheet) return o[0].styleSheet.cssText;
						return o.text();
					}

					pane
						.append(scrollStyleX)
						.append(scrollStyleY)
						.bind('resizeScroll', function () {
							xStyle = styleString(scrollStyleX);
							yStyle = styleString(scrollStyleY);

							scrollStyleX.trigger('updateStyle');
							scrollStyleY.trigger('updateStyle');

							scrollChild
								.height(sheet.height())
								.width(sheet.width());

							scroll
								.height(enclosure.height())
								.width(enclosure.width());

							jS.evt.scroll.start('x', pane, sheet);
							jS.evt.scroll.start('y', pane, sheet);

							scrollStyleX.trigger('updateStyle', [null, xStyle]);
							scrollStyleY.trigger('updateStyle', [null, yStyle]);
						});

					if (!$.fn.mousewheel) return;

					pane
						.mousewheel(function (e, o) {
							var E = e.originalEvent,
								e,
								c,
								div = function (a, b) {
									return 0 != a % b ? a : a / b;
								};


							if ("mousewheel" == E.type) {
								var scrollNoXY = 1,
									setPixels = div(-E.wheelDelta, scrollNoXY), x, y;

								if (E.wheelDeltaX !== u) {
									scroll
										.scrollTop(scroll[0].scrollTop + div(-E.wheelDeltaY, scrollNoXY))
										.scrollLeft(scroll[0].scrollLeft + div(-E.wheelDeltaX, scrollNoXY))
										.scroll();
								} else {
									scroll
										.scrollTop(scroll[0].scrollTop + setPixels)
										.scroll();
								}

							} else {
								e = E.detail, 100 < e ? e = 3 : -100 > e && (e = -3);

								var top = 0, left = 0;
								switch (e) {
									case 1:
									case -1:
										left = e * 50;
										break;
									case 3:
									case -3:
										top = e * 15;
										break;
								}

								scroll
									.scrollTop(scroll[0].scrollTop + top)
									.scrollLeft(scroll[0].scrollLeft + left)
									.scroll();
							}

							return false;
						});
				},

				hide:function (enclosure, pane, sheet) {
					pane = pane || jS.obj.pane();

					var toggleHideStyleX = jS.controls.toggleHide.x[jS.i] = $('<style></style>')
							.appendTo(pane)
							.bind('updateStyle', function (e) {
								var style = $.sheet.nthCss('col', '#' + jS.id.sheet + jS.i, this, jS.toggleHide.hiddenColumns[jS.i], 0) +
									$.sheet.nthCss('td', '#' + jS.id.sheet + jS.i + ' tr', this, jS.toggleHide.hiddenColumns[jS.i], 0);

								if (this.styleSheet) {
									this.styleSheet.cssText = style;
								} else {
									toggleHideStyleX.text(style);
								}

								jS.autoFillerGoToTd();
							}),
						toggleHideStyleY = jS.controls.toggleHide.y[jS.i] = $('<style></style>')
							.appendTo(pane)
							.bind('updateStyle', function (e) {
								var style = $.sheet.nthCss('tr', '#' + jS.id.sheet + jS.i, this, jS.toggleHide.hiddenRows[jS.i], 0);

								if (this.styleSheet) {
									this.styleSheet.cssText = style;
								} else {
									toggleHideStyleY.text(style);
								}

								jS.autoFillerGoToTd();
							});

					s.hiddenColumns[jS.i] = s.hiddenColumns[jS.i] || [];
					s.hiddenRows[jS.i] = s.hiddenRows[jS.i] || [];

					if (!s.hiddenColumns[jS.i].length || !s.hiddenRows[jS.i].length) {
						s.hiddenRows[jS.i] = arrHelpers.toNumbers((sheet.data('hiddenrows') || '' + '').split(','));
						s.hiddenColumns[jS.i] = arrHelpers.toNumbers((sheet.data('hiddencolumns') || '' + '').split(','));
					}

					if (jS.s.hiddenRows[jS.i]) {
						for (var row in jS.s.hiddenRows[jS.i]) {
							jS.toggleHide.row(jS.s.hiddenRows[jS.i][row]);
						}
					}

					if (s.hiddenColumns[jS.i]) {
						for (var col in s.hiddenColumns[jS.i]) {
							jS.toggleHide.column(s.hiddenColumns[jS.i][col]);
						}
					}
				},

				/**
				 * Creates the spreadsheet user interface
				 * @param {jQuery|HTMLElement} sheet raw table
				 * @param {Integer} i the new count for spreadsheets in this instance
				 * @returns {jQuery|HTMLElement} table
				 * @methodOf jS.controlFactory
				 * @name sheetUI
				 */
				sheetUI:function (sheet, i) {
					if (!i) {
						jS.sheetCount = 0;
						jS.i = 0;
					} else {
						jS.sheetCount++;
						jS.i = i;
					}

					jS.tuneTableForSheetUse(sheet);

					jS.readOnly[i] = sheet.hasClass('readonly');

					var enclosure = jS.controlFactory.enclosure().appendTo(jS.obj.ui()),
						pane = jS.obj.pane().html(sheet);

					jS.controlFactory.scroll(enclosure, pane, sheet);

					if (jS.isSheetEditable()) {
						var autoFiller = jS.controlFactory.autoFiller();
						if (autoFiller) {
							pane.append(autoFiller);
						}
					}

					jS.sheetDecorate(sheet);

					jS.controlFactory.barTop(sheet);
					jS.controlFactory.barLeft(sheet);

					jS.sheetTab(true);

					if (jS.isSheetEditable()) {
						var formula = jS.obj.formula();

						pane
							.mousedown(function (e) {
								jS.setNav(true);
								if (jS.isBusy()) return false;

								if (jS.isTd(e.target)) {
									jS.evt.cellOnMouseDown(e);
									return false;
								}

								if (jS.isBar(e.target)) { //possibly a bar
									jS.evt.barInteraction.select(e.target);
									return false;
								}
							})
							.mouseover(function (e) {
								//This manages bar resize, bar menu, and bar selection
								if (jS.isBusy()) return false;

								if (!jS.isBar(e.target)) return;
								var bar = $(e.target),
									entity = bar.data('entity'),
									i = jS.getBarIndex[entity](e.target);

								if (i < 0) return false;

								if (jS.evt.barInteraction.selecting) {
									jS.evt.barInteraction.last = i;

									jS.cellSetActiveBar(entity, jS.evt.barInteraction.first, jS.evt.barInteraction.last);
								} else {
									jS.resizeBar[entity](bar, i, pane, sheet);

									if (jS.isSheetEditable()) {
										jS.controlFactory.barHandleFreeze[entity](pane);

										if (entity == "top") {
											jS.controlFactory.barMenu[entity](e, i, bar);
										}
									}
								}
							})
							.bind('contextmenu', function (e) {
								if (jS.isBusy()) return false;

								if (jS.isBar(e.target)) {
									var o = $(e.target),
										entity = o.data('entity'),
										i = jS.getBarIndex[entity](e.target);

									if (i < 0) return false;

									if (jS.evt.barInteraction.first == jS.evt.barInteraction.last) {
										jS.controlFactory.barMenu[entity](e, i);
									}
								} else {
									jS.controlFactory.cellMenu(e);
								}
								return false;
							})
							.disableSelectionSpecial()
							.bind('cellEdit', jS.evt.cellEdit)
							.dblclick(jS.evt.cellOnDblClick);
					}

					jS.themeRoller.start(sheet);

					// resizable container div
					jS.resizableSheet(s.parent, {
						minWidth:s.width * 0.1,
						minHeight:s.height * 0.1,

						start:function () {
							enclosure.hide();
						},
						stop:function () {
							enclosure.show();
							s.width = s.parent.width();
							s.height = s.parent.height();
							pane.trigger('resizeScroll');
						}
					});

					jS.createSpreadsheet(sheet, jS.i);

					jS.checkMinSize(sheet);

					jS.controlFactory.tab();

					jS.controlFactory.hide(enclosure, pane, sheet);

					jS.setChanged(true);

					//jS.log('Sheet Initialized');

					return sheet;
				},

				/**
				 * The viewing console for spreadsheet
				 * @returns {*|jQuery|HTMLElement}
				 * @methodOf jS.controlFactory
				 * @name enclosure
				 */
				enclosure:function () {
					var pane = jS.controls.pane[jS.i] = $('<div class="' + jS.cl.pane + '"></div>'),
						enclosure = jS.controls.enclosure[jS.i] = $('<div class="' + jS.cl.enclosure + '"></div>')
							.append(pane);

					jS.controls.panes = jS.obj.panes().add(pane);
					jS.controls.enclosures = jS.obj.enclosures().add(enclosure);

					return enclosure;
				},

				/**
				 * Adds a tab for navigation to a spreadsheet
				 * @returns {Node|jQuery}
				 * @methodOf jS.controlFactory
				 * @name tab
				 */
				tab:function () {
					var tab = jS.controls.tab[jS.i] = $('<span class="' + jS.cl.uiTab + ' ui-corner-bottom">' +
						'<a class="' + jS.cl.tab + '" data-i="' + jS.i + '">' + jS.sheetTab(true) + '</a>' +
						'</span>')
						.insertBefore(
						jS.obj.tabContainer().find('span:last')
					);

					jS.controls.tabs = jS.obj.tabs().add(tab);

					return tab;
				},

				/**
				 * Creates a teaxtarea for a user to put a value in that floats on top of the current selected cell
				 * @param {jQuery|HTMLElement} td the td to be edited
				 * @param {Boolean} noSelect
				 * @methodOf jS.controlFactory
				 * @name inPlaceEdit
				 */
				inPlaceEdit:function (td, noSelect) {
					td = td || jS.obj.cellActive();

					if (!td.length) {
						td = $(jS.rowTds(null, 1)[1]);
						jS.cellEdit(td);
					}

					jS.obj.inPlaceEdit().trigger('destroy');
					var formula = jS.obj.formula(),
						offset = td.offset(),
						style = td.attr('style'),
						w = td.width(),
						h = td.height(),
						val = formula.val();

					if (!offset) return; //If the td is a dud, we do not want a textarea

					var textarea = jS.controls.inPlaceEdit[jS.i] = $('<textarea class="' + jS.cl.inPlaceEdit + ' ' + jS.cl.uiInPlaceEdit + '" data-i="' + jS.i + '"/>')
						.css('left', offset.left)
						.css('top', offset.top)
						.width(w)
						.height(h)
						.keydown(jS.evt.inPlaceEditOnKeyDown)
						.keyup(function () {
							formula.val(textarea.val());
						})
						.change(function () {
							formula.val(textarea.val());
						})
						.focus(function () {
							jS.setNav(false);
						})
						.focusout(function () {
							jS.setNav(true);
						})
						.blur(function () {
							jS.setNav(true);
						})
						.bind('paste', jS.evt.pasteOverCells)
						.appendTo($body)
						.val(formula.val())
						.focus()
						.bind('destroy', function () {
							jS.cellLast.isEdit = (textarea.val() != val);
							textarea.remove();
							jS.controls.inPlaceEdit[textarea.data('i')] = false;
						});

					if (!noSelect) {
						textarea.select();
					}

					//Make the textarrea resizable automatically
					if ($.fn.elastic) {
						textarea.elastic();
					}
				},

				/**
				 * Created the autoFiller object
				 * @returns {*|jQuery|null}
				 * @methodOf jS.controlFactory
				 * @name autoFiller
				 */
				autoFiller:function () {
					if (!s.autoFiller) return null;

					jS.controls.autoFiller[jS.i] = $('<div class="' + jS.cl.autoFiller + ' ' + jS.cl.uiAutoFiller + '">' +
							'<div class="' + jS.cl.autoFillerHandle + '" />' +
							'<div class="' + jS.cl.autoFillerCover + '" />' +
						'</div>')
							.mousedown(function (e) {
								var td = jS.obj.cellActive();
								if (td) {
									var loc = jS.getTdLocation(td);
									jS.cellSetActive(td, loc, true, jS.autoFillerNotGroup, function () {
										var highlighted = jS.obj.cellHighlighted(),
											hLoc = jS.getTdLocation(highlighted.first());
										jS.fillUpOrDown(hLoc.row < loc.row || hLoc.col < loc.col);
										jS.autoFillerGoToTd(highlighted.last());
										jS.autoFillerNotGroup = false;
									});
								}
							});

					return jS.controls.autoFiller[jS.i];
				}
			},

			/**
			 * Allows grouping of cells
			 * @memberOf jS
			 * @name autoFillerNotGroup
			 */
			autoFillerNotGroup:true,


			/**
			 * Sends tab delimited string into cells, usually a paste from external spreadsheet application
			 * @param oldVal what formula should be when this is done working with all the values
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name updateCellsAfterPasteToFormula
			 */
			updateCellsAfterPasteToFormula:function (oldVal) {
				var newValCount = 0,
					formula = jS.obj.formula(),
					last = new Date();

				oldVal = oldVal || formula.val();

				var loc = {row:jS.cellLast.row, col:jS.cellLast.col},
					val = formula.val(), //once ctrl+v is hit formula now has the data we need
					firstValue = val;

				if (loc.row == 0 && loc.col == 0) return false; //at this point we need to check if there is even a cell selected, if not, we can't save the information, so clear formula editor

				var row = tsv.parse(val);

				//Single cell value
				if (!$.isArray(row)) {
					formula.val(row);
					jS.fillUpOrDown(false, false, row);
					return true;
				}

				//values that need put into multi cells
				for (var i = 0; i < row.length; i++) {
					jS.cellLast.isEdit = true;
					var col = row[i];
					for (var j = 0; j < col.length; j++) {
						newValCount++;
						var td = jS.getTd(jS.i, i + loc.row, j + loc.col);

						td.row = loc.row;
						td.col = loc.col;

						if (td.length) {
							if (!jS.spreadsheets[jS.i] || !jS.spreadsheets[jS.i][i + loc.row] || !jS.spreadsheets[jS.i][i + loc.row][j + loc.col]) continue;
							var cell = jS.spreadsheets[jS.i][i + loc.row][j + loc.col];
							if (cell) {
								s.parent.one('sheetPreCalculation', function () {
									if ((col[j] + '').charAt(0) == '=') { //we need to know if it's a formula here
											cell.formula = col[j].substring(1);
											cell.value = '';
											td.data('formula', col[j]);
									} else {
											cell.formula = '';
											cell.value = col[j];
											td.removeData('formula');
									}
								});
								jS.calcDependencies(jS.i, i + loc.row, j + loc.col);

								if (i == 0 && j == 0) { //we have to finish the current edit
									firstValue = col[j];
								}
							}
						}
					}
				}

				if (val != firstValue) {
					formula.val(firstValue);
				}

				jS.fillUpOrDown(false, false, firstValue);

				jS.evt.cellEditDone(true);
			},

			/**
			 * Event handlers for instance
			 * @memberOf jS
			 * @name evt
			 * @namespace
			 */
			evt:{

				/**
				 * Key down handlers
				 * @memberOf jS.evt
				 * @name keydownHandler
				 * @namespace
				 */
				keydownHandler:{

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name enterOnInPlaceEdit
					 */
					enterOnInPlaceEdit:function (e) {
						if (!e.shiftKey) {
							return jS.evt.cellSetFocusFromKeyCode(e);
						} else {
							return true;
						}
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name enter
					 */
					enter:function (e) {
						if (!jS.cellLast.isEdit && !e.ctrlKey) {
							jS.obj.cellActive().dblclick();
							return false;
						} else {
							return this.enterOnInPlaceEdit(e);
						}
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name tab
					 */
					tab:function (e) {
						return jS.evt.cellSetFocusFromKeyCode(e);
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name findCell
					 */
					findCell:function (e) {
						if (e.ctrlKey) {
							jS.cellFind();
							return false;
						}
						return true;
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name redo
					 */
					redo:function (e) {
						if (e.ctrlKey && !jS.cellLast.isEdit) {
							jS.cellUndoable.undoOrRedo();
							return false;
						}
						return true;
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name undo
					 */
					undo:function (e) {
						if (e.ctrlKey && !jS.cellLast.isEdit) {
							jS.cellUndoable.undoOrRedo(true);
							return false;
						}
						return true;
					},


					copy:function (e, clearValue) {
						var tds = jS.obj.cellHighlighted(),
							formula = jS.obj.formula(),
							oldValue = formula.val(),
							cellsTsv = jS.tdsToTsv(tds, clearValue);

						formula
							.val(cellsTsv)
							.focus()
							.select();

						$document
							.one('keyup', function () {
								if (clearValue) {
									formula.val('');
								} else {
									formula.val(oldValue);
								}
							});

						return true;
					},

					cut:function (e) {
						return this.copy(e, true);
					},

					/**
					 * Manages the page up and down buttons
					 * @param {Boolean} reverse Go up or down
					 * @returns {Boolean}
					 * @methodOf jS.evt.keydownHandler
					 * @name pageUpDown
					 */
					pageUpDown:function (reverse) {
						var size = jS.sheetSize(),
							pane = jS.obj.pane(),
							paneHeight = pane.height(),
							prevRowsHeights = 0,
							thisRowHeight = 0,
							td;

						if (reverse) { //go up
							for (var i = jS.cellLast.row; i > 0 && prevRowsHeights < paneHeight; i--) {
								td = jS.getTd(jS.i, i, 1);
								if (!td.data('hidden') && td.is(':hidden')) td.show();
								prevRowsHeights += td.parent().height();
							}
						} else { //go down
							for (var i = jS.cellLast.row; i < size.rows && prevRowsHeights < paneHeight; i++) {
								td = jS.getTd(jS.i, i, 1);
								prevRowsHeights += td.parent().height();
							}
						}
						jS.cellEdit(td);

						return false;
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name formulaKeydown
					 */
					formulaKeydown:function (e) {
						if (jS.readOnly[jS.i]) return false;
						if (jS.cellLast.row < 0 || jS.cellLast.col < 0) return false;

						jS.trigger('sheetFormulaKeydown', [false]);

						switch (e.keyCode) {
							case key.C:
								if (e.ctrlKey) {
									return jS.evt.keydownHandler.copy(e);
								} else {
									jS.obj.cellActive().dblclick();
									return true;
								}
							case key.X:
								if (e.ctrlKey) {
									return jS.evt.keydownHandler.cut(e);
								} else {
									jS.obj.cellActive().dblclick();
									return true;
								}
							case key.Y:
								if (e.ctrlKey) {
									jS.evt.keydownHandler.redo(e);
									return false;
								} else {
									jS.obj.cellActive().trigger('cellEdit');
									return true;
								}
								break;
							case key.Z:
								if (e.ctrlKey) {
									jS.evt.keydownHandler.undo(e);
									return false;
								} else {
									jS.obj.cellActive().trigger('cellEdit');
									return true;
								}
								break;
							case key.ESCAPE:
								jS.evt.cellEditAbandon();
								break;
							case key.ENTER:
								jS.evt.cellSetFocusFromKeyCode(e);
								return false;
								break;
							default:
								jS.cellLast.isEdit = true;
						}
					},

					/**
					 * Helper for events
					 * @param {Boolean} ifTrue
					 * @param e {Object} jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name formulaKeydownIf
					 */
					formulaKeydownIf:function (ifTrue, e) {
						if (ifTrue) {
							jS.obj.cellActive().dblclick();
							return true;
						}
						return false;
					},

					/**
					 *
					 * @param {Object} e jQuery event
					 * @returns {*}
					 * @methodOf jS.evt.keydownHandler
					 * @name documentKeydown
					 */
					documentKeydown:function (e) {
						if (jS.readOnly[jS.i]) return false;
						if (jS.cellLast.row < 0 || jS.cellLast.col < 0) return false;

						if (jS.nav) {
							switch (e.keyCode) {
								case key.DELETE:
									jS.tdsToTsv(null, true);
									jS.obj.formula().val('');
									break;
								case key.TAB:
									jS.evt.keydownHandler.tab(e);
									break;
								case key.ENTER:
								case key.LEFT:
								case key.UP:
								case key.RIGHT:
								case key.DOWN:
									(e.shiftKey ? jS.evt.cellSetHighlightFromKeyCode(e) : jS.evt.cellSetFocusFromKeyCode(e));
									break;
								case key.PAGE_UP:
									jS.evt.keydownHandler.pageUpDown(true);
									break;
								case key.PAGE_DOWN:
									jS.evt.keydownHandler.pageUpDown();
									break;
								case key.HOME:
								case key.END:
									jS.evt.cellSetFocusFromKeyCode(e);
									break;
								case key.V:
									if (e.ctrlKey) {
										return jS.evt.keydownHandler.formulaKeydownIf(!jS.evt.pasteOverCells(e), e);
									} else {
										jS.obj.cellActive().trigger('cellEdit');
										return true;
									}
									break;
								case key.Y:
									if (e.ctrlKey) {
										jS.evt.keydownHandler.redo(e);
										return false;
									} else {
										jS.obj.cellActive().trigger('cellEdit');
										return true;
									}
									break;
								case key.Z:
									if (e.ctrlKey) {
										jS.evt.keydownHandler.undo(e);
										return false;
									} else {
										jS.obj.cellActive().trigger('cellEdit');
										return true;
									}
									break;
								case key.ESCAPE:
									jS.evt.cellEditAbandon();
									break;
								case key.F:
									if (e.ctrlKey) {
										return jS.evt.keydownHandler.formulaKeydownIf(jS.evt.keydownHandler.findCell(e), e);
									} else {
										jS.obj.cellActive().trigger('cellEdit');
										return true;
									}
									break;
								case key.CAPS_LOCK:
								case key.SHIFT:
								case key.ALT:
									break;
								case key.CONTROL: //we need to filter these to keep cell state
									jS.obj.formula().focus().select();
									return true;
									break;
								default:
									jS.obj.cellActive().trigger('cellEdit');
									return true;
									break;
							}
							return false;
						}
					}
				},

				/**
				 * Used for pasting from other spreadsheets
				 * @param {Object} e jQuery event
				 * @returns {Boolean}
				 * @methodOf jS.evt
				 * @name pasteOverCells
				 */
				pasteOverCells:function (e) {
					if (e.ctrlKey || e.type == "paste") {
						var fnAfter = function () {
							jS.updateCellsAfterPasteToFormula();
						};

						var doc = $document
							.one('keyup', function () {
								fnAfter();
								fnAfter = function () {
								};
								doc.mouseup();
							})
							.one('mouseup', function () {
								fnAfter();
								fnAfter = function () {
								};
								doc.keyup();
							});

						jS.setDirty(true);
						jS.setChanged(true);
						return true;
					}
				},

				/**
				 * Edits the textarea that appears over cells for in place edit
				 * @param {Object} e jQuery event
				 * @returns {*}
				 * @methodOf jS.evt
				 * @name inPlaceEditOnKeyDown
				 */
				inPlaceEditOnKeyDown:function (e) {
					jS.trigger('sheetFormulaKeydown', [true]);

					switch (e.keyCode) {
						case key.ENTER:
							return jS.evt.keydownHandler.enterOnInPlaceEdit(e);
							break;
						case key.TAB:
							return jS.evt.keydownHandler.tab(e);
							break;
						case key.ESCAPE:
							jS.evt.cellEditAbandon();
							return false;
							break;
					}
				},

				/**
				 * Updates a cell after edit afterward event "sheetCellEdited" is called w/ params (td, row, col, spreadsheetIndex, sheetIndex)
				 * @param {Boolean} force if set to true forces a calculation of the selected sheet
				 * @methodOf jS.evt
				 * @name cellEditDone
				 */
				cellEditDone:function (force) {
					jS.obj.inPlaceEdit().trigger('destroy');
					if (jS.cellLast.isEdit || force) {
						var formula = jS.obj.formula(),
							td = jS.obj.cellActive();

						if (jS.isFormulaEditable(td)) {
							//Lets ensure that the cell being edited is actually active
							if (td && jS.cellLast.row > 0 && jS.cellLast.col > 0) {

								//This should return either a val from textbox or formula, but if fails it tries once more from formula.
								var v = formula.val(),
									cell = jS.spreadsheets[jS.i][jS.cellLast.row][jS.cellLast.col];

								s.parent.one('sheetPreCalculation', function () {
									if (v.charAt(0) == '=') {
										td.data('formula', v);
										cell.value = v;
										cell.formula = v;
									} else {
										td.removeData('formula');
										cell.value = v;
										cell.formula = '';
									}
								});
								jS.calcDependencies(jS.i, jS.cellLast.row, jS.cellLast.col);

								//formula.focus().select();
								jS.cellLast.isEdit = false;

								//perform final function call
								jS.trigger('sheetCellEdited', [cell]);
							}
						}
					}
				},

				/**
				 * Abandons a cell edit
				 * @param {Boolean} skipCalc if set to true will skip sheet calculation;
				 * @methodOf jS.evt
				 * @name cellEditAbandon
				 */
				cellEditAbandon:function (skipCalc) {
					jS.obj.inPlaceEdit().trigger('destroy');
					jS.themeRoller.bar.clearActive();
					jS.themeRoller.cell.clearHighlighted();

					if (!skipCalc) {
						jS.calc();
					}

					jS.cellLast.td = $([]);
					jS.cellLast.row = 0;
					jS.cellLast.col = 0;
					jS.rowLast = 0;
					jS.colLast = 0;

					jS.labelUpdate('', true);
					jS.obj.formula()
						.val('');

					jS.autoFillerHide();

					return false;
				},

				/**
				 * Sets active cell from a pixel location
				 * @param {Integer} left pixels left
				 * @param {Integer} top pixels top
				 * @returns {Boolean}
				 * @methodOf jS.evt
				 * @name cellSetFocusFromXY
				 */
				cellSetFocusFromXY:function (left, top) {
					var td = jS.getTdFromXY(left, top);
					if (jS.isTd(td)) {
						td = $(td);
						jS.cellEdit(td);
						return false;
					}
					return true;
				},

				/**
				 * Highlights a cell from a key code
				 * @param {Object} e jQuery event
				 * @returns {Boolean}
				 * @methodOf jS.evt
				 * @name cellSetHighlightFromKeyCode
				 */
				cellSetHighlightFromKeyCode:function (e) {
					var c = jS.highlightedLast.colLast,
						r = jS.highlightedLast.rowLast,
						size = jS.sheetSize(),
						td;
					jS.obj.cellActive().mousedown();

					switch (e.keyCode) {
						case key.UP:
							r--;
							break;
						case key.DOWN:
							r++;
							break;
						case key.LEFT:
							c--;
							break;
						case key.RIGHT:
							c++;
							break;
					}

					function keepInSize(i, size) {
						if (i < 1) return 1;
						if (i > size) return size;
						return i;
					}

					r = keepInSize(r, size.rows);
					c = keepInSize(c, size.cols);

					jS.themeRoller.cell.clearHighlighted();
					//set current bars
					jS.highlightedLast.colEnd = r;
					jS.highlightedLast.rowEnd = c;

					//highlight the cells
					jS.highlightedLast.td = jS.cycleCellsAndMaintainPoint(jS.themeRoller.cell.setHighlighted, jS.getTdLocation(jS.obj.cellActive()), {row:r, col:c});
					td = jS.getTd(jS.i, r, c)
						.mousemove()
						.mouseup();

					jS.highlightedLast.rowLast = r;
					jS.highlightedLast.colLast = c;
					return false;
				},


				/**
				 * Activates a cell from a key code
				 * @param {Object} e jQuery event
				 * @returns {Boolean}
				 * @methodOf jS.evt
				 * @name cellSetFocusFromKeyCode
				 */
				cellSetFocusFromKeyCode:function (e) {
					var c = jS.cellLast.col, //we don't set the cellLast.col here so that we never go into indexes that don't exist
						r = jS.cellLast.row,
						overrideIsEdit = false;

					switch (e.keyCode) {
						case key.UP:
							r--;
							break;
						case key.DOWN:
							r++;
							break;
						case key.LEFT:
							c--;
							break;
						case key.RIGHT:
							c++;
							break;
						case key.ENTER:
							r++;
							overrideIsEdit = true;
							if (jS.highlightedLast.td.length > 1) {
								var inPlaceEdit = jS.obj.inPlaceEdit(),
									v = inPlaceEdit.val();

								inPlaceEdit.trigger('destroy');
								jS.updateCellsAfterPasteToFormula(v);
								return true;
							} else if (s.autoAddCells) {
								if (jS.cellLast.row == jS.sheetSize().rows) {
									jS.controlFactory.addRow();
								}
							}
							break;
						case key.TAB:
							overrideIsEdit = true;
							if (e.shiftKey) {
								c--;
							} else {
								c++;
							}
							if (s.autoAddCells) {
								if (jS.cellLast.col == jS.sheetSize().cols) {
									jS.controlFactory.addColumn();
								}
							}
							break;
						case key.HOME:
							c = 1;
							break;
						case key.END:
							c = jS.obj.cellActive().parent().children('td').length - 1;
							break;
					}

					//we check here and make sure all values are above 0, so that we get a selected cell
					c = (c ? c : 1);
					r = (r ? r : 1);

					//to get the td could possibly make keystrokes slow, we prevent it here so the user doesn't even know we are listening ;)
					if (!jS.cellLast.isEdit || overrideIsEdit) {
						//get the td that we want to go to
						var td = jS.getTd(jS.i, r, c);

						//if the td exists, lets go to it
						if (td) {
							jS.cellEdit(td);
							return false;
						}
					}
					//default, can be overridden above
					return true;
				},

				/**
				 * Cell on mouse down
				 * @param {Object} e jQuery event
				 * @methodOf jS.evt
				 * @name cellOnMouseDown
				 */
				cellOnMouseDown:function (e) {


					jS.obj.formula().blur();
					if (e.shiftKey) {
						jS.getTdRange(e, jS.obj.formula().val());
					} else {
						jS.cellEdit($(e.target), true);
					}
				},

				/**
				 * Cell on double click
				 * @param {Object} e jQuery event
				 * @methodOf jS.evt
				 * @name cellOnDblClick
				 */
				cellOnDblClick:function (e) {
					if (jS.isBusy()) return false;

					jS.controlFactory.inPlaceEdit(null, true);
					//jS.log('click, in place edit activated');
				},

				cellEdit: function(e) {
					if (jS.isBusy()) return false;

					jS.controlFactory.inPlaceEdit();
				},

				/**
				 * Handles bar events, used for highlighting and activating
				 * @memberOf jS.evt
				 * @name barInteraction
				 * @namespace
				 */
				barInteraction:{

					/**
					 * The first bar that received the event (mousedown)
					 * @memberOf jS.evt.barInteraction
					 * @name first
					 */
					first:0,

					/**
					 * The last bar that received the event (mousedown)
					 * @memberOf jS.evt.barInteraction
					 * @name last
					 */
					last:0,

					/**
					 * Tracks if we are in select mode
					 * @memberOf jS.evt.barInteraction
					 * @name selecting
					 */
					selecting:false,

					/**
					 * Manages the bar selection
					 * @param {Object} o target
					 * @returns {*}
					 * @methodOf jS.evt.barInteraction
					 * @name select
					 */
					select:function (o) {
						if (!o) return;
						if (!jS.isBar(o)) return;
						o = $(o);
						var entity = o.data('entity'), //returns "top" or "left";
							i = jS.getBarIndex[entity](o[0]);

						if (i < 0) return false;

						jS[entity + 'Last'] = i; //keep track of last column for inserting new columns
						jS.evt.barInteraction.last = jS.evt.barInteraction.first = i;

						jS.cellSetActiveBar(entity, jS.evt.barInteraction.first, jS.evt.barInteraction.last);
						jS.evt.barInteraction.first = jS.evt.barInteraction.last = jS[entity + 'Last'] = i;

						jS.evt.barInteraction.selecting = true;
						$document
							.one('mouseup', function () {
								jS.evt.barInteraction.selecting = false;
							});

						return false;
					}
				},

				/**
				 * Manages scrolling
				 * @memberOf jS.evt
				 * @name scroll
				 * @namespace
				 */
				scroll:{

					/**
					 * axis cache, x & y
					 * @memberOf jS.evt.scroll
					 * @name axis
					 */
					axis:{x:{}, y:{}},

					/**
					 * tracks the current spreadsheet size
					 * @memberOf jS.evt.scroll
					 * @name size
					 */
					size:{},

					/**
					 * tracks last select cell
					 * @memberOf jS.evt.scroll
					 * @name td
					 */
					td:{},

					/**
					 * prepairs everything needed for a scroll, needs activated every time spreadsheet changes in size
					 * @param {String} axis x or y
					 * @param {jQuery|HTMLElement} pane pane object
					 * @param {jQuery|HTMLElement} sheet sheet object
					 * @methodOf jS.evt.scroll
					 * @name start
					 */
					start:function (axis, pane, sheet) {

						jS.autoFillerHide();

						pane = pane || jS.obj.pane();
						sheet = sheet || jS.obj.sheet();
						var me = jS.evt.scroll;
						me.size = jS.sheetSize(sheet);
						me.td = jS.obj.cellActive();

						me.axis[axis].v = [];
						me.axis[axis].p = [];

						switch (axis || 'x') {
							case 'x':
								var x = me.axis.x;
								x.max = me.size.cols;
								x.min = 1;
								x.scrollStyle = jS.obj.scrollStyleX()
									.trigger('updateStyle');
								x.area = pane.width();
								x.sheetArea = sheet.width();
								x.scrollUpdate = function (scroll) {
									scroll = scroll || jS.obj.scroll();
									scroll.scrollLeft(x.value * (scroll.width() / me.size.cols));
									return;
								}

								break;
							case 'y':
								var y = me.axis.y;
								y.max = me.size.rows;
								y.min = 1;
								y.scrollStyle = jS.obj.scrollStyleY()
									.trigger('updateStyle');
								y.area = pane.height();
								y.sheetArea = sheet.height();
								y.scrollUpdate = function (scroll) {
									scroll = scroll || jS.obj.scroll();
									scroll.scrollTop(y.value * (scroll.height() / me.size.rows));
									return;
								}
								break;
						}

						me.axis[axis].gridSize = 100 / (me.axis[axis].max - me.axis[axis].min);

						for (var i = me.axis[axis].min; i <= me.axis[axis].max; i++) {
							me.axis[axis].v[i] = me.axis[axis].gridSize * i;
							me.axis[axis].p[me.axis[axis].gridSize * i] = i + 1;
						}
					},

					/**
					 * Scrolls to a position within the spreadsheet
					 * @param {Object} pos {axis, value, pixel} if value not set, pixel is used
					 * @methodOf jS.evt.scroll
					 * @name scrollTo
					 */
					scrollTo:function (pos) {
						pos = pos || {};
						pos.axis = pos.axis || 'x';
						pos.value = pos.value || 0;
						pos.pixel = pos.pixel || 1;

						if (!jS.evt.scroll.axis) {
							jS.evt.scroll.start(pos.axis);
						}
						var me = jS.evt.scroll.axis[pos.axis];

						//if (pos.value == me.value && me.value !== u) return;

						if (!pos.value) {
							if (!me.p) return;
							pos.value = me.p[arrHelpers.closest(me.v, Math.abs(pos.pixel / (me.sheetArea - me.area)) * 100, me.min)];
						}

						pos.max = pos.max || me.max;

						var i = me.min, indexes = [];

						while (i <= pos.value || i <= pos.max) {
							if (i < pos.value && i >= me.min) {
								indexes.push(i);
							}
							i++;
						}

						if (indexes.length) {
							if (me.scrollStyle) me.scrollStyle.trigger('updateStyle', [indexes]);
						} else {
							if (me.scrollStyle) me.scrollStyle.trigger('updateStyle');
						}

						me.value = pos.value;
					},

					/**
					 * Called after scroll is done
					 * @methodOf jS.evt.scroll
					 * @name stop
					 */
					stop:function () {
						if (this.axis.x.scrollUpdate) this.axis.x.scrollUpdate();
						if (this.axis.y.scrollUpdate) this.axis.y.scrollUpdate();

						if (jS.evt.scroll.td) {
							jS.evt.scroll.td = null;
							jS.autoFillerGoToTd();
						}
					}
				}
			},

			/**
			 *
			 * @param {Integer} start index to start from
			 * @methodOf jS
			 * @name refreshColumnLabels
			 */
			refreshColumnLabels:function (start) {
				start = start || 0;

				jS.obj.barMenuParentTop().trigger('destroy');

				var tds = jS.controls.bar.x.td[jS.i];

				if (!tds) return;

				for (var i = start; i < tds.length; i++) {
					if (i) {//greater than 1 (corner)
						$(tds[i]).text(jSE.columnLabelString(i));
					}
				}
			},


			/**
			 *
			 * @param {Integer} start index to start from
			 * @methodOf jS
			 * @name refreshRowLabels
			 */
			refreshRowLabels:function (start) {
				start = start || 0;

				var tds = jS.controls.bar.y.td[jS.i];

				if (!tds) return;

				for (var i = start; i < tds.length; i++) {
					if (i) {
						$(tds[i]).text(i);
					}
				}
			},

			/**
			 * Detects if an object is a td within a spreadsheet's table
			 * @param {jQuery|HTMLElement} o target
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name isTd
			 */
			isTd:function (o) {
				if (!o) return false;

				o = (o[0] ? o[0] : [o]);
				if (o[0]) {
					if (!isNaN(o[0].cellIndex)) {
						if (o[0].cellIndex > 0 && o[0].parentNode.rowIndex > 0) {
							return true;
						}
					}
				}
				return false;
			},

			/**
			 * Detects if an object is a bar td within a spreadsheet's table
			 * @param {jQuery|HTMLElement} o target
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name isBar
			 */
			isBar:function (o) {
				if (!o) return false;

				o = (o[0] ? o[0] : [o]);
				if (o[0]) {
					if (!isNaN(o[0].cellIndex)) {
						if (o[0].cellIndex == 0 || o[0].parentNode.rowIndex == 0) {
							return true;
						}
					}
				}
				return false;
			},

			/**
			 * Tracks read state of spreadsheet
			 * @memberOf jS
			 * @name readOnly
			 */
			readOnly:[],

			/**
			 * Detects read state of a spreadsheet
			 * @param {Integer} i index of spreadsheet within instance
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name isSheetEditable
			 */
			isSheetEditable:function (i) {
				i = i || jS.i;
				return (
					s.editable == true && !jS.readOnly[i]
					);
			},

			/**
			 * Detects read state of formula of an object
			 * @param {jQuery|HTMLElement} o target
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name isFormulaEditable
			 */
			isFormulaEditable:function (o) {
				if (s.lockFormulas) {
					if (o.data('formula') !== u) {
						return false;
					}
				}
				return true;
			},

			/**
			 * Toggles full screen mode
			 * @methodOf jS
			 * @name toggleFullScreen
			 */
			toggleFullScreen:function () {
				if (!jS) return;
				jS.evt.cellEditDone();
				var fullScreen = jS.obj.fullScreen();
				if (fullScreen.is(':visible')) {
					$body.removeClass('bodyNoScroll');
					s.parent = fullScreen.data('parent');

					var w = s.parent.width(),
						h = s.parent.height();

					s.width = w;
					s.height = h;

					s.parent.append(fullScreen.children())

					fullScreen.remove();

					jS.sheetSyncSize();

					jS.obj.pane().trigger('resizeScroll');

					jS.trigger('sheetFullScreen', [false]);
				} else { //here we make a full screen
					$body.addClass('bodyNoScroll');

					var w = $window.width() - 15,
						h = $window.height() - 15,
						parent = s.parent;

					s.width = w;
					s.height = h;

					s.parent = jS.controls.fullScreen[jS.i] = $('<div class="' + jS.cl.fullScreen + ' ' + jS.cl.uiFullScreen + '" />')
						.append(s.parent.children())
						.appendTo($body)
						.data('parent', s.parent);

					jS.obj.pane().trigger('resizeScroll');
					jS.sheetSyncSize();
					parent.trigger('sheetFullScreen', [true]);
				}
			},

			/**
			 * Assists in rename of spreadsheet
			 * @methodOf jS
			 * @name renameSheet
			 */
			renameSheet:function (i) {
				if (isNaN(i)) return false;

				if (i > -1)
					jS.sheetTab();
			},

			/**
			 * Switches spreadsheet
			 * @param {Integer} i index of spreadsheet within instance
			 * @methodOf jS
			 * @name switchSheet
			 */
			switchSheet:function (i) {
				if (isNaN(i)) return false;

				if (i == -1) {
					jS.addSheet('5x10');
				} else if (i != jS.i) {
					jS.setActiveSheet(i);
					jS.calc(i);
				}
			},

			/**
			 * Makes table object usable by sheet
			 * @param {jQuery|HTMLElement} o table
			 * @returns {*}
			 * @methodOf jS
			 * @name tuneTableForSheetUse
			 */
			tuneTableForSheetUse:function (o) {
				jS.controls.sheet[jS.i] = o
					.addClass(jS.cl.sheet)
					.attr('id', jS.id.sheet + jS.i)
					.attr('border', '1px')
					.attr('cellpadding', '0')
					.attr('cellspacing', '0');

				jS.controls.sheets = jS.obj.sheets().add(o);

				//override frozenAt settings with table's data-frozenatrow and data-frozenatcol
				var frozenAtRow = o.data('frozenatrow'),
					frozenAtCol = o.data('frozenatcol');

				if (!jS.s.frozenAt[jS.i]) jS.s.frozenAt[jS.i] = {row:0, col:0};
				if (frozenAtRow) jS.s.frozenAt[jS.i].row = frozenAtRow;
				if (frozenAtCol) jS.s.frozenAt[jS.i].col = frozenAtCol;

				return o;
			},

			/**
			 * Cycles through all the td's and turns table into spreadsheet
			 * @param {jQuery|HTMLElement} sheet spreadsheet table
			 * @param {Integer} i spreadsheet index within instance
			 * @param {Object} start {row, col}, index of column and or row to start at, can be null
			 * @methodOf jS
			 * @name createSpreadsheet
			 */
			createSpreadsheet:function (sheet, i, start) {
				sheet = sheet || jS.obj.sheet();
				i = i || jS.i;

				start = $.extend({row:0, col:0}, start);

				jS.spreadsheets[i] = []; //reset the sheet's spreadsheet

				var rows = jS.rows(sheet);
				$(rows).each(function (row) {
					$(this).children().each(function (col) {
						var td = $(this);

						if (row > 0 && col > 0) {
							jS.createCell(td, i, row, col, td.text(), td.data('formula'));
						} else {
							if (col == 0 && row > 0) { //barleft
								td
									.data('type', 'bar')
									.data('entity', 'left')
									.text(row)
									.attr('class', jS.cl.barLeft + ' ' + jS.cl.barLeft + '_' + jS.i + ' ' + jS.cl.uiBar);
							}

							if (row == 0 && col > 0) { //bartop
								td
									.data('type', 'bar')
									.data('entity', 'top')
									.text(jSE.columnLabelString(col))
									.attr('class', jS.cl.barTop + ' ' + jS.cl.barTop + '_' + jS.i + ' ' + jS.cl.uiBar);
							}

							if (row == 0 && col == 0) { //corner
								jS.controls.bar.corner[jS.i] = td
									.data('type', 'bar')
									.data('entity', 'corner')
									.attr('class', jS.cl.uiBar + ' ' + ' ' + jS.cl.barCorner);
							}
						}
					});
				});
			},

			/**
			 * Toggles cells from being hidden, not yet used needs a bit of work
			 * @memberOf jS
			 * @name toggleHide
			 */
			toggleHide:{
				hiddenRows:[],
				row:function (i) {
					i = i || jS.rowLast;
					if (!i) return;

					var row = jS.rows()[i],
						$row = $(row),
						style = [];

					if (!this.hiddenRows[jS.i]) this.hiddenRows[jS.i] = [];

					if ($row.length && $.inArray(i + 1, this.hiddenRows[jS.i]) < 0) {
						this.hiddenRows[jS.i].push(i + 1);
					} else {
						this.hiddenRows[jS.i].splice(this.hiddenRows[jS.i].indexOf(i + 1), 1);
					}

					jS.obj.toggleHideStyleY().trigger('updateStyle');
				},
				rowShowAll:function () {
					$.each(this.hiddenRows[jS.i], function (j) {
						$(this).removeData('hidden');
					});
					jS.obj.toggleHideStyleY().html('');
					this.hiddenRows[jS.i] = [];
				},

				hiddenColumns:[],
				columnIndexOffset:[],
				column:function (i) {
					i = i || jS.colLast;
					if (!i) return;

					var col = jS.cols()[i],
						$col = $(col),
						style = [];

					if (!this.hiddenColumns[jS.i]) this.hiddenColumns[jS.i] = [];

					if ($col.length && $.inArray(i + 1, this.hiddenColumns[jS.i]) < 0) {
						this.hiddenColumns[jS.i].push(i + 1);
					} else {
						this.hiddenColumns[jS.i].splice(this.hiddenColumns[jS.i].indexOf(i + 1), 1);
					}

					jS.obj.toggleHideStyleX().trigger('updateStyle');
				},
				columnShowAll:function () {
					jS.obj.toggleHideStyleX().html('');
					this.hiddenColumns[jS.i] = [];
				}
			},

			merged:[],

			/**
			 * Merges cells together
			 * @methodOf jS
			 * @name merge
			 */
			merge:function () {
				var cellsValue = [],
					tds = jS.obj.cellHighlighted(),
					tdFirstLoc = jS.getTdLocation(tds.first()),
					tdLastLoc = jS.getTdLocation(tds.last()),
					colI = 0,
					rowI = 0,
					firstCell = jS.spreadsheets[jS.i][tdFirstLoc.row][tdFirstLoc.col],
					last = new Date();

				if (tds.length > 1 && tdFirstLoc.row) {
					jS.setDirty(true);
					jS.setChanged(true);

					//create a group to be merged into 1
					if (!jS.merged[jS.i + '_' + tdFirstLoc.row + '_' + tdFirstLoc.col]) jS.merged[jS.i + '_' + tdFirstLoc.row + '_' + tdFirstLoc.col] = [];
					var merged = jS.merged[jS.i + '_' + tdFirstLoc.row + '_' + tdFirstLoc.col];

					for (var row = tdFirstLoc.row; row <= tdLastLoc.row; row++) {
						if (row) {
							rowI++;
						}
						for (var col = tdFirstLoc.col; col <= tdLastLoc.col; col++) {
							if (row == tdFirstLoc.row) {
								colI++;
							}
							var td = jS.getTd(jS.i, row, col),
								cell = jS.spreadsheets[jS.i][row][col],
								cellLeft = jS.spreadsheets[jS.i][row][tdFirstLoc.col - 1] || jS.spreadsheets[jS.i][row][tdFirstLoc.col],
								cellRight = jS.spreadsheets[jS.i][row][tdLastLoc.col + 1] || jS.spreadsheets[jS.i][row][tdLastLoc.col],
								cellUp = jS.spreadsheets[jS.i][tdLastLoc.row - 1][tdLastLoc.col] || jS.spreadsheets[jS.i][tdLastLoc.row][tdLastLoc.col],
								cellDown = jS.spreadsheets[jS.i][tdLastLoc.row + 1][tdLastLoc.col] || jS.spreadsheets[jS.i][tdLastLoc.row][tdLastLoc.col];

							merged.push(cell);

							cellsValue.push(cell.formula ? "(" + cell.formula.substring(1) + ")" : cell.value);

							s.parent.one('sheetPreCalculation', function () {
								if (col != tdFirstLoc.col || row != tdFirstLoc.row) {
									cell.formula = null;
									cell.value = '';
									cell.html = '';
									cell.defer = firstCell;
									cell.right = cellRight;
									cell.down = cellDown;
									cell.left = cellLeft;
									cell.up = cellUp;

									td
										.removeData('formula')
										.html('')
										.hide();
								}
							});

							jS.calcDependencies(jS.i, row, col, last);
						}
					}


					firstCell.value = cellsValue.join(' ');
					firstCell.formula = (firstCell.formula ? cellsValue.join(' ') : '');

					tds.first()
						.show()
						.attr('rowSpan', rowI)
						.attr('colSpan', colI);

					jS.calcDependencies(jS.i, tdFirstLoc.row, tdFirstLoc.col);
					jS.evt.cellEditDone();
				}
			},

			/**
			 * Unmerges cells together
			 * @methodOf jS
			 * @name unmerge
			 */
			unmerge:function () {
				var td = jS.obj.cellHighlighted().first(),
					loc = jS.getTdLocation(td),
					cellFirst = jS.spreadsheets[jS.i][loc.row][loc.col],
					formula = td.data('formula'),
					last = new Date();

				var rowMax = Math.max(td.attr('rowSpan') * 1, 1);
				var colMax = Math.max(td.attr('colSpan') * 1, 1);

				for (var row = loc.row; row <= loc.row + rowMax; row++) {
					for (var col = loc.col; col <= loc.col + colMax; col++) {
						var td = jS.getTd(jS.i, row, col)
								.show()
								.removeAttr('colSpan')
								.removeAttr('rowSpan'),
							cell = jS.spreadsheets[jS.i][row][col];

						cell.up = cell.down = cell.left = cell.right = cell.defer = null;

						jS.calcDependencies(jS.i, row, col, last);
					}
				}
			},

			/**
			 * Fills values down or up to highlighted cells from active cell;
			 * @param {Boolean} goUp default is down, when set to true value are filled from bottom, up;
			 * @param {Boolean} skipOffsetForumals default is formulas will offest, when set to true formulas will stay static;
			 * @param {String} v the value to set cells to, if not set, formula will be used;
			 * @methodOf jS
			 * @name fillUpOrDown
			 */
			fillUpOrDown:function (goUp, skipOffsetForumals, v) {
				var cells = jS.obj.cellHighlighted(),
					cellActive = jS.obj.cellActive(),
					last = new Date();

				var startFromActiveCell = cellActive.hasClass(jS.cl.uiCellHighlighted),
					startLoc = jS.getTdLocation(cells.first()),
					endLoc = jS.getTdLocation(cells.last());

				v = (v ? v : jS.obj.formula().val()); //allow value to be overridden

				var offset = {
						row:0,
						col:0
					},
					newV = v,
					fn,
					cell;
				if (v.charAt(0) == '=') {
					fn = function (sheet, row, col) {
						if (goUp) {
							offset.row = -endLoc.row + row;
							offset.col = -endLoc.col + col;
						} else {
							offset.row = row - startLoc.row;
							offset.col = col - startLoc.col;
						}

						newV = jS.reparseFormula(v, offset);
						s.parent.one('sheetPreCalculation', function () {
							cell = jS.spreadsheets[sheet][row][col];
							cell.formula = newV;
							cell.value = '';
							cell.td.data('formula', newV);
						});

						jS.calcDependencies(sheet, row, col, last);
					};
				} else {
					if (goUp && !isNaN(newV)) {
						newV *= 1;
						newV -= endLoc.row;
						newV -= endLoc.col;
					}
					fn = function (sheet, row, col) {
						s.parent.one('sheetPreCalculation', function () {
							cell = jS.spreadsheets[sheet][row][col];
							cell.formula = '';
							cell.value = newV;
							cell.td.removeData('formula');
						});

						jS.calcDependencies(sheet, row, col, last);

						if (!isNaN(newV) && newV != '') newV++;
					};
				}

				jS.cycleCells(fn, startLoc, endLoc);
			},

			tdsToTsv:function (tds, clearValue, fnEach) {
				tds = tds || jS.obj.cellHighlighted();
				fnEach = fnEach || function (loc, cell) {
					if (clearValue) {
						s.parent.one('sheetPreCalculation', function () {
							cell.formula = '';
							cell.value = '';
						});
						jS.calcDependencies(jS.i, loc.row, loc.col, last);
					}
				};
				var cells = [],
					cellsTsv,
					formula = jS.obj.formula(),
					oldValue = formula.val(),
					firstRowI = 0,
					last = new Date();


				tds.each(function (i) {
					var loc = jS.getTdLocation(tds[i]),
						cell = jS.spreadsheets[jS.i][loc.row][loc.col],
						value = (cell.formula ? '=' + cell.formula : cell.value);

					if (!firstRowI) firstRowI = loc.row;

					if (!cells[loc.row - firstRowI]) cells[loc.row - firstRowI] = [];

					if ((value + '').match(/\n/)) {
						value = '"' + value + '"';
					}

					cells[loc.row - firstRowI].push(value || '');

					fnEach.apply(this, [loc, cell]);
				});

				for (var i in cells) {
					cells[i] = cells[i].join('\t');
				}

				return cells.join('\n');
			},

			/**
			 * Makes cell formulas increment within a range
			 * @param {Object} loc {row: int, col: int}
			 * @param {Object} offset {row: int,col: int} offsets increment
			 * @param {Boolean} isBefore inserted before location
			 * @methodOf jS
			 * @name offsetFormulas
			 */
			offsetFormulas:function (loc, offset, isBefore) {
				var size = jS.sheetSize(),
				//shifted range is the range of cells that are moved
					shiftedRange = {
						first:loc,
						last:{
							row:size.rows,
							col:size.cols
						}
					},
				//effected range is the entire spreadsheet
					affectedRange = {
						first:{
							row:0,
							col:0
						},
						last:{
							row:size.rows,
							col:size.cols
						}
					};

				jS.log("offsetFormulas from - Col:" + loc.col + ',Row:' + loc.row);
				jS.log("Is before loc:" + (isBefore ? 'true' : 'false'));
				jS.log("Offset: - Col:" + offset.col + ',Row:' + offset.row);

				function isInFormula(thisLoc, rowOrCol) {
					var move = false;

					if (isBefore) {
						if (thisLoc >= rowOrCol)
							move = true;
					} else {
						if (thisLoc > rowOrCol)
							move = true;
					}

					return move;
				}

				jS.cycleCells(function (sheet, row, col) {
					var td = $(this),
						formula = td.data('formula');

					if (formula && jS.isFormulaEditable(td)) {
						formula = jS.reparseFormula(formula, offset, function (thisLoc) {
							return {
								row:isInFormula(thisLoc.row, loc.row),
								col:isInFormula(thisLoc.col, loc.col)
							};
						});

						jS.spreadsheets[sheet][row][col].formula = formula;
						td.data('formula', formula);
					}

				}, affectedRange.first, affectedRange.last);


				jS.evt.cellEditDone();
				jS.calc();
			},

			/**
			 * Reparses a formula
			 * @param formula
			 * @param {Object} offset {row: int,col: int} offsets increment
			 * @param {Function} fn Sent the current location of what is being reparsed
			 * @returns {String}
			 * @methodOf jS
			 * @name reparseFormula
			 */
			reparseFormula:function (formula, offset, fn) {
				return formula.replace(jSE.regEx.cell, function (ignored, col, row, pos) {
					if (col == "SHEET") return ignored;

					var loc = jSE.parseLocation(ignored);

					if (fn) {
						var move = fn(loc);


						if (move.col || move.row) {
							if (move.col) loc.col += offset.col;
							if (move.row) loc.row += offset.row;

							return jS.makeFormula(loc);
						}
					} else {
						return jS.makeFormula(loc, offset);
					}

					return ignored;
				});
			},

			/**
			 * Reconstructs a formula
			 * @param {Object} loc {row: i, col: i}
			 * @param {Object} offset {row: i, col: i}
			 * @returns {String}
			 * @methodOf jS
			 * @name makeForumla
			 */
			makeFormula:function (loc, offset) {
				offset = $.extend({row:0, col:0}, offset);

				//set offsets
				loc.col += offset.col;
				loc.row += offset.row;

				//0 based now
				if (loc.col < 0) loc.col = 0;
				if (loc.row < 0) loc.row = 0;

				return jSE.parseCellName(loc.col, loc.row);
			},

			/**
			 * Cylces through a certain group of td objects in a spreadsheet table and applies a function to them
			 * @param {Function} fn the function to apply to a cell
			 * @param {Object} firstLoc {row: 0, col: 0} the cell to start at
			 * @param {Object} lastLoc {row: 0, col: 0} the cell to end at
			 * @param {Integer} i spreadsheet index within instance
			 * @methodOf jS
			 * @name cycleCells
			 */
			cycleCells:function (fn, firstLoc, lastLoc, i) {
				i = i || jS.i;
				firstLoc = firstLoc || {row:0, col:0};

				if (!lastLoc) {
					var size = jS.sheetSize($('#' + jS.id.sheet + i));
					lastLoc = {row:size.rows, col:size.cols};
				}

				for (var row = firstLoc.row; row <= lastLoc.row; row++) {
					for (var col = firstLoc.col; col <= lastLoc.col; col++) {
						var td = jS.getTd(i, row, col);
						if (td) {
							fn.apply(td, [i, row, col]);
						}
					}
				}
			},

			/**
			 * Cylces through all td objects in a spreadsheet table and applies a function to them
			 * @param fn
			 * @methodOf jS
			 * @name cycleCellsAll
			 */
			cycleCellsAll:function (fn) {
				for (var i = 0; i <= jS.sheetCount; i++) {
					var size = jS.sheetSize($('#' + jS.id.sheet + i)),
						endLoc = {row:size.rows, col:size.cols};
					jS.cycleCells(fn, {row:0, col:0}, endLoc, i);
				}
			},

			/**
			 * Cylces through a certain group of td objects in a spreadsheet table and applies a function to them, firstLoc can be bigger then lastLoc, this is more dynamic
			 * @param {Function} fn the function to apply to a cell
			 * @param {Object} firstLoc {row: 0, col: 0} the cell to start at
			 * @param {Object} lastLoc {row: 0, col: 0} the cell to end at
			 * @returns {Array} of td objects
			 * @methodOf jS
			 * @name cycleCellsAndMaintainPoint
			 */
			cycleCellsAndMaintainPoint:function (fn, firstLoc, lastLoc) {
				var td = $([]),
					rowMin = Math.min(firstLoc.row, lastLoc.row),
					colMin = Math.min(firstLoc.col, lastLoc.col),
					rowMax = Math.max(firstLoc.row, lastLoc.row),
					colMax = Math.max(firstLoc.col, lastLoc.col);

				for (var row = rowMin; row <= rowMax; row++) {
					for (var col = colMin; col <= colMax; col++) {
						td = td.add(jS.getTd(jS.i, row, col));
						fn(td[td.length - 1]);
					}
				}

				return td;
			},

			/**
			 * Prepairs a table for use as a sheet
			 * @param {jQuery|HTMLElement} o table object
			 * @methodOf jS
			 * @name sheetDecorate
			 */
			sheetDecorate:function (o) {
				jS.formatSheet(o);
				jS.sheetDecorateRemove(false, o);
			},

			/**
			 * Adds tbody, colgroup, heights and widths to different parts of a spreadsheet
			 * @param {jQuery|HTMLElement} o table object
			 * @methodOf jS
			 * @name formatSheet
			 */
			formatSheet:function (o) {
				var w = s.newColumnWidth,
					h = s.colMargin,
					tbody = o.children('tbody');

				if (tbody.length < 1) {
					tbody = $('<tbody />');
					o.wrapInner(tbody);
				}

				var colgroup = o.children('colgroup');
				if (colgroup.length < 1 || colgroup.children('col').length < 1) {
					o.remove('colgroup');
					colgroup = $('<colgroup />')
						.prependTo(o);
					var firstRow = tbody.children('tr:first');
					firstRow.children().each(function () {
						$('<col />')
							.width(w)
							.css('width', w + 'px')
							.attr('width', w + 'px')
							.appendTo(colgroup);
					});
					tbody.children('tr').each(function () {
						$(this)
							.height(h)
							.css('height', h + 'px')
							.attr('height', h + 'px');
					});
				}

				o
					.removeAttr('width')
					.css('width', '');
			},

			/**
			 * Ensure sheet minimums have been met, if not add columns and rows
			 * @param {jQuery|HTMLElement} o table object
			 * @methodOf jS
			 * @name checkMinSize
			 */
			checkMinSize:function (o) {
				var size = jS.sheetSize(o),
					addRows = 0,
					addCols = 0;

				if (size.cols < s.minSize.cols) {
					jS.controlFactory.addColumnMulti(null, s.minSize.cols - size.cols);
				}

				if (size.rows < s.minSize.rows) {
					jS.controlFactory.addRowMulti(null, s.minSize.rows - size.rows);
				}
			},

			/**
			 * jQuery ui Themeroller integration
			 * @memberOf jS
			 * @name themeRoller
			 * @namespace
			 */
			themeRoller:{

				/**
				 * Starts themeroller integration
				 * @param {jQuery|HTMLElement} sheet spreadsheet table
				 * @methodOf jS.themeRoller
				 * @name start
				 */
				start:function (sheet) {
					s.parent.addClass(jS.cl.uiParent);
					sheet.addClass(jS.cl.uiSheet);

					jS.obj.header().addClass(jS.cl.uiControl);
					jS.obj.label().addClass(jS.cl.uiControl);
					jS.obj.formula().addClass(jS.cl.uiControlTextBox);
				},

				/**
				 * Themeroller cell interactions
				 * @memberOf jS.themeRoller
				 * @name cell
				 * @namespace
				 */
				cell:{

					/**
					 * Highlights td object
					 * @param {jQuery|HTMLElement} td td object
					 * @methodOf jS.themeRoller.cell
					 * @name setHighlighted
					 */
					setHighlighted:function (td) {
						$(td)
							.addClass(jS.cl.uiCellHighlighted);
					},

					/**
					 * Detects if there is a cell hlighlighted
					 * @returns {Boolean}
					 * @methodOf jS.themeRoller.cell
					 * @name isHighlighted
					 */
					isHighlighted:function () {
						return (jS.highlightedLast.td.length ? true : false);
					},

					/**
					 * Clears highlighted cells
					 * @methodOf jS.themeRoller.cell
					 * @name clearHighlighted
					 */
					clearHighlighted:function () {
						if (jS.themeRoller.cell.isHighlighted()) {
							jS.obj.cellHighlighted()
								.removeClass(jS.cl.uiCellHighlighted);
						}

						jS.highlightedLast.rowStart = 0;
						jS.highlightedLast.colStart = 0;

						jS.highlightedLast.rowEnd = 0;
						jS.highlightedLast.colEnd = 0;
						jS.highlightedLast.td = $([]);
					}
				},

				/**
				 * Themeroller bar interactions
				 * @memberOf jS.themeRoller
				 * @name bar
				 * @namespace
				 */
				bar:{

					/**
					 * Adds initial style to bar
					 * @param {jQuery|HTMLElement} o bar object
					 * @methodOf jS.themeRoller.bar
					 * @name style
					 */
					style:function (o) {
						$(o).addClass(jS.cl.uiBar);
					},

					/**
					 * Sets a bar to be active
					 * @param {String} direction left or top
					 * @param {Integer} i index of bar
					 * @methodOf jS.themeRoller.bar
					 * @name setActive
					 */
					setActive:function (direction, i) {
						//We don't clear here because we can have multi active bars
						switch (direction) {
							case 'top':
								jS.obj.barTop(i).addClass(jS.cl.uiBarHighlight);
								break;
							case 'left':
								jS.obj.barLeft(i).addClass(jS.cl.uiBarHighlight);
								break;
						}
					},

					/**
					 * Clears bars from being active
					 * @methodOf jS.themeRoller.bar
					 * @name clearActive
					 */
					clearActive:function () {
						jS.obj.barTops()
							.removeClass(jS.cl.uiBarHighlight);

						jS.obj.barLefts()
							.removeClass(jS.cl.uiBarHighlight);
					}
				},

				/**
				 * Themeroller tab interactions
				 * @memberOf jS.themeRoller
				 * @name tab
				 * @namespace
				 */
				tab:{

					/**
					 * Sets a tab to be active
					 * @param {jQuery|HTMLElement} o tab object
					 * @methodOf jS.themeRoller.tab
					 * @name setActive
					 */
					setActive:function (o) {
						this.clearActive();
						jS.obj.tab().addClass(jS.cl.uiTabActive);
					},

					/**
					 * Clears a tab from being active
					 * @methodOf jS.themeRoller.tab
					 * @name clearActive
					 */
					clearActive:function () {
						jS.obj.tabContainer().find('span.' + jS.cl.uiTabActive)
							.removeClass(jS.cl.uiTabActive);
					}
				}
			},

			/**
			 * jQuery ui resizeable integration
			 * @param {jQuery|HTMLElement} o To set resizable
			 * @param {Object} settings the settings used with jQuery ui resizable
			 * @methodOf jS
			 * @name resizable
			 */
			resizable:function (o, settings) {
				if (!o.data('resizable')) {
					o.resizable(settings);
				}
			},

			frozenAt:function () {
				if (!jS.s.frozenAt[jS.i]) jS.s.frozenAt[jS.i] = {row:0, col:0};
				return jS.s.frozenAt[jS.i];
			},

			scrolledTo:function () {
				if (!jS.scrolledArea[jS.i]) jS.scrolledArea[jS.i] = {col:{start:jS.frozenAt().col, end:jS.frozenAt().col}, row:{start:jS.frozenAt().row, end:jS.frozenAt().row}};
				return jS.scrolledArea[jS.i];
			},

			/**
			 * instance busy state
			 * @memberOf jS
			 * @name busy
			 */
			busy:[],


			/**
			 * Set the spreadsheet busy status
			 * @param {Boolean} busy
			 * @memberOf jS
			 * @name setBusy
			 */
			setBusy:function (busy) {
				if (busy) {
					jS.busy.push(busy);
				} else {
					jS.busy.pop();
				}
			},

			isBusy:function () {
				return (jS.busy.length > 0 ? true : false);
			},

			/**
			 * jQuery ui draggable integration
			 * @param {jQuery|HTMLElement} o To set resizable
			 * @param {Object} settings the settings used with jQuery ui resizable
			 * @methodOf jS
			 * @name draggable
			 */
			draggable:function (o, settings) {
				if (!o.data('jSdraggable')) {
					o
						.data('jSdraggable', true)
						.draggable(settings);
				}
			},

			/**
			 * jQuery nearest integration
			 * @param o
			 * @param settings
			 * @methodOf jS
			 * @name nearest
			 */
			nearest:function (o, settings) {
				return $(o).nearest(settings);
			},

			/**
			 * Bar resizing
			 * @memberOf jS
			 * @name resizeBar
			 * @namespace
			 */
			resizeBar:{

				/**
				 * Provides the top bar with ability to resize
				 * @param {jQuery|HTMLElement} bar td bar object
				 * @param {Integer} i index of bar
				 * @param {jQuery|HTMLElement} pane spreadsheet pane
				 * @param {jQuery|HTMLElement} sheet spreadsheet table
				 * @methodOf jS.resizeBar
				 * @name top
				 */
				top:function (bar, i, pane, sheet) {
					jS.obj.barTopControls().remove();
					var barController = $('<div class="' + jS.cl.barController + '" />')
						.width(bar.width())
						.height(0)
						.prependTo(bar);

					jS.controls.bar.x.controls[jS.i] = jS.obj.barTopControls().add(barController);

					jS.resizableCells(barController, {
						handles:'e',
						start:function (e, ui) {
							jS.autoFillerHide();
							jS.setBusy(true);
							this.col = $(jS.col(sheet, i));
						},
						resize:function (e, ui) {
							this.col
								.width(ui.size.width)
								.attr('width', ui.size.width + 'px')
								.css('width', ui.size.width + 'px');
						},
						stop:function (e, ui) {
							jS.setBusy(false);
							pane.trigger('resizeScroll');
							jS.followMe();
							jS.setDirty(true);
						}
					});
				},

				/**
				 * Provides the left bar with ability to resize
				 * @param {jQuery|HTMLElement} bar td bar object
				 * @param {Integer} i index of bar
				 * @param {jQuery|HTMLElement} pane spreadsheet pane
				 * @param {jQuery|HTMLElement} sheet spreadsheet table
				 * @methodOf jS.resizeBar
				 * @name left
				 */
				left:function (bar, i, pane, sheet) {
					jS.obj.barLeftControls().remove();
					var offset = bar.offset(),
						barController = $('<div class="' + jS.cl.barController + '"></div>')
							.prependTo(bar)
							.offset({
								top:offset.top,
								left:offset.left
							});

					jS.controls.bar.y.controls[jS.i] = jS.obj.barLeftControls().add(barController);

					var child = $('<div class="barControllerChild"></div>')
							.height(bar.height())
							.prependTo(barController),

						me = bar.parent().add(bar).add(barController);

					jS.resizableCells(child, {
						handles:'s',
						start:function () {
							jS.autoFillerHide();
							jS.setBusy(true);
						},
						resize:function (e, ui) {
							me
								.height(ui.size.height)
								.attr('height', (ui.size.height))
								.css('height', ui.size.height + 'px');
						},
						stop:function (e, ui) {
							jS.setBusy(false);
							pane.trigger('resizeScroll');
							jS.followMe();
							jS.setDirty(true);
						}
					});
				},

				/**
				 * Provides the corner bar, just a place holder, needed for auto events
				 * @methodOf jS.resizeBar
				 * @name corner
				 */
				corner:function () {
				}
			},

			/**
			 * Removes sheet decorations
			 * @param {Boolean} makeClone creates a clone rather than the actual object
			 * @param {jQuery|HTMLElement} sheets spreadsheet table object to remove decorations from
			 * @returns {jQuery|HTMLElement}
			 * @methodOf jS
			 * @name sheetDecorateRemove
			 */
			sheetDecorateRemove:function (makeClone, sheets) {
				sheets = sheets || jS.obj.sheets();
				sheets = (makeClone ? sheets.clone() : sheets);

				//Get rid of highlighted cells and active cells
				sheets.find('td.' + jS.cl.uiCellActive)
					.removeClass(jS.cl.uiCellActive);

				sheets.find('td.' + jS.cl.uiCellHighlighted)
					.removeClass(jS.cl.uiCellHighlighted);
				return sheets;
			},

			/**
			 * Removed bars from spreadsheet table
			 * @param {jQuery|HTMLElement} sheet spreadsheet table object to remove bars from
			 * @returns {jQuery|HTMLElement}
			 * @methodOf jS
			 * @name sheetBarsRemove
			 */
			sheetBarsRemove:function (sheet) {
				sheet = $(sheet ? sheet : jS.obj.sheets());
				sheet.find('tr.' + jS.cl.barTopParent).remove();
				sheet.find('td.' + jS.cl.barLeft).remove();
				return sheet;
			},

			/**
			 * Updates the label so that the user knows where they are currently positioned
			 * @param {String|Object} v Value to update to, if object {col, row}
			 * @param {Boolean} setDirect
			 * @methodOf jS
			 * @name labelUpdate
			 */
			labelUpdate:function (v, setDirect) {
				if (!setDirect) {
					v = jSE.parseCellName(v.col, v.row);
					if (v) jS.obj.label().text(v);
				} else {
					jS.obj.label().text(v);
				}
			},

			/**
			 * Starts td to be edited
			 * @param {jQuery|HTMLElement} td
			 * @param {Boolean} isDrag should be determined by if the user is dragging their mouse around setting cells
			 */
			cellEdit:function (td, isDrag) {
				if (td.is(jS.cellLast.td)) return;

				jS.autoFillerNotGroup = true; //make autoFiller directional again.
				//This finished up the edit of the last cell
				jS.evt.cellEditDone();

				var loc = jS.getTdLocation(td);
				if (!jS.spreadsheets[jS.i] || !jS.spreadsheets[jS.i][loc.row] || !jS.spreadsheets[jS.i][loc.row][loc.col]) return;
				var cell = jS.spreadsheets[jS.i][loc.row][loc.col],
					v;

				jS.trigger('sheetCellEdit', [cell]);

				jS.followMe(td);

				//Show where we are to the user
				jS.labelUpdate(loc);

				if (cell.formula) {
					v = '=' + cell.formula;
				} else {
					v = cell.value;
				}

				var formula = jS.obj.formula()
					.val(v)
					.blur();

				jS.cellSetActive(td, loc, isDrag);
			},

			/**
			 * sets cell active to sheet, and highlights it for the user, shouldn't be called directly, should use cellEdit
			 * @param {jQuery|HTMLElement} td
			 * @param {Object} loc {col, row}
			 * @param {Boolean} isDrag should be determined by if the user is dragging their mouse around setting cells
			 * @param {Boolean} directional makes highlighting directional, only left/right or only up/down
			 * @param {Function} fnDone called after the cells are set active
			 * @memberOf jS
			 * @name cellSetActive
			 */
			cellSetActive:function (td, loc, isDrag, directional, fnDone) {
				if (loc.col != u) {
					jS.cellLast.td = td; //save the current cell/td

					jS.cellLast.row = jS.rowLast = loc.row;
					jS.cellLast.col = jS.colLast = loc.col;

					jS.themeRoller.bar.clearActive();
					jS.themeRoller.cell.clearHighlighted();

					jS.highlightedLast.td = td;

					jS.themeRoller.cell.setHighlighted(td); //themeroll the cell and bars
					jS.themeRoller.bar.setActive('left', jS.cellLast.row);
					jS.themeRoller.bar.setActive('top', jS.cellLast.col);

					var selectModel,
						clearHighlightedModel;

					jS.highlightedLast.rowStart = loc.row;
					jS.highlightedLast.colStart = loc.col;
					jS.highlightedLast.rowLast = loc.row;
					jS.highlightedLast.colLast = loc.col;

					switch (s.cellSelectModel) {
						case 'excel':
						case 'gdrive':
							selectModel = function () {
							};
							clearHighlightedModel = jS.themeRoller.cell.clearHighlighted;
							break;
						case 'oo':
							selectModel = function (target) {
								var td = $(target);
								if (jS.isTd(td)) {
									jS.cellEdit(td);
								}
							};
							clearHighlightedModel = function () {
							};
							break;
					}

					if (isDrag) {
						var lastLoc = loc; //we keep track of the most recent location because we don't want tons of recursion here
						jS.obj.pane()
							.mousemove(function (e) {
								if (jS.isBusy()) return false;

								var endLoc = jS.getTdLocation(e.target);

								if (endLoc.col < 1 || endLoc.row < 1) return false; //bar

								var ok = true;

								if (directional) {
									ok = false;
									if (loc.col == endLoc.col || loc.row == endLoc.row) {
										ok = true;
									}
								}

								if ((lastLoc.col != endLoc.col || lastLoc.row != endLoc.row) && ok) { //this prevents this method from firing too much
									//clear highlighted cells if needed
									clearHighlightedModel();

									//set current bars
									jS.highlightedLast.colEnd = endLoc.col;
									jS.highlightedLast.rowEnd = endLoc.row;

									//select active cell if needed
									selectModel(e.target);

									//highlight the cells
									jS.highlightedLast.td = jS.cycleCellsAndMaintainPoint(jS.themeRoller.cell.setHighlighted, loc, endLoc);
								}

								lastLoc = endLoc;
							});

						$document
							.one('mouseup', function () {
								jS.obj.pane()
									.unbind('mousemove')
									.unbind('mouseup');

								if ($.isFunction(fnDone)) {
									fnDone();
								}
							});
					}
				}
			},

			/**
			 * the most recent used column
			 * @memberOf jS
			 * @name colLast
			 */
			colLast:0,

			/**
			 * the most recent used row
			 * @memberOf jS
			 * @name rowLast
			 */
			rowLast:0,

			/**
			 * the most recent used cell, {td, row, col, isEdit}
			 * @memberOf jS
			 * @type {Object}
			 * @name cellLast
			 */
			cellLast:{
				td:$([]), //this is a dud td, so that we don't get errors
				row:0,
				col:0,
				isEdit:false
			},

			/**
			 * the most recent highlighted cells {td, rowStart, colStart, rowEnd, colEnd}
			 * @memberOf jS
			 * @type {Object}
			 * @name highlightedLast
			 */
			highlightedLast:{
				td:$([]),
				rowStart:0,
				colStart:0,
				rowEnd:0,
				colEnd:0
			},

			/**
			 * sets a cells class for styling
			 * @param {String} setClass class(es) to set cells to
			 * @param {String} removeClass class(es) to remove from cell if the setClass would conflict with
			 * @returns {Boolean}
			 * @methodOf jS
			 * @name cellStyleToggle
			 */
			cellStyleToggle:function (setClass, removeClass) {
				jS.setDirty(true);
				//Lets check to remove any style classes
				var tds = jS.obj.cellHighlighted();

				//TODO: use calcDependencies and sheetPreCalculation to set undo redo data

				if (removeClass) {
					tds.removeClass(removeClass);
				}
				//Now lets add some style
				if (tds.hasClass(setClass)) {
					tds.removeClass(setClass);
				} else {
					tds.addClass(setClass);
				}

				return false;
			},

			/**
			 * Resizes fonts in a cell by 1 pixel
			 * @param {String} direction "up" or "down"
			 * @methodOf jS
			 * @name fontReSize
			 */
			fontReSize:function (direction) {
				var resize = 0;
				switch (direction) {
					case 'up':
						resize = 1;
						break;
					case 'down':
						resize = -1;
						break;
				}

				//Lets check to remove any style classes
				var uiCell = jS.obj.cellHighlighted();

				//TODO: use calcDependencies and sheetPreCalculation to set undo redo data

				uiCell.each(function (i) {
					cell = $(this);
					var curr_size = (cell.css("font-size") + '').replace("px", ""),
						new_size = parseInt(curr_size ? curr_size : 10) + resize;
					cell.css("font-size", new_size + "px");
				});

			},

			/**
			 * Current number of cells being parsed
			 * @type {Integer}
			 * @memberOf jS
			 * @name callStack
			 */
			callStack:0,

			/**
			 * Ignites calculation with cell, is recursively called if cell uses value from another cell
			 * @param {Integer} sheet sheet index within instance
			 * @param {Integer} row row index
			 * @param {Integer} col col index
			 * @returns {*} cell value after calculated
			 * @name updateCellValue
			 * @methodOf jS
			 */
			updateCellValue:function (sheet, row, col) {
				//first detect if the cell exists if not return nothing
				if (!jS.spreadsheets[sheet]) return s.error({error:jS.msg.notFoundSheet});
				if (!jS.spreadsheets[sheet][row]) return s.error({error:jS.msg.notFoundRow});
				if (!jS.spreadsheets[sheet][row][col]) return s.error({error:jS.msg.notFoundColumn});

				var cell = jS.spreadsheets[sheet][row][col],
					fn;
				cell.oldValue = cell.value; //we detect the last value, so that we don't have to update all cell, thus saving resources

				if (cell.result) { //unset the last result if it is set
					delete cell.result;
				}

				switch (cell.state) {
					case 'updating':
						return s.error({error:jS.msg.loopDetected});
					case 'updatingDependencies':
						return cell.valueOverride || cell.value;
				}

				if (cell.defer) {//merging creates a defer property, which points the cell to another location to get the other value
					return this.updateCellValue(cell.defer.sheet, cell.defer.row, cell.defer.col);
				}

				cell.state = 'updating';
				cell.html = [];
				cell.fnCount = 0;
				cell.result = null;

				if (cell.calcLast != jS.calcLast || cell.calcDependenciesLast != jS.calcDependenciesLast) {
					cell.valueOverride = null;
					cell.calcLast = jS.calcLast;
					cell.calcDependenciesLast = jS.calcDependenciesLast;

					cell.calcCount++;
					if (cell.formula) {
						try {
							if (cell.formula.charAt(0) == '=') {
								cell.formula = cell.formula.substring(1);
							}

							var formulaParser;
							if (jS.callStack) { //we prevent parsers from overwriting each other
								if (!cell.formulaParser) { //cut down on un-needed parser creation
									cell.formulaParser = (new jS.formulaParser);
								}
								formulaParser = cell.formulaParser
							} else {//use the sheet's parser if there aren't many calls in the callStack
								formulaParser = jS.FormulaParser;
							}

							jS.callStack++
							formulaParser.lexer.obj = {
								type:'cell',
								sheet:sheet,
								row:row,
								col:col,
								obj:cell,
								s:s,
								editable:s.editable,
								jS:jS,
								error:s.error
							};
							formulaParser.lexer.handler = jS.cellHandler;
							cell.result = formulaParser.parse(cell.formula);
						} catch (e) {
							cell.result = e.toString();
							jS.alertFormulaError(cell.value);
						}
						jS.callStack--;
						cell = jS.filterValue(cell, sheet, row, col);
					} else {
						fn = jS.s.cellStartingHandlers[cell.value.charAt(0)];
						if (fn) {
							fn.apply(cell, [cell.value]);
						} else {
							cell = jS.filterValue(cell, sheet, row, col);
						}
					}
				}

				cell.state = null;
				return cell.valueOverride || cell.value;
			},

			updateCellDependencies:function (sheet, row, col) {
				var cell = jS.spreadsheets[sheet][row][col];
				if (cell.state) return;
				cell.state = 'updatingDependencies';
				var dependencies = $.extend({}, cell.dependencies);
				cell.dependencies = [];
				for (var i in dependencies) {
					var dependantCell = dependencies[i],
						dependantCellLoc = jS.getTdLocation(dependantCell.td);

					jS.updateCellValue(dependantCell.sheet, dependantCellLoc.row, dependantCellLoc.col);
					if (dependantCellLoc.row && dependantCellLoc.col) {
						jS.updateCellDependencies(dependantCell.sheet, dependantCellLoc.row, dependantCellLoc.col);
					}
				}
				cell.state = null;
			},

			/**
			 * Fillters cell's value so correct entity is displayed
			 * @param {Object} cell cell
			 * @param {Integer} sheet sheet index within instance
			 * @param {Integer} row row index
			 * @param {Integer} col col index
			 * @returns {Object} cell
			 * @methodOf jS
			 * @name filterValue
			 */
			filterValue:function (cell, sheet, row, col) {
				cell = cell || {};

				if (cell.result != u) {
					cell.value = cell.result;
					jS.getTd(sheet, row, col).html(cell.html.length > 0 ? cell.html : s.encode(cell.value));
				} else if (cell.html.length > 0) {
					jS.getTd(sheet, row, col).html(cell.html);
				} else {
					jS.getTd(sheet, row, col).html(s.encode(cell.value));
				}
				return cell;
			},

			/**
			 * Object handler for formulaParser
			 * @name cellHandler
			 * @memberOf jS
			 * @namespace
			 */
			cellHandler:{

				/**
				 * Variable handler for formulaParser, arguments are the variable split by '.'.  Expose variables by using jQuery.sheet setting formulaVariables
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name variable
				 */
				variable:function () {
					if (arguments.length) {
						var name = arguments[0],
							attr = arguments[1];

						switch (name.toLowerCase()) {
							case 'true':
								return jFN.TRUE();
							case 'false':
								return jFN.FALSE();
						}

						if (jS.s.formulaVariables[name] && !attr) {
							return jS.s.formulaVariables[name];
						} else if (jS.s.formulaVariables[name] && attr) {
							return jS.s.formulaVariables[name][attr];
						} else {
							return '';
						}
					}
				},

				/**
				 * time to fraction of day 1 / 0-24
				 * @param {Time} time
				 * @param {Boolean} isAMPM
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name time
				 */
				time:function (time, isAMPM) {
					return times.fromString(time, isAMPM);
				},

				/**
				 * Concatenate a string
				 * @returns {String}
				 * @methodOf jS.cellHandler
				 * @name concatenate
				 */
				concatenate:function () {
					jS.spreadsheets[this.sheet][this.row][this.col].html = [];
					return jFN.CONCATENATE.apply(this, arguments).value;
				},

				/**
				 * Get cell value
				 * @param {String} id example "A1"
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name cellValue
				 */
				cellValue:function (id) { //Example: A1
					var loc = jSE.parseLocation(id);

					jS.cellHandler.createDependency.apply(this, [this.sheet, loc]);

					return jS.updateCellValue(this.sheet, loc.row, loc.col);
				},

				/**
				 * Creates a relationship between 2 cells, where the formula originates and the cell that is required to supply a value to
				 * @param {Integer} sheet
				 * @param {Object} loc {row, col}
				 */
				createDependency:function (sheet, loc) {
					if (!jS.spreadsheets[sheet]) return;
					if (!jS.spreadsheets[sheet][loc.row]) return;
					if (!jS.spreadsheets[sheet][loc.row][loc.col]) return;

					if (!jS.spreadsheets[this.sheet]) return;
					if (!jS.spreadsheets[this.sheet][this.row]) return;
					if (!jS.spreadsheets[this.sheet][this.row][this.col]) return;

					if (!jS.spreadsheets[sheet][loc.row][loc.col].dependencies) jS.spreadsheets[sheet][loc.row][loc.col].dependencies = {};
					//if (!jS.spreadsheets[this.sheet][this.row][this.col].dependencies) jS.spreadsheets[this.sheet][this.row][this.col].dependencies = {};


					jS.spreadsheets[sheet][loc.row][loc.col].dependencies[this.sheet + '_' + this.row + '_' + this.col] = jS.spreadsheets[this.sheet][this.row][this.col];
					//jS.spreadsheets[this.sheet][this.row][this.col].dependencies[sheet + '_' + loc.row + '_' + loc.col] = jS.spreadsheets[sheet][loc.row][loc.col];
				},

				/**
				 * Get cell values as an array
				 * @param {String} start example "A1"
				 * @param {String} end example "B1"
				 * @returns {Array}
				 * @methodOf jS.cellHandler
				 * @name cellRangeValue
				 */
				cellRangeValue:function (start, end) {//Example: A1:B1
					start = jSE.parseLocation(start);
					end = jSE.parseLocation(end);
					var result = [];

					for (var i = start.row; i <= end.row; i++) {
						for (var j = start.col; j <= end.col; j++) {
							jS.cellHandler.createDependency.apply(this, [this.sheet, {row:i, col:j}]);

							result.push(jS.updateCellValue(this.sheet, i, j));
						}
					}
					return [result];
				},

				/**
				 * Get cell value
				 * @param {String} id example "$A$1"
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name fixedCellValue
				 */
				fixedCellValue:function (id) {
					id = id.replace(/\$/g, '');
					return jS.cellHandler.cellValue.apply(this, [id]);
				},

				/**
				 * Get cell values as an array
				 * @param {String} start example "$A$1"
				 * @param {String} end example "$B$1"
				 * @returns {Array}
				 * @methodOf jS.cellHandler
				 * @name fixedCellRangeValue
				 */
				fixedCellRangeValue:function (start, end) {
					start = start.replace(/\$/g, '');
					end = end.replace(/\$/g, '');
					return jS.cellHandler.cellRangeValue.apply(this, [start, end]);
				},

				/**
				 * Get cell value from a different sheet within an instance
				 * @param {String} sheet example "SHEET1"
				 * @param {String} id example "A1"
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name remoteCellValue
				 */
				remoteCellValue:function (sheet, id) {//Example: SHEET1:A1
					var loc = jSE.parseLocation(id);
					sheet = jSE.parseSheetLocation(sheet);

					jS.cellHandler.createDependency.apply(this, [sheet, loc]);

					return jS.updateCellValue(sheet, loc.row, loc.col);
				},

				/**
				 * Get cell values as an array from a different sheet within an instance
				 * @param {String} sheet example "SHEET1"
				 * @param {String} start example "A1"
				 * @param {String} end example "B1"
				 * @returns {Array}
				 * @methodOf jS.cellHandler
				 * @name remoteCellRangeValue
				 */
				remoteCellRangeValue:function (sheet, start, end) {//Example: SHEET1:A1:B2
					sheet = jSE.parseSheetLocation(sheet);
					start = jSE.parseLocation(start);
					end = jSE.parseLocation(end);

					var result = [];

					for (var i = start.row; i <= end.row; i++) {
						for (var j = start.col; j <= end.col; j++) {
							result.push(jS.updateCellValue(sheet, i, j));
						}
					}

					return [result];
				},

				/**
				 * Calls a function either from jQuery.sheet.engine or defined in jQuery sheet setting formulaFunctions.  When calling a function the cell being called from is "this".
				 * @param {String} fn function name (Will be converted to upper case)
				 * @param {Array} args arguments needing to be sent to function
				 * @param {Object} cell cell
				 * @returns {*}
				 * @methodOf jS.cellHandler
				 * @name callFunction
				 */
				callFunction:function (fn, args, cell) {
					fn = fn.toUpperCase();
					if (!args) {
						args = [''];
					} else if ($.isArray(args)) {
						args = args.reverse();
					} else {
						args = [args];
					}

					if ($.sheet.fn[fn]) {
						jS.spreadsheets[cell.sheet][cell.row][cell.col].fnCount++;
						var values = [],
							html = [];

						for (i in args) {
							if (args[i]) {
								if (args[i].value || args[i].html) {
									values.push(args[i].value);
									html.push(args[i].html);
								} else {
									values.push(args[i]);
									html.push(args[i]);
								}
							}
						}

						cell.html = html;
						var result = $.sheet.fn[fn].apply(cell, values);
						if (result != null) {
							if (result.html != u) {
								jS.spreadsheets[cell.sheet][cell.row][cell.col].html = result.html;
							}
							if (result.value != u) {
								return result.value;
							}
						}
						return result;
					} else {
						return s.error({error:"Function " + fn + " Not Found"});
					}
				}
			},

			/**
			 * Cell lookup handlers
			 * @name cellLookupHandlers
			 * @memberOf jS
			 * @namespace
			 */
			cellLookupHandlers:{

				/**
				 * @param {String} id example "$A$1"
				 * @returns {Array} [sheet, startCell, endCell]
				 * @methodOf jS.cellLookupHandlers
				 * @name fixedCellValue
				 */
				fixedCellValue:function (id) {
					return [jS.sheet, jSE.parseLocation(id), jSE.parseLocation(id)];
				},

				/**
				 * @param {String} sheet example "SHEET1"
				 * @param {String} start example "$A$1"
				 * @param {String} end example "$B$1"
				 * @returns {Array} [sheet, startCell, endCell]
				 * @methodOf jS.cellLookupHandlers
				 * @name fixedCellRangeValue
				 */
				fixedCellRangeValue:function (sheet, start, end) {
					return [jSE.parseSheetLocation(sheet), jSE.parseLocation(start), jSE.parseLocation(end)];
				},

				/**
				 * doesn't do anything right now
				 * @param id
				 * @methodOf jS.cellLookupHandlers
				 * @name cellValue
				 */
				cellValue:function (id) {

				},

				/**
				 * @param {String} sheet example "SHEET1"
				 * @param {String} start example "A1"
				 * @param {String} end example "B1"
				 * @returns {Array} [sheet, startCell, endCell]
				 * @methodOf jS.cellLookupHandlers
				 * @name cellRangeValue
				 */
				cellRangeValue:function (sheet, start, end) {
					return [jS.sheet, jSE.parseLocation(start), jSE.parseLocation(end)];
				},

				/**
				 * @param {String} sheet example "SHEET1"
				 * @param {String} id example "A1"
				 * @returns {Array} [sheet, startCell, endCell]
				 * @methodOf jS.cellLookupHandlers
				 * @name remoteCellValue
				 */
				remoteCellValue:function (sheet, id) {
					return [jS.sheet, jSE.parseLocation(id), jSE.parseLocation(id)];
				},

				/**
				 *
				 * @param {String} sheet example "SHEET1"
				 * @param {String} start example "A1"
				 * @param {String} end example "B1"
				 * @returns {Array} [sheet, startCell, endCell]
				 * @methodOf jS.cellLookupHandlers
				 * @name remoteCellRangeValue
				 */
				remoteCellRangeValue:function (sheet, start, end) {
					return [jSE.parseSheetLocation(sheet), jSE.parseLocation(start), jSE.parseLocation(end)];
				},

				/**
				 * @returns {*}
				 * @methodOf jS.cellLookupHandlers
				 * @name callFunction
				 */
				callFunction:function () {
					if (arguments[0] == "VLOOKUP" || arguments[0] == "HLOOKUP" && arguments[1]) {
						return arguments[1].reverse()[1];
					}
				}
			},

			/**
			 * Looks up cell using jS.cellLookupHandlers
			 * @returns {Array}
			 * @methodOf jS
			 * @name cellLookup
			 */
			cellLookup:function () {
				var formulaParser = (new jS.formulaParser);
				formulaParser.lexer.obj = this.obj;
				formulaParser.lexer.handler = $.extend(formulaParser.lexer.handler, jS.cellLookupHandlers);

				var args = formulaParser.parse(this.obj.formula),
					lookupTable = [];

				for (var row = args[1].row; row <= args[2].row; row++) {
					for (var col = args[1].col; col <= args[2].col; col++) {
						lookupTable.push({
							sheet:args[0],
							row:row,
							col:col
						});
					}
				}

				return lookupTable;
			},

			/**
			 *
			 * @param {String} msg
			 * @methodOf jS
			 * @name alertFormulaError
			 */
			alertFormulaError:function (msg) {
				alert(
					'cell:' + row + ' ;' + col + '\n' +
					'value: "' + cell.formula + '"\n' +
					'error: \n' + e
				);
			},

			/**
			 * Date of last calculation
			 * @memberOf jS
			 * @name calcLast
			 */
			calcLast:0,

			/**
			 * @memberOf jS
			 * @name calcDependenciesLast
			 */
			calcDependenciesLast:0,

			/**
			 * Where jS.spreadsheets are calculated, and returned to their td counterpart
			 * @param {Integer} tableI table index
			 * @methodOf jS
			 * @name calc
			 */
			calc:function (tableI) { /* harnesses formula engine's calculation function
			 tableI: int, the current table integer;
			 fuel: variable holder, used to prevent memory leaks, and for calculations;
			 */
				tableI = (tableI ? tableI : jS.i);
				if (jS.readOnly[tableI] || jS.isChanged() === false) return; //readonly is no calc at all

				jS.log('Calculation Started');
				jS.calcLast = new Date();
				jSE.calc(tableI, jS.spreadsheetsToArray()[tableI], jS.updateCellValue);
				jS.trigger('sheetCalculation', [
					{which:'speadsheet'}
				]);
				jS.setChanged(false);
				jS.log('Calculation Ended');
			},

			/**
			 * Calculates just the dependencies of a single cell, and their dependencies recursivley
			 * @param {Integer} sheet
			 * @param {Integer} row
			 * @param {Integer} cell
			 * @param {Boolean} skipUndoable
			 * @param {Date} last
			 */
			calcDependencies:function (sheet, row, cell, last, skipUndoable) {
				last = last || new Date();
				jS.calcDependenciesLast = last;

				if (!skipUndoable) {
					jS.cellUndoable.add(last, sheet, row, cell);
				}

				jS.trigger('sheetPreCalculation', [
					{which:'cell', sheet:sheet, row:row, cell:cell}
				]);
				jS.setDirty(true);
				jS.setChanged(true);
				jS.updateCellValue(sheet, row, cell);
				jS.updateCellDependencies(sheet, row, cell);
				jS.trigger('sheetCalculation', [
					{which:'cell', sheet:sheet, row:row, cell:cell}
				]);

				if (!skipUndoable) {
					jS.cellUndoable.add(last, sheet, row, cell, true);
				}
			},

			/**
			 * adds a spreadsheet table
			 * @param {Object} size, optional, size example "10x100" which means 10 columns by 100 rows
			 * @methodOf jS
			 * @name addSheet
			 */
			addSheet:function (size) {
				if (!size) {
					size = prompt(jS.msg.newSheet);
					size = size.toLowerCase().split('x');
					size = {cols:$.trim(size[0]) * 1, rows:$.trim(size[1]) * 1};
				}

				if (size) {
					jS.evt.cellEditAbandon();
					jS.setDirty(true);
					var newSheetControl = jS.controlFactory.sheetUI($.sheet.makeTable.fromSize(size), jS.sheetCount + 1);

					jS.setActiveSheet(jS.sheetCount);

					jS.sheetSyncSize();

					jS.obj.pane().trigger('resizeScroll');

					jS.trigger('sheetAdd', [jS.i]);
				}
			},

			/**
			 * deletes a spreadsheet table
			 * @param {Integer} i optional spraedsheet index within instance
			 * @methodOf jS
			 * @name deleteSheet
			 */
			deleteSheet:function (i) { /* removes the currently selected sheet */
				var oldI = i || jS.i;

				jS.obj.barHelper().remove();

				jS.obj.pane().remove();
				jS.obj.tabContainer().children().eq(jS.i).remove();
				jS.spreadsheets[oldI] = null;
				jS.i = 0;
				jS.sheetCount--;

				jS.setActiveSheet(jS.i);
				jS.setDirty(true);
				jS.setChanged(true);

				jS.trigger('sheetDelete', [oldI]);
			},

			/**
			 * removes the currently selected row
			 * TODO: Needs refactor to use jS.spreadsheets
			 * @param {Boolean} skipCalc
			 * @methodOf jS
			 * @name deleteRow
			 */
			deleteRow:function (skipCalc) {
				//remove tr's first
				jS.getTd(jS.i, jS.rowLast, 1).parent().remove();

				//now remove bar
				jS.controls.bar.y.td[jS.i].splice(jS.rowLast, 1);

				//now remove cells
				jS.spreadsheets[jS.i].splice(jS.rowLast, 1);

				jS.refreshRowLabels(jS.rowLast);

				jS.setChanged(true);

				jS.offsetFormulas({
					row:jS.rowLast,
					col:0
				}, {
					row:-1,
					col:0
				});

				jS.setDirty(true);

				jS.evt.cellEditAbandon();

				jS.obj.pane().trigger('resizeScroll');

				jS.trigger('sheetDeleteRow', jS.rowLast);
			},

			/**
			 * removes the currently selected column
			 * TODO: Needs refactor to jS.spreadsheets
			 * @param {Boolean} skipCalc
			 * @methodOf jS
			 * @name deleteColumn
			 */
			deleteColumn:function (skipCalc) {
				if (jS.colLast < 1) return;
				jS.obj.barHelper().remove();
				var sheet = jS.obj.sheet(),
					size = jS.sheetSize(sheet);

				//remove tds first
				for (var i = 1; i <= size.rows; i++) {
					jS.getTd(jS.i, i, jS.colLast).remove();
				}

				//now remove bar
				jS.obj.barTop(jS.colLast).remove();

				//remove column
				jS.controls.bar.x.td[jS.i].splice(jS.colLast, 1);

				//remove cells
				for (var row in jS.spreadsheets[jS.i]) {
					jS.spreadsheets[jS.i][row].splice(jS.colLast, 1);
				}

				//now remove col
				$(jS.col(sheet, jS.colLast)).remove();

				//refresh labels
				jS.refreshColumnLabels(jS.colLast);

				jS.setChanged(true);

				jS.offsetFormulas({
					row:0,
					col:jS.colLast
				}, {
					row:0,
					col:-1
				});

				jS.setDirty(true);

				jS.evt.cellEditAbandon();

				jS.obj.pane().trigger('resizeScroll');

				jS.trigger('sheetDeleteColumn', jS.colLast);
			},

			/**
			 * manages a tabs inner value
			 * @param {Bool} get makes return the current value of the tab
			 * @returns {jQuery|HTMLElement}
			 * @methodOf jS
			 * @name sheetTab
			 */
			sheetTab:function (get) {
				var sheetTab = '';
				if (get) {
					sheetTab = jS.obj.sheet().attr('title');
					sheetTab = (sheetTab ? sheetTab : jS.msg.sheetTitleDefault.replace(/[{]index[}]/gi, jS.i + 1));
				} else if (jS.isSheetEditable() && s.editableNames) { //ensure that the sheet is editable, then let them change the sheet's name
					var newTitle = prompt(jS.msg.newSheetTitle, jS.sheetTab(true));
					if (!newTitle) { //The user didn't set the new tab name
						sheetTab = jS.obj.sheet().attr('title');
						newTitle = (sheetTab ? sheetTab : jS.msg.sheetTitleDefault.replace(/[{]index[}]/gi, jS.i + 1));
					} else {
						jS.setDirty(true);
						jS.obj.sheet().attr('title', newTitle);
						jS.obj.tab().html(newTitle);

						sheetTab = newTitle;
					}
				}
				return $('<div />').text(sheetTab).html();
			},

			/**
			 * prints a value in a new window
			 * @param {String} o anything
			 * @methodOf jS
			 * @name print
			 */
			print:function (o) {
				var w = window.open();
				w.document.write("<html><body><xmp>" + o + "\n</xmp></body></html>");
				w.document.close();
			},

			/**
			 * prints the source of a sheet for a user to see
			 * @param {Boolean} pretty makes html a bit easier for the user to see
			 * @returns {Boolean}
			 * @methofOf jS
			 * @name viewSource
			 */
			viewSource:function (pretty) {
				var sheetClone = jS.tables();
				sheetClone = jS.sheetBarsRemove(sheetClone);

				var s = "";
				if (pretty) {
					$(sheetClone).each(function () {
						s += jS.HTMLtoPrettySource(this);
					});
				} else {
					s += $('<div />').html(sheetClone).html();
				}

				jS.print(s);

				return false;
			},

			/**
			 * prints html to 1 line
			 * @param {HTMLElement} node
			 * @returns {String}
			 * @constructor
			 * @methodOf jS
			 * @name HTMLtoCompactSource
			 */
			HTMLtoCompactSource:function (node) {
				var result = "";
				if (node.nodeType == 1) {
					// ELEMENT_NODE
					result += "<" + node.tagName;
					hasClass = false;

					var n = node.attributes.length;
					for (var i = 0, hasClass = false; i < n; i++) {
						var key = node.attributes[i].name,
							val = node.getAttribute(key);

						if (val) {
							if (key == "contentEditable" && val == "inherit") {
								continue;
								// IE hack.
							}
							if (key == "class") {
								hasClass = true;
							}

							if (typeof(val) == "string") {
								result += " " + key + '="' + val.replace(/"/g, "'") + '"';
							} else if (key == "style" && val.cssText) {
								result += ' style="' + val.cssText + '"';
							}
						}
					}

					if (node.tagName == "COL") {
						// IE hack, which doesn't like <COL..></COL>.
						result += '/>';
					} else {
						result += ">";
						var childResult = "";
						$(node.childNodes).each(function () {
							childResult += jS.HTMLtoCompactSource(this);
						});
						result += childResult;
						result += "</" + node.tagName + ">";
					}

				} else if (node.nodeType == 3) {
					// TEXT_NODE
					result += node.data.replace(/^\s*(.*)\s*$/g, "$1");
				}
				return result;
			},

			/**
			 *  prints html to many lines, formatted for easy viewing
			 * @param {HTMLElement} node
			 * @param {String} prefix
			 * @returns {String}
			 * @constructor
			 * @methodOf jS
			 * @name HTMLtoPrettySource
			 */
			HTMLtoPrettySource:function (node, prefix) {
				if (!prefix) {
					prefix = "";
				}
				var result = "";
				if (node.nodeType == 1) {
					// ELEMENT_NODE
					result += "\n" + prefix + "<" + node.tagName;
					var n = node.attributes.length;
					for (var i = 0; i < n; i++) {
						var key = node.attributes[i].name,
							val = node.getAttribute(key);

						if (val) {
							if (key == "contentEditable" && val == "inherit") {
								continue; // IE hack.
							}
							if (typeof(val) == "string") {
								result += " " + key + '="' + val.replace(/"/g, "'") + '"';
							} else if (key == "style" && val.cssText) {
								result += ' style="' + val.cssText + '"';
							}
						}
					}
					if (node.childNodes.length <= 0) {
						result += "/>";
					} else {
						result += ">";
						var childResult = "",
							n = node.childNodes.length;

						for (var i = 0; i < n; i++) {
							childResult += jS.HTMLtoPrettySource(node.childNodes[i], prefix + "  ");
						}
						result += childResult;
						if (childResult.indexOf('\n') >= 0) {
							result += "\n" + prefix;
						}
						result += "</" + node.tagName + ">";
					}
				} else if (node.nodeType == 3) {
					// TEXT_NODE
					result += node.data.replace(/^\s*(.*)\s*$/g, "$1");
				}
				return result;
			},

			/**
			 * scrolls the sheet to the selected cell
			 * @param {jQuery|HTMLElement} td
			 * @param {Boolean} onlyCheckIfVisible causes return of true || false if the td is visible
			 * @methodOf jS
			 * @name followMe
			 */
			followMe:function (td, onlyCheckIfVisible) {
				td = td || jS.obj.cellActive();
				if (!td.length) return;

				var pane = jS.obj.pane(),
					paneHeight = pane.height(),
					paneWidth = pane.width(),
					panePos = pane.offset(),
					visibleFold = {
						top:panePos.top,
						bottom:panePos.top + paneHeight,
						left:panePos.left,
						right:panePos.left + paneWidth
					},
					move = true,
					i = 0,
					x = 0,
					y = 0,
					max = 5,
					tdPos = td.offset(),
					tdWidth = td.width(),
					tdHeight = td.height(),
					tdLocation = {
						top:tdPos.top,
						bottom:tdPos.top + tdHeight,
						left:tdPos.left,
						right:tdPos.left + tdWidth
					},
					tdParent = td.parent(),
					tdInBottomRowOfSameCol = $(jS.rowTds()[jS.getTdLocation(td).col]),
					directions,
					tempHeight = 0,
					tempWidth = 0,
					checkVisible = {
						up:true,
						down:true,
						left:true,
						right:true
					},
					scrolledArea = jS.scrolledTo();

				if (tdHeight > paneHeight || tdWidth > paneWidth) return;

				jS.setBusy(true);

				while (move == true && i < max) {
					var tempTd = jS.getTd(jS.i, scrolledArea.row.end + y, scrolledArea.col.end + x),
						xHidden = tdInBottomRowOfSameCol.is(':hidden'),
						yHidden = tdParent.is(':hidden');

					move = false;

					directions = {
						up:yHidden,
						down:tdLocation.bottom - tempHeight > visibleFold.bottom,
						left:xHidden,
						right:tdLocation.right - tempWidth > visibleFold.right
					};

					//$.sheet.debugPositionBox(tdLocation.right -tempWidth, tdLocation.bottom - tempHeight, null, 'green', directions);

					if (directions.left) {
						if (onlyCheckIfVisible) {
							checkVisible.left = false;
						} else {
							x--;
							move = true;
							jS.evt.scroll.scrollTo({axis:'x', value:scrolledArea.col.end + x});
						}
					} else if (directions.right) {
						if (onlyCheckIfVisible) {
							checkVisible.right = false;
						} else {
							x++;
							move = true;
						}
					}

					if (directions.up) {
						if (onlyCheckIfVisible) {
							checkVisible.up = false;
						} else {
							y--;
							move = true;
							jS.evt.scroll.scrollTo({axis:'y', value:scrolledArea.row.end + y});
						}
					} else if (directions.down) {
						if (onlyCheckIfVisible) {
							checkVisible.down = false;
						} else {
							y++;
							move = true;
						}
					}

					if (onlyCheckIfVisible) {
						jS.setBusy(false);
						return checkVisible;
					}

					tempHeight += tempTd.height();
					tempWidth += tempTd.width();

					i++;
				}

				if (x > 0) { //right
					jS.evt.scroll.scrollTo({axis:'x', value:(scrolledArea.col.end + 1) + x});
					jS.evt.scroll.stop();
				}

				if (y > 0) { //down
					jS.evt.scroll.scrollTo({axis:'y', value:(scrolledArea.row.end + 1) + y});
					jS.evt.scroll.stop();
				}

				setTimeout(function () {
					jS.setBusy(false);
				}, 100);

				jS.autoFillerGoToTd(td, tdHeight, tdWidth);
			},

			/**
			 * moves autoFiller to a selected cell
			 * @param {jQuery|HTMLElement} td
			 * @param {Integer} tdHeight optional, height of a td object
			 * @param {Integer} tdWidth optional, width of a td object
			 * @methodOf jS
			 * @name autoFillerGoToTd
			 */
			autoFillerGoToTd:function (td, tdHeight, tdWidth) {
				if (!s.autoFiller) return;

				td = td || jS.obj.cellActive();
				tdHeight = tdHeight || td.height();
				tdWidth = tdWidth || td.width();

				if (jS.isTd(td[0]) && td.is(':visible')) { //ensure that it is a usable cell
					var tdPos = td.position();
					jS.obj.autoFiller()
						.show()
						.css('top', ((tdPos.top + (tdHeight || td.height()) - 3) + 'px'))
						.css('left', ((tdPos.left + (tdWidth || td.width()) - 3) + 'px'));
				} else {
					jS.autoFillerHide();
				}
			},

			/**
			 * hides the auto filler
			 * @methodOf jS
			 * @name autoFillerHide
			 */
			autoFillerHide:function () {
				if (!s.autoFiller) return;

				jS.obj.autoFiller().hide();
			},

			/**
			 * sets active a spreadsheet inside of a sheet instance
			 * @param {Integer} i a sheet integer desired to show
			 * @methodOf jS
			 * @name setActiveSheet
			 */
			setActiveSheet:function (i) {
				i = i || 0;

				if (jS.cellLast.row > 0 || jS.cellLast.col > 0) {
					jS.evt.cellEditDone();
					jS.obj.formula().val('');
				}

				jS.obj.enclosures()
					.hide();

				jS.i = i;

				jS.obj.enclosure()
					.show();

				jS.themeRoller.tab.setActive();

				jS.readOnly[i] = jS.obj.sheet().hasClass('readonly');

				jS.obj.pane().trigger('resizeScroll');
			},

			/**
			 * opens a spreadsheet into the active sheet instance
			 * @param tables
			 * @returns {Boolean} if set to true, foces bars on left and top not be reloaded
			 * @methodOf jS
			 * @name openSheet
			 */
			openSheet:function (tables) {
				if (jS.isDirty ? confirm(jS.msg.openSheet) : true) {
					jS.setBusy(true);
					var header = jS.controlFactory.header(),
						ui = jS.controlFactory.ui(),
						tabContainer = jS.controlFactory.tabContainer();

					s.parent
						.append(header)
						.append(ui)
						.append(tabContainer);

					tables.each(function (i) {
						jS.controlFactory.sheetUI($(this), i);
						jS.calc(i);
						jS.trigger('sheetOpened', [i]);
					});

					jS.sheetSyncSize();

					jS.setActiveSheet(0);

					jS.setDirty(false);
					jS.setBusy(false);

					jS.trigger('sheetAllOpened');
					return true;
				} else {
					return false;
				}
			},

			/**
			 * creates a new sheet from size from prompt
			 * @methodOf jS
			 * @name newSheet
			 */
			newSheet:function () {
				var size = prompt(jS.msg.newSheet);
				if (size) {
					jS.openSheet($.sheet.makeTable.fromSize(size));
				}
			},

			/**
			 * creates a new row and then applies an array's values to each of it's new values, not currently working
			 * TODO: Needs refactored to use jS.spreadsheets
			 * @param {Array} rowArray values to import
			 * @methodOf jS
			 * @name importRow
			 */
			importRow:function (rowArray) {
				jS.controlFactory.addRow();

				var error = "";
				jS.obj.sheet().find('tr:last td').each(function (i) {
					$(this).removeData('formula');
					try {
						//To test this, we need to first make sure it's a string, so converting is done by adding an empty character.
						if ((rowArray[i] + '').charAt(0) == "=") {
							$(this).data('formula', rowArray[i]);
						} else {
							$(this).html(rowArray[i]);
						}
					} catch (e) {
						//We want to make sure that is something bad happens, we let the user know
						error += e + ';\n';
					}
				});

				if (error) {//Show them the errors
					alert(error);
				}

				jS.calc();
			},

			/**
			 * creates a new column and then applies an array's values to each of it's new values
			 * TODO: needs refactored to use jS.spreadsheets
			 * @param {Array} columnArray values to import
			 * @methodOf jS
			 * @name importColumn
			 */
			importColumn:function (columnArray) {
				jS.controlFactory.addColumn();

				var error = "";
				jS.obj.sheet().find('tr').each(function (i) {
					var o = $(this).find('td:last');
					try {
						//To test this, we need to first make sure it's a string, so converting is done by adding an empty character.
						if ((columnArray[i] + '').charAt(0) == "=") {
							o.data('formula', columnArray[i]);
						} else {
							o.html(columnArray[i]);
						}
					} catch (e) {
						//We want to make sure that is something bad happens, we let the user know
						error += e + ';\n';
					}
				});

				if (error) {//Show them the errors
					alert(error);
				}

				//Let's recalculate the sheet just in case
				jS.calc();
			},


			/**
			 * Sync's the called parent's controls so that they fit correctly within the parent
			 * @function sheetSyncSize
			 * @methodOf jS
			 * @name sheetSyncSize
			 */
			sheetSyncSize:function () {
				var h = s.height;
				if (!h) {
					h = 400; //Height really needs to be set by the parent
				} else if (h < 200) {
					h = 200;
				}
				s.parent
					.height(h)
					.width(s.width);

				var w = s.width;
				h -= jS.obj.header().outerHeight();
				h -= jS.obj.tabContainer().outerHeight() + jS.s.boxModelCorrection;

				jS.obj.panes()
					.height(h - window.scrollBarSize.height - s.boxModelCorrection)
					.width(w - window.scrollBarSize.width);


				jS.obj.enclosures()
					.height(h)
					.width(w);

				jS.obj.scrolls()
					.height(h)
					.width(w);


				jS.obj.ui()
					.height(h)
					.width(w);
			},

			/**
			 * changes a cell's style and makes it undoable/redoable
			 * @param style
			 * @param value
			 */
			cellChangeStyle:function (style, value) {
				jS.setDirty(this);
				jS.cellUndoable.add(jS.obj.cellHighlighted()); //save state, make it undoable
				jS.obj.cellHighlighted().css(style, value);
				jS.cellUndoable.add(jS.obj.cellHighlighted(), true); //save state, make it redoable

			},

			/**
			 * Finds a cell in a sheet from a value
			 * @param {String} v value to look for within a cell
			 * @methodOf jS
			 * @name cellFind
			 */
			cellFind:function (v) {
				if (!v) {
					v = prompt(jS.msg.cellFind);
				}
				var trs = jS.obj.sheet()
					.children('tbody')
					.children('tr');

				if (v) {//We just do a simple uppercase/lowercase search.
					var o = trs.children('td:contains("' + v + '")');

					if (o.length < 1) {
						o = trs.children('td:contains("' + v.toLowerCase() + '")');
					}

					if (o.length < 1) {
						o = trs.children('td:contains("' + v.toUpperCase() + '")');
					}

					o = o.eq(0);
					if (o.length > 0) {
						jS.cellEdit(o);
					} else {
						alert(jS.msg.cellNoFind);
					}
				}
			},

			/**
			 * Sets active bar
			 * @param {String} type "col" || "row" || "all"
			 * @param {Integer} start start highlighting from
			 * @param {Integer} end end highlighting to
			 * @methodOf jS
			 * @name cellSetActiveBar
			 */
			cellSetActiveBar:function (type, start, end) {
				var size = jS.sheetSize(),
					first = Math.min(start, end),
					last = Math.max(start, end),
					rows = {},
					cols = {},
					visibleCol = {},
					visibleRow = {},
					setActive = function () {
						switch (s.cellSelectModel) {
							case 'oo': //follow cursor behavior
								jS.cellEdit(jS.getTd(jS.i, visibleRow.end, visibleCol.end));
								break;
							default: //stay at initial cell
								jS.cellEdit(jS.getTd(jS.i, visibleRow.start, visibleCol.start));
								break;
						}
					},
					td = $([]),
					scrolledArea  = jS.scrolledTo();

				switch (type) {
					case 'top':
						rows.start = 1;
						rows.end = size.rows;
						visibleRow.start = visibleRow.end = scrolledArea.row.end;

						cols.start = first;
						cols.end = last;
						visibleCol.start = start;
						visibleCol.end = end;

						break;
					case 'left':
						rows.start = first;
						rows.end = last;
						visibleRow.start = start;
						visibleRow.end = end;

						cols.start = 1;
						cols.end = size.cols;
						visibleCol.start = visibleCol.end = scrolledArea.col.end;

						break;
					case 'corner': //all
						cols.start = 1;
						cols.end = size.cols;
						rows.start = 1;
						rows.end = size.rows;

						break;
				}

				for (var row = rows.start; row <= rows.end; row++) { //rows
					for (var col = cols.start; col <= cols.end; col++) { //cols
						td = td.add(jS.getTd(jS.i, row, col));
					}
				}

				setActive();
				jS.themeRoller.cell.clearHighlighted();
				jS.themeRoller.cell.setHighlighted(td);

				jS.highlightedLast.td = td;

				jS.highlightedLast.rowStart = rows.start;
				jS.highlightedLast.rowEnd = rows.end;

				jS.highlightedLast.colStart = cols.start;
				jS.highlightedLast.colEnd = cols.end;
			},

			/**
			 * gets a range of selected cells, then returns it
			 * @param {Object} e jQuery event, optional, when in use, is during mouse down
			 * @param {String} v Value to preserve and return
			 * @param newFn
			 * @param notSetFormula
			 * @returns {String}
			 * @methodOf jS
			 * @name getTdRange
			 */
			getTdRange:function (e, v, newFn, notSetFormula) {
				jS.cellLast.isEdit = true;

				var range = function (loc) {
					if (loc.first.col > loc.last.col ||
						loc.first.row > loc.last.row
						) {
						return {
							first:jSE.parseCellName(loc.last.col, loc.last.row),
							last:jSE.parseCellName(loc.first.col, loc.first.row)
						};
					} else {
						return {
							first:jSE.parseCellName(loc.first.col, loc.first.row),
							last:jSE.parseCellName(loc.last.col, loc.last.row)
						};
					}
				};
				var label = function (loc) {
					var rangeLabel = range(loc),
						v2 = v + '';
					v2 = (v2.match(/=/) ? v2 : '=' + v2); //make sure we can use this value as a formula

					if (newFn || v2.charAt(v2.length - 1) != '(') { //if a function is being sent, make sure it can be called by wrapping it in ()
						v2 = v2 + (newFn ? newFn : '') + '(';
					}

					var formula,
						lastChar = '';
					if (rangeLabel.first != rangeLabel.last) {
						formula = rangeLabel.first + ':' + rangeLabel.last;
					} else {
						formula = rangeLabel.first;
					}

					if (v2.charAt(v2.length - 1) == '(') {
						lastChar = ')';
					}

					return v2 + formula + lastChar;
				};
				var newVal = '';

				if (e) { //if from an event, we use mousemove method
					var loc = {
						first:jS.getTdLocation([e.target])
					};

					var sheet = jS.obj.sheet().mousemove(function (e) {
						loc.last = jS.getTdLocation([e.target]);

						newVal = label(loc);

						if (!notSetFormula) {
							jS.obj.formula().val(newVal);
							jS.obj.inPlaceEdit().val(newVal);
						}
					});

					$document.one('mouseup', function () {
						sheet.unbind('mousemove');
						return newVal;
					});
				} else {
					var cells = jS.obj.cellHighlighted().not(jS.obj.cellActive());

					if (cells.length) {
						var loc = { //tr/td column and row index
							first:jS.getTdLocation(cells.first()),
							last:jS.getTdLocation(cells.last())
						};

						newVal = label(loc);

						if (!notSetFormula) {
							jS.obj.formula().val(newVal);
							jS.obj.inPlaceEdit().val(newVal);
						}

						return newVal;
					} else {
						return '';
					}
				}
			},

			/**
			 * Gets the td element within a spreadsheet instance
			 * @param {Integer} table table index
			 * @param {Integer} row row index
			 * @param {Integer} col column index
			 * @returns {Element}
			 * @methodOf
			 * @name getTd
			 */
			getTd:function (table, row, col) {
				if (
					!jS.spreadsheets[table] || !jS.spreadsheets[table][row] || !jS.spreadsheets[table][row][col] || !jS.spreadsheets[table][row][col].td
					) {
					return $('<td />');
				}

				return jS.spreadsheets[table][row][col].td;
			},

			/**
			 * Gets the td row and column index as an object {row, col}
			 * @param td
			 * @returns {Object}
			 * @methodOf jS
			 * @name getTdLocation
			 */
			getTdLocation:function (td) {
				var result = {col:0, row:0};
				td = td || '';
				if (!td && !td[0]) return result;

				td = td[0] || td;

				if (td.cellIndex == u || td.parentNode == u || td.parentNode.rowIndex == u) return result;

				return {
					col:parseInt(td.cellIndex),
					row:parseInt(td.parentNode.rowIndex)
				};
			},

			/**
			 * Get a td from a pixel location
			 * @param {Integer} left pixels from left
			 * @param {Integer} top pixels from top
			 * @param {Boolean} isBar
			 * @returns {Element|Boolean} Boolean if not found
			 * @methodOf jS
			 * @name getTdFromXY
			 */
			getTdFromXY:function (left, top, isBar) {
				var pane = jS.obj.pane(),
					paneOffset = pane.offset();

				top += paneOffset.top;
				left += paneOffset.left;

				//here we double check that the coordinates are inside that of the pane, if so then we can continue
				if (
					(
						top >= paneOffset.top &&
							top <= paneOffset.top + pane.height()
						)
						&&
						(
							left >= paneOffset.left &&
								left <= paneOffset.left + pane.width()
							)
					) {
					var td = $.nearest({x:left, y:top}, jS.obj.sheet().children('tbody').children('tr').children('td'));

					//I use this snippet to help me know where the point was positioned
					/*var o = $('<div class="ui-widget-content" style="position: absolute;">TESTING TESTING</div>')
					 .css('top', top + 'px')
					 .css('left', left + 'px')
					 .appendTo('body');*/

					if (jS.isTd(td)) {
						return td;
					}

					if (isBar && jS.isBar(td)) {
						return td;
					}

					return false;
				}
				return false;
			},

			/**
			 * Get the bar index from an Element
			 * @memberOf jS
			 * @namespace
			 * @name getBarIndex
			 */
			getBarIndex:{

				/**
				 * get index from bar left element
				 * TODO: Needs to use object's index to be faster
				 * @param o
				 * @returns {Integer}
				 * @methodOf jS.getBarIndex
				 * @name left
				 */
				left:function (o) {
					o = o || {};
					if (!o.parentNode || isNaN(o.parentNode.rowIndex)) {
						return -1;
					} else {
						return o.parentNode.rowIndex;
					}
				},

				/**
				 * get index from bar top element
				 * TODO: Needs to use object's index to be faster
				 * @param o
				 * @returns {Integer}
				 * @methodOf hS.getBarIndex
				 * @name top
				 */
				top:function (o) {
					o = o || {};
					if (isNaN(o.cellIndex)) {
						return -1;
					} else {
						return o.cellIndex;
					}
				},
				corner:function () {
					return 0;
				}
			},

			/**
			 * Time manager for measuring execution speed
			 * @namespace
			 * @name time
			 * @memberOf jS
			 */
			time:{
				now:new Date(),
				last:new Date(),
				diff:function () {
					return Math.abs(Math.ceil(this.last.getTime() - this.now.getTime()) / 1000).toFixed(5);
				},
				set:function () {
					this.last = this.now;
					this.now = new Date();
				},
				get:function () {
					return this.now.getHours() + ':' + this.now.getMinutes() + ':' + this.now.getSeconds();
				}
			},

			/**
			 * The log prints: {Current Time}, {Seconds from last log};{msg}
			 * @param msg
			 * @memberOf jS
			 * @name log
			 */
			log:function (msg) {  //
				jS.time.set();
				console.log(jS.time.get() + ', ' + jS.time.diff() + '; ' + msg);
			},

			/**
			 * Changed tracker per sheet
			 * @memberOf jS
			 * @name changed
			 */
			changed:[],

			/**
			 * Changed = needs to be calculated
			 * @methodOf jS
			 * @name isChanged
			 */
			isChanged:function () {
				return jS.changed[jS.i];
			},

			/**
			 * Sets changed
			 * @param {Boolean} changed changed state
			 * @name setChanged
			 * @methodOf jS
			 */
			setChanged:function (changed) {
				jS.changed[jS.i] = changed;
			},

			/**
			 * Dirty = changed needs saved
			 * @memberOf jS
			 */
			isDirty:false,

			/**
			 * Dirty manager
			 * @param dirty
			 * @methodOf jS
			 * @name setDirty
			 */
			setDirty:function (dirty) {
				jS.dirty = dirty;
			},

			/**
			 * @param v
			 * @methodOf jS
			 * @name appendToFormula
			 */
			appendToFormula:function (v) {
				var formula = jS.obj.formula(),
					fV = formula.val();

				if (fV.charAt(0) != '=') {
					fV = '=' + fV;
				}

				formula.val(fV + v);
			},

			/**
			 * Undoable manager
			 * there should always be 2 cellUndoable.add()'s every time used, one to save the current state, the second to save the new
			 * @memberOf jS
			 * @name cellUndoable
			 * @namespace
			 */
			cellUndoable:{
				/**
				 * undo stack
				 * @param undo
				 * @memberOf jS.cellUndoable
				 * @name stacks
				 */
				stacks:[],

				/**
				 * @param {Boolean} undo
				 * @methodOf jS.cellUndoable
				 * @name undoOrRedo
				 */
				undoOrRedo:function (undo) {
					if (!this.stacks[jS.i]) return;

					//hide the autoFiller, it can get confused
					jS.autoFillerHide();

					var stack = this.stack(), cells;

					if (undo) {
						stack.moveBackward();
					} else {
						stack.moveForward();
					}

					cells = stack.getCells();

					for (var i in cells) {
						var td = cells[i].td,
							loc = jS.getTdLocation(td);

						jS.spreadsheets[jS.i][loc.row][loc.col] = cells[i];

						td
							.data('formula', cells[i].formula)
							.attr('style', cells[i].style)
							.addClass(cells[i].cl);

						jS.cellLast.td = $([]);

						jS.calcDependencies(jS.i, loc.row, loc.col, null, true);
					}
				},

				/**
				 * gets the current element
				 * @returns {jQuery|HTMLElement}
				 * @name get
				 * @methodOf jS.cellUndoable
				 */
				stack:function () {
					if (!this.stacks[jS.i]) this.stacks[jS.i] = {
						i: 0,
						max: 20,
						lasts: [],
						lastsCells: [],
						getCells: function(last) {
							var index = (last ? $.inArray(last, this.lasts) : this.i);
							if (index < 0) {
								this.i = this.lasts.length;
								this.lasts.push(last);
								index = this.lasts.length - 1
								this.lastsCells[index] = [];
							}
							return this.lastsCells[index];
						},
						cleanAhead: function() {
							this.lasts.splice(this.i + 1, this.lasts.length - this.i);
							this.lastsCells.splice(this.i + 1, this.lasts.length - this.i);
						},
						cleanBehind: function() {
							while (this.lasts.length > this.max) {
								this.lasts.shift();
								this.lastsCells.shift();
							}
						},
						moveForward: function() {
							this.i += 1;
							this.i = Math.min(this.i, this.lasts.length - 1);
						},
						moveBackward: function() {
							this.i -= 1;
							this.i = Math.max(this.i, 0);
						}
					};

					return this.stacks[jS.i];
				},

				/**
				 * adds elements to the undoable stack
				 * @param {Date} last
				 * @param {Integer} sheet
				 * @param {Integer} row
				 * @param {Integer} col
				 * @param {Boolean} after
				 * @name add
				 * @methodOf jS.cellUndoable
				 */
				add:function (last, sheet, row, col, after) {
					var stack = this.stack(),
						cells = stack.getCells(last.valueOf() + (after ? 1 : 0));

					stack.cleanAhead();

					if (row > 0 & col > 0) {
						var clone = {},
							cell = jS.spreadsheets[sheet][row][col];

						for (var attr in cell) {
							clone[attr] = cell[attr];
						}
						clone.style = cell.td.attr('style');
						clone.cl = (cell.td.attr('class') || '')
							.replace(jS.cl.uiCellActive , '')
							.replace(jS.cl.uiCellHighlighted, '');
						clone.sheet = sheet;
					}

					cells.push(clone);

					stack.cleanBehind();
				}
			},

			/**
			 * get cols associated with a sheet/table within an instance
			 * @param {jQuery|HTMLElement} o table
			 * @returns {Element}
			 * @name cols
			 * @methodOf jS
			 */
			cols:function (o) {
				o = o || jS.obj.sheet();

				//table / colgroup / col
				if (!o[0]) return [];
				if (!o[0].children) return [];
				if (!o[0].children[0]) return [];
				if (!o[0].children[0].children) return [];

				return o[0].children[0].children
			},

			tables:function (o) {
				o = o || jS.obj.sheets();
				o = o.clone();
				o.find('.' + jS.cl.barTopParent).remove();
				o.find('.' + jS.cl.barLeft).remove();
				o.children('colgroup').children('col:first').remove();
				o = jS.sheetDecorateRemove(false, o)
				return o;
			},

			/**
			 * get col associated with a sheet/table within an instance
			 * @param {jQuery|HTMLElement} o table
			 * @param {Integer} i, Index of column
			 * @returns {Element}
			 * @methodOf jS
			 * @name col
			 */
			col:function (o, i) {
				o = o || jS.obj.sheet();

				var cols = jS.cols(o);

				if (i === u) {
					i = cols.length - 1;
				}

				return cols[i];
			},

			/**
			 * get cells of a table row
			 * @param {jQuery|HTMLElement} o table
			 * @param {Index} row Index of row
			 * @returns {Element}
			 * @methodOf jS
			 * @name rowTds
			 */
			rowTds:function (o, row) {
				o = o || jS.obj.sheet();

				var rows = jS.rows(o);

				if (row == u) {
					row = rows.length - 1;
				}


				if (!rows[row]) return {}; //tr
				if (!rows[row].children) return {}; //td

				return rows[row].children;
			},

			/**
			 * Get rows of a sheet/table
			 * @param {jQuery|HTMLElement} o table
			 * @returns {Element}
			 * @methodOf jS
			 * @name rows
			 */
			rows:function (o) {
				o = o || jS.obj.sheet();
				if (!o[0]) return {}; //table
				if (!o[0].children) return {}; //table
				if (!o[0].children[1]) return {}; //tbody
				if (!o[0].children[1].children) return {}; //tr

				return o[0].children[1].children;
			},

			/**
			 *
			 * @param {jQuery|HTMLElement} o table
			 * @returns {Object} {cols, rows}
			 * @methodOf jS
			 * @name sheetSize
			 */
			sheetSize:function (o) {
				o = o || jS.obj.sheet();
				//table / tbody / tr / td

				var lastRow = jS.rowTds(o),
					loc = jS.getTdLocation(lastRow[lastRow.length - 1]);
				return {
					cols:loc.col,
					rows:loc.row
				};
			},

			/**
			 * Toggles from editable to viewable and back
			 * TODO: refactor, not working
			 * @param replacementTables
			 * @methodOf jS
			 * @name toggleState
			 */
			toggleState:function (replacementTables) {
				if (s.allowToggleState) {
					var tables = replacementTables || jS.tables().detach();
					if (s.editable) {
						jS.evt.cellEditAbandon();
						jS.trigger('sheetSave', [tables]);
					}
					jS.setDirty(false);
					jS.setChanged(true);
					s.editable = !s.editable;

					jS.kill();

					s.parent
						.html(tables)
						.sheet(s);
					s = null;
				}
			},

			/**
			 * Turns a cell into a forumla variable so it can be accessed by a name
			 * @param ref
			 * @methodOf jS
			 * @name setCellRef
			 */
			setCellRef:function (ref) {
				var td = jS.obj.cellActive(),
					loc = jS.getTdLocation(td),
					cellRef = (ref ? ref : prompt(jS.msg.setCellRef));

				if (cellRef) { //TODO: need to update value when cell is updated
					jS.s.formulaVariables[cellRef] = jS.updateCellValue(jS.i, loc.row, loc.col);
				}
			}
		};
		jS.setBusy(true);
		s.parent.data('sheetInstance', jS);

		//got tired of ie crashing when console not available
		if (!window.console) window.console = {log:function () {
		}};

		if (!window.scrollBarSize) {
			window.scrollBarSize = $.sheet.getScrollBarSize();
		}

		var $window = $(window),
			$document = $(document),
			$body = $('body'),
			emptyFN = function () {
			},
			u = undefined;

		//ready the sheet's parser
		jS.formulaLexer = function () {
		};
		jS.formulaLexer.prototype = formula.lexer;
		jS.formulaParser = function () {
			this.lexer = new jS.formulaLexer();
			this.yy = {};
		};
		jS.formulaParser.prototype = formula;

		jS.FormulaParser = new jS.formulaParser;

		//We need to take the sheet out of the parent in order to get an accurate reading of it's height and width
		//$(this).html(s.loading);
		s.origHtml = s.parent.children().detach();

		s.parent.addClass(jS.cl.parent);

		s.parent
			.unbind('sheetSwitch')
			.bind('sheetSwitch', function (e, js, i) {
				jS.switchSheet(i);
			})
			.unbind('sheetRename')
			.bind('sheetRename', function (e, js, i) {
				jS.renameSheet(i);
			});

		//Use the setting height/width if they are there, otherwise use parent's
		s.width = (s.width ? s.width : s.parent.width());
		s.height = (s.height ? s.height : s.parent.height());


		// Drop functions if they are not needed & save time in recursion
		if (!s.log) {
			jS.log = emptyFN;
		}

		if (!$.nearest) {
			jS.nearest = emptyFN;
		}

		jS.resizableCells = jS.resizableSheet = jS.resizable;
		if (!$.ui) {
			jS.resizable = jS.draggable = emptyFN;
		} else {
			if (!s.resizableCells) jS.resizableCells = emptyFN;
			if (!s.resizableSheet) jS.resizableSheet = emptyFN;
		}

		if (!$.support.boxModel) {
			s.boxModelCorrection = 0;
		}

		if (!s.barMenus) {
			jS.controlFactory.barMenuTop = jS.controlFactory.barMenuLeft = emptyFN;
		}

		if (!s.freezableCells) {
			jS.controlFactory.barHandleFreeze.top = jS.controlFactory.barHandleFreeze.left = emptyFN;
		}

		if (s.calcOff) {
			jS.calc = emptyFN;
		}

		if (!window.Raphael) {
			jSE.chart = emptyFN;
		}

		//jS.log('Startup');

		$window
			.resize(function () {
				if (jS && !jS.isBusy()) { //We check because jS might have been killed
					s.width = s.parent.width();
					s.height = s.parent.height();
					jS.sheetSyncSize();
				}
			});


		if ($.sheet.fn) { //If the new calculations engine is alive, fill it too, we will remove above when no longer needed.
			//Extend the calculation engine plugins
			$.sheet.fn = $.extend($.sheet.fn, s.formulaFunctions);

			//Extend the calculation engine with advanced functions
			if ($.sheet.advancedfn) {
				$.sheet.fn = $.extend($.sheet.fn, $.sheet.advancedfn);
			}

			//Extend the calculation engine with finance functions
			if ($.sheet.financefn) {
				$.sheet.fn = $.extend($.sheet.fn, $.sheet.financefn);
			}
		}

		if (!s.alertFormulaErrors) {
			jS.alertFormulaError = emptyFN;
		}

		s.title = s.title || s.parent.attr('title') || '';

		jS.s = s;

		if (s.origHtml.length) {
			jS.openSheet(s.origHtml);
		}

		jS.setBusy(false);

		return jS;
	},
	/**
	 * @namespace
	 * @name jQuery.sheet.makeTable
	 */
	makeTable:{
		/**
		 * creates a spreadsheet object from a size given
		 * @methodOf
		 * @param {Object} size {rows: int, cols: int}
		 * @return {jQuery|HTMLElement}
		 */
		fromSize:function (size) {
			size = size || {rows:25, cols:10};

			//Create elements before loop to make it faster.
			var table = jQuery('<table />')
			td = '<td></td>',
				tds = '';

			for (var i = size.cols; i >= 1; i--) {
				tds += td;
			}

			var tr = '<tr style="height: ' + 15 + 'px;">' + tds + '</tr>',
				trs = '';
			for (var i = size.rows; i >= 1; i--) {
				trs += tr;
			}

			return table.html('<tbody>' + trs + '</tbody>');
		}
	},

	/**
	 * Destroy all spreadsheets loaded
	 * @methodOf jQuery.sheet
	 * @name killAll
	 */
	killAll:function () { /* removes all sheets */
		if (jQuery.sheet) {
			if (jQuery.sheet.instance) {
				jQuery.sheet.instance.each(function () {
					if (this.kill) {
						this.kill();
					}
				});
				jQuery.sheet.instance = $([]);
			}
		}
	},

	/**
	 * Make 2 or more spreadsheets scroll to together, useful for history viewing or spreadsheet comparison
	 * @param {Integer} I instance index
	 * @method Of jQuery.sheet
	 * @name scrollLocker
	 */
	scrollLocker:function (I) {
		jQuery.sheet.instance[I].obj.scrolls().each(function (i) {
			var me = this;
			$(this).bind('scroll', function () {
				jQuery.sheet.instance.each(function (j) {
					if (j != I) {
						this.controls.scroll[i]
							.scrollLeft(me.scrollLeft)
							.scrollTop(me.scrollTop);
					}
				});
			});
		});
	},

	/**
	 * Make 2 or more spreadsheets switch together, just like clicking their tabs at the same time
	 * @param {Integer} I instance index
	 * @method Of jQuery.sheet
	 * @name switchSheetLocker
	 */
	switchSheetLocker:function (I) {
		jQuery.sheet.instance.each(function () {
			this.s.parent.bind('switch', function (e, jS, i) {
				jQuery.sheet.instance.each(function () {
					this.setActiveSheet(i);
				});
			});
		});
	},

	/**
	 * Get current instance count
	 * @return {Number}
	 * @methodOf jQuery.sheet
	 * @name I
	 */
	I:function () {
		var I = 0;
		if (this.instance) {
			I = (this.instance.length === 0 ? 0 : this.instance.length - 1); //we use length here because we havent yet created sheet, it will append 1 to this number thus making this the effective instance number
		} else {
			this.instance = [];
		}
		return I;
	},

	/**
	 * Get scrollbar size
	 * @return {Object} {height: int, width: int}
	 * @methodOf jQuery.sheet
	 * @name getScrollBarSize
	 */
	getScrollBarSize:function () {
		var inner = $('<p></p>').css({
				width:'100%',
				height:'100%'
			}),
			outer = $('<div></div>').css({
				position:'absolute',
				width:'100px',
				height:'100px',
				top:'0',
				left:'0',
				visibility:'hidden',
				overflow:'hidden'
			}).append(inner);

		jQuery(document.body).append(outer);

		var w1 = inner.width(),
			h1 = inner.height();

		outer.css('overflow', 'scroll');

		var w2 = inner.width(),
			h2 = inner.height();

		if (w1 == w2 && outer[0].clientWidth) {
			w2 = outer[0].clientWidth;
		}
		if (h1 == h2 && outer[0].clientHeight) {
			h2 = outer[0].clientHeight;
		}

		outer.detach();

		return {
			width:w1 - w2,
			height:h1 - h2
		};
	},

	debugPositionBox:function (x, y, box, color, which) {
		color = color || '#' + Math.floor(Math.random() * 16777215).toString(16);
		if (box) {
			var $box = jQuery([]);
			$box = $box.add(this.debugPositionBox(box.left, box.top, null, color, 'top-left'));
			$box = $box.add(this.debugPositionBox(box.right, box.top, null, color, 'top-right'));
			$box = $box.add(this.debugPositionBox(box.left, box.bottom, null, color, 'bottom-left'));
			$box = $box.add(this.debugPositionBox(box.right, box.bottom, null, color, 'bottom-right'));
			return $box;
		}
		return jQuery('<div style="width: 10px; height: 10px; position: absolute;"></div>')
			.css('top', (y - 5) + 'px')
			.css('left', (x + 5) + 'px')
			.css('background-color', color)
			.click(function () {
				console.log(which || 'none');
			})
			.appendTo('body');
	}
};

/**
 * jQuery.sheet's default formula engine
 * @namespace
 * @name engine
 * @memberOf jQuery.sheet
 */
var jSE = jQuery.sheet.engine = {
	/**
	 * Calculate a spreadsheet
	 * @param {Integer} tableI
	 * @param {Array} spreadsheets [spreadsheet][row][cell], [0][1][1] = SHEET1!A1
	 * @param {Function} ignite, function to run on every cell
	 * @methodOf jQuery.sheet.engine
	 * @name calc
	 */
	calc:function (tableI, spreadsheets, ignite) {
		for (var j = 1; j < spreadsheets.length; j++) {
			for (var k = 1; k < spreadsheets[j].length; k++) {
				ignite(tableI, j, k);
			}
		}
	},

	/**
	 * Parse a cell name to it's location
	 * @param {String} locStr, "A1" = {row: 1, col: 1}
	 * @return {Object} {row: 1, col: 1}
	 * @methodOf jQuery.sheet.engine
	 * @name parseLocation
	 */
	parseLocation:function (locStr) {
		for (var firstNum = 0; firstNum < locStr.length; firstNum++) {
			if (locStr.charCodeAt(firstNum) <= 57) {// 57 == '9'
				break;
			}
		}
		return {
			row:parseInt(locStr.substring(firstNum)),
			col:jSE.columnLabelIndex(locStr.substring(0, firstNum))
		};
	},

	/**
	 * Parse a sheet name to it's index
	 * @param {String} locStr, SHEET1 = 0
	 * @return {Integer}
	 * @methodOf jQuery.sheet.engine
	 * @name parseSheetLocation
	 */
	parseSheetLocation:function (locStr) {
		return ((locStr + '').replace('SHEET', '') * 1) - 1;
	},

	/**
	 *
	 * @param {Integer} col, 1 = A
	 * @param {Integer} row, 1 = 1
	 * @return {String}
	 * @methodOf jQuery.sheet.engine
	 * @name parseCellName
	 */
	parseCellName:function (col, row) {
		return jSE.columnLabelString(col) + (row || '');
	},

	/**
	 * Available labels, used for their index
	 * @memberOf jQuery.sheet.engine
	 * @name columnLabels
	 */
	columnLabels:'ABCDEFGHIJKLMNOPQRSTUVWXYZ',

	/**
	 * Get index of a column label
	 * @param {String} str, A to 1, B to 2, Z to 26, AA to 27
	 * @return {Number}
	 * @methodOf jQuery.sheet.engine
	 * @name columnLabelIndex
	 */
	columnLabelIndex:function (str) {
		var num = 0,
			str = str.toUpperCase();

		for (var i = 0; i < str.length; i++) {
			var digit = this.columnLabels.indexOf(str[i]);
			num = (num * 26) + digit;
		}
		return (num >= 0 ? num : 0) + 1;
	},

	/**
	 * Available indexes, used for their labels
	 * @memberOf jQuery.sheet.engine
	 * @name columnIndexes
	 */
	columnIndexes:[],

	/**
	 * Get label of a column index
	 * @param {Integer} index, 1 = A, 2 = B, 26 = Z, 27 = AA
	 * @return {String}
	 * @name columnLabelString
	 * @methodOf jQuery.sheet.engine
	 */
	columnLabelString:function (index) {
		if (!this.columnIndexes.length) { //cache the indexes to save on processing
			var s = '', i, j, k, l;
			i = j = k = -1;
			for (l = 1; l < 16385; ++l) {
				s = '';
				++k;
				if (k == 26) {
					k = 0;
					++j;
					if (j == 26) {
						j = 0;
						++i;
					}
				}
				if (i >= 0) s += this.columnLabels[i];
				if (j >= 0) s += this.columnLabels[j];
				if (k >= 0) s += this.columnLabels[k];
				this.columnIndexes[l] = s;
			}
		}

		return this.columnIndexes[index] || '';
	},

	/**
	 * Regular expressions cache
	 * @memberOf jQuery.sheet.engine
	 * @name regEx
	 */
	regEx: {
		n: 			    /[\$,\s]/g,
		cell: 			/\$?([a-zA-Z]+)\$?([0-9]+)/gi, //a1
		range: 			/\$?([a-zA-Z]+)\$?([0-9]+):\$?([a-zA-Z]+)\$?([0-9]+)/gi, //a1:a4
		remoteCell:		/\$?(SHEET+)\$?([0-9]+)[:!]\$?([a-zA-Z]+)\$?([0-9]+)/gi, //sheet1:a1
		remoteCellRange:/\$?(SHEET+)\$?([0-9]+)[:!]\$?([a-zA-Z]+)\$?([0-9]+):\$?([a-zA-Z]+)\$?([0-9]+)/gi, //sheet1:a1:b4
		sheet:			/SHEET/i,
		amp: 			/&/g,
		gt: 			/</g,
		lt: 			/>/g,
		nbsp: 			/&nbsp;/g
	},

	/**
	 * Creates a chart, piggybacks RaphealJS
	 * @param {Object} o, options
	 * x: { legend: "", data: [0]}, //x data
	 * y: { legend: "", data: [0]}, //y data
	 * title: "",
	 * data: [0], //chart data
	 * legend: "",
	 * td: jS.getTd(this.sheet, this.row, this.col), //td container for cell
	 * chart: jQuery('<div class="' + jS.cl.chart + '" />') //chart
	 * @return {jQuery|HTMLElement}
	 */
	chart:function (o) {
		var jS = this.jS,
			owner = this;

		function sanitize(v, toNum) {
			if (!v) {
				if (toNum) {
					v = 0;
				} else {
					v = "";
				}
			} else {
				if (toNum) {
					v = arrHelpers.toNumbers(v);
				} else {
					v = arrHelpers.flatten(v);
				}
			}
			return v;
		}

		o = jQuery.extend({
			x:{ legend:"", data:[0]},
			y:{ legend:"", data:[0]},
			title:"",
			data:[0],
			legend:"",
			td:jS.getTd(this.sheet, this.row, this.col),
			chart:jQuery('<div class="' + jS.cl.chart + '" />')
				.mousedown(function () {
					o.td.mousedown();
				}),
			gR:{}
		}, o);

		jS.controls.chart[jS.i] = jS.obj.chart().add(o.chart);

		o.data = sanitize(o.data, true);
		o.x.data = sanitize(o.x.data, true);
		o.y.data = sanitize(o.y.data, true);
		o.legend = sanitize(o.legend);
		o.x.legend = sanitize(o.x.legend);
		o.y.legend = sanitize(o.y.legend);

		o.legend = (o.legend ? o.legend : o.data);

		this.s.parent.one('sheetCalculation', function () {
			var width = o.chart.width(),
				height = o.chart.height(),
				r = Raphael(o.chart[0]);
			if (o.title) r.text(width / 2, 10, o.title).attr({"font-size":20});
			switch (o.type) {
				case "bar":
					o.gR = r.barchart(width / 8, height / 8, width * 0.8, height * 0.8, o.data, o.legend)
						.hover(function () {
							this.flag = r.popup(
								this.bar.x,
								this.bar.y,
								this.bar.value || "0"
							).insertBefore(this);
						}, function () {
							this.flag.animate({
									opacity:0
								}, 300,

								function () {
									this.remove();
								}
							);
						});
					break;
				case "hbar":
					o.gR = r.hbarchart(width / 8, height / 8, width * 0.8, height * 0.8, o.data, o.legend)
						.hover(function () {
							this.flag = r.popup(this.bar.x, this.bar.y, this.bar.value || "0").insertBefore(this);
						}, function () {
							this.flag.animate({
									opacity:0
								}, 300,
								function () {
									this.remove();
								}
							);
						});
					break;
				case "line":
					o.gR = r.linechart(width / 8, height / 8, width * 0.8, height * 0.8, o.x.data, o.y.data, {
						nostroke:false,
						axis:"0 0 1 1",
						symbol:"circle",
						smooth:true
					})
						.hoverColumn(function () {
							this.tags = r.set();
							if (this.symbols.length) {
								for (var i = 0, ii = this.y.length; i < ii; i++) {
									this.tags.push(
										r
											.tag(this.x, this.y[i], this.values[i], 160, 10)
											.insertBefore(this)
											.attr([
											{ fill:"#fff" },
											{ fill:this.symbols[i].attr("fill") }
										])
									);
								}
							}
						}, function () {
							this.tags && this.tags.remove();
						});

					break;
				case "pie":
					o.gR = r.piechart(width / 2, height / 2, (width < height ? width : height) / 2, o.data, {legend:o.legend})
						.hover(function () {
							this.sector.stop();
							this.sector.scale(1.1, 1.1, this.cx, this.cy);

							if (this.label) {
								this.label[0].stop();
								this.label[0].attr({ r:7.5 });
								this.label[1].attr({ "font-weight":800 });
							}
						}, function () {
							this.sector.animate({ transform:'s1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

							if (this.label) {
								this.label[0].animate({ r:5 }, 500, "bounce");
								this.label[1].attr({ "font-weight":400 });
							}
						});
					break;
				case "dot":
					o.gR = r.dotchart(width / 8, height / 8, width * 0.8, height * 0.8, o.x.data, o.y.data, o.data, {
						symbol:"o",
						max:10,
						heat:true,
						axis:"0 0 1 1",
						axisxstep:o.x.data.length - 1,
						axisystep:o.y.data.length - 1,
						axisxlabels:(o.x.legend ? o.x.legend : o.x.data),
						axisylabels:(o.y.legend ? o.y.legend : o.y.data),
						axisxtype:" ",
						axisytype:" "
					})
						.hover(function () {
							this.marker = this.marker || r.tag(this.x, this.y, this.value, 0, this.r + 2).insertBefore(this);
							this.marker.show();
						}, function () {
							this.marker && this.marker.hide();
						});

					break;
			}

			o.gR
				.mousedown(function () {
					o.td.mousedown().mouseup();
				});

			o.chart.mousemove(function () {
				o.td.mousemove();
				return false;
			});

		});

		return o.chart;
	}
};

var jFN = jQuery.sheet.fn = {//fn = standard functions used in cells
	//information functions
	ISNUMBER:function (v) {
		if (!isNaN(v)) {
			return jFN.TRUE();
		}
		return jFN.FALSE();
	},
	N:function (v) {
		if (v == null) {
			return 0;
		}
		if (v instanceof Date) {
			return v.getTime();
		}
		if (typeof(v) == 'object') {
			v = v.toString();
		}
		if (typeof(v) == 'string') {
			v = parseFloat(v.replace(jSE.regEx.n, ''));
		}
		if (isNaN(v)) {
			return 0;
		}
		if (typeof(v) == 'number') {
			return v;
		}
		if (v == true) {
			return 1;
		}
		return 0;
	},
	VERSION:function () {
		return this.jS.version;
	},
	//math functions
	ABS:function (v) {
		return Math.abs(jFN.N(v));
	},
	CEILING:function (value, significance) {
		significance = significance || 1;
		return (parseInt(value / significance) * significance) + significance;
	},
	EVEN:function (v) {
		v = Math.round(v);
		var even = (v % 2 == 0);
		if (!even) {
			if (v > 0) {
				v++;
			} else {
				v--;
			}
		}
		return v;
	},
	EXP:function (v) {
		return Math.exp(v);
	},
	FLOOR:function (value, significance) {
		significance = significance || 1;
		if (
			(value < 0 && significance > 0 ) ||
				(value > 0 && significance < 0 )) {
			return {
				value:0,
				html:"#NUM"
			};
		}
		if (value >= 0) {
			return Math.floor(value / significance) * significance;
		} else {
			return Math.ceil(value / significance) * significance;
		}
	},
	INT:function (v) {
		return Math.floor(jFN.N(v));
	},
	LN:function (v) {
		return Math.log(v);
	},
	LOG:function (v, n) {
		n = n || 10;
		return Math.log(v) / Math.log(n);
	},
	LOG10:function (v) {
		return jFN.LOG(v);
	},
	MOD:function (x, y) {
		var modulus = x % y;
		if (y < 0) {
			modulus *= -1;
		}
		return modulus;
	},
	ODD:function (v) {
		var gTZ = false;
		if (v > 0) {
			v = Math.floor(Math.round(v));
			gTZ = true;
		} else {
			v = Math.ceil(v);
		}

		var vTemp = Math.abs(v);
		if ((vTemp % 2) == 0) { //even
			vTemp++;
		}

		if (gTZ) {
			return vTemp;
		} else {
			return -vTemp;
		}
	},
	PI:function () {
		return Math.PI;
	},
	POWER:function (x, y) {
		return Math.pow(x, y);
	},
	SQRT:function (v) {
		return Math.sqrt(v);
	},
	RAND:function () {
		return Math.random();
	},
	RND:function () {
		return Math.random();
	},
	ROUND:function (v, decimals) {
		return jFN.FIXED(v, (decimals ? decimals : 0), false);
	},
	ROUNDDOWN:function (v, decimals) {
		var neg = (v < 0);
		v = Math.abs(v);
		decimals = decimals || 0;
		v = Math.floor(v * Math.pow(10, decimals)) / Math.pow(10, decimals);
		return (neg ? -v : v);
	},
	ROUNDUP:function (v, decimals) {
		var neg = (v < 0);
		v = Math.abs(v);
		decimals = decimals || 0;
		v = Math.ceil(v * Math.pow(10, decimals)) / Math.pow(10, decimals);
		return (neg ? -v : v);
	},
	SUM:function () {
		var sum = 0,
			v = arrHelpers.toNumbers(arguments);

		for (i in v) {
			sum += v[i] * 1;
		}
		return sum;
	},
	TRUNC:function (number, digits) {
		digits = digits || 0;
		number = number + '';

		if (digits == 0) {
			return number.split('.').shift();
		}

		if (number.match('.')) {
			if (digits == 1) {
				number = number.substr(0, number.length - 1);
			} else if (digits == -1) {
				number = number.split('.').shift();
				number = number.substr(0, number.length - 1) + '0';
			}
		}

		return number;
	},
	//statistical functions
	AVERAGE:function (v) {
		return jFN.SUM(arguments) / jFN.COUNT(arguments);
	},
	AVG:function (v) {
		return jFN.AVERAGE(v);
	},
	COUNT:function () {
		var count = 0,
			v = arrHelpers.toNumbers(arguments);

		for (i in v) {
			if (v[i] != null) count++;
		}

		return count;
	},
	COUNTA:function () {
		var count = 0,
			v = arrHelpers.flatten(arguments);

		for (i in v) {
			if (v[i]) {
				count++;
			}
		}

		return count;
	},
	MAX:function () {
		var v = arrHelpers.toNumbers(arguments),
			max = v[0];

		for (i in v) {
			max = (v[i] > max ? v[i] : max);
		}
		return max;
	},
	MIN:function () {
		var v = arrHelpers.toNumbers(arguments),
			min = v[0];

		for (i in v) {
			min = (v[i] < min ? v[i] : min);
		}
		return min;
	},
	//string functions
	ASC:function (v) {
		return v.charCodeAt(0);
	},
	CHAR:function (v) {
		return String.fromCharCode(v);
	},
	CLEAN:function (v) {
		var exp = new RegExp("[\cG\x1B\cL\cJ\cM\cI\cK\x07\x1B\f\n\r\t\v]","g");
		return v.replace(exp, '');
	},
	CODE:function (v) {
		return jFN.ASC(v);
	},
	CONCATENATE:function () {
		var arr = arrHelpers.flatten(arguments),
			result = '';
		jQuery.each(arr, function (i) {
			result += arr[i];
		});
		return {
			value:result,
			html:result
		};
	},
	DOLLAR:function (v, decimals, symbol) {
		decimals = decimals || 2;
		symbol = symbol || '$';

		var r = jFN.FIXED(v, decimals, false),
			html;
		if (v >= 0) {
			html = symbol + r;
		} else {
			html = '-' + symbol + r.slice(1);
		}
		return {
			value:v,
			html:html
		};
	},
	FIXED:function (v, decimals, noCommas) {
		decimals = decimals || 2;
		return Globalize.format(v, 'n' + decimals)
	},
	LEFT:function (v, numberOfChars) {
		numberOfChars = numberOfChars || 1;
		return v.substring(0, numberOfChars);
	},
	LEN:function (v) {
		if (!v) {
			return 0;
		}
		return v.length;
	},
	LOWER:function (v) {
		return v.toLowerCase();
	},
	MID:function (v, start, end) {
		if (!v || !start || !end) {
			return this.error({error:'ERROR'});
		}
		return v.substring(start - 1, end + start - 1);
	},
	REPLACE:function (oldText, start, numberOfChars, newText) {
		if (!oldText || !start || !numberOfChars || !newText) {
			return this.error({error:'ERROR'});
		}
		var result = oldText.split('');
		result.splice(start - 1, numberOfChars);
		result.splice(start - 1, 0, newText);
		return result.join('');
	},
	REPT:function (v, times) {
		var result = '';
		for (var i = 0; i < times; i++) {
			result += v;
		}
		return result;
	},
	RIGHT:function (v, numberOfChars) {
		numberOfChars = numberOfChars || 1;
		return v.substring(v.length - numberOfChars, v.length);
	},
	SEARCH:function (find, body, start) {
		start = start || 0;
		if (start) {
			body = body.split('');
			body.splice(0, start - 1);
			body = body.join('');
		}
		var i = body.search(find);

		if (i < 0) {
			return this.error({error:'#VALUE!'});
		}

		return start + (start ? 0 : 1) + i;
	},
	SUBSTITUTE:function (text, oldText, newText, nthAppearance) {
		nthAppearance = nthAppearance || 0;
		oldText = new RegExp(oldText, 'g');
		var i = 1;
		text = text.replace(oldText, function (match, contents, offset, s) {
			var result = match;
			if (nthAppearance) {
				if (i >= nthAppearance) {
					result = newText;
				}
			} else {
				result = newText;
			}

			i++;
			return result;
		});
		return text;
	},
	TEXT:function () {
		return this.error({error:'Not Yet Implemented'});
	},
	UPPER:function (v) {
		return v.toUpperCase();
	},
	VALUE:function (v) {
		if (jQuery.isNumeric(v)) {
			return v *= 1;
		} else {
			return this.error({error:"#VALUE!"})
		}
	},
	//date/time functions
	NOW:function () {
		var today = new Date();
		return {
			value:today,
			html:dates.toString(today)
		};
	},
	TODAY:function () {
		var today = new Date();
		return {
			value:dates.toCentury(today) - 1,
			html:dates.toString(today, 'd')
		};
	},
	WEEKENDING:function (weeksBack) {
		var date = new Date();
		date = new Date(
			date.getFullYear(),
			date.getMonth(),
			date.getDate() + 5 - date.getDay() - ((weeksBack || 0) * 7)
		);

		return {
			value:date,
			html:dates.toString(date, 'd')
		};
	},
	WEEKDAY:function (date, returnValue) {
		date = dates.get(date);
		var day = date.getDay();

		returnValue = (returnValue ? returnValue : 1);
		switch (returnValue) {
			case 3:
				switch (day) {
					case 0:return 7;
					case 1:return 1;
					case 2:return 2;
					case 3:return 3;
					case 4:return 4;
					case 5:return 5;
					case 6:return 6;
				}
				break;
			case 2:
				switch (day) {
					case 0:return 6;
					case 1:return 0;
					case 2:return 1;
					case 3:return 2;
					case 4:return 3;
					case 5:return 4;
					case 6:return 5;
				}
				break;
			case 1:
				day++;
				break;
		}

		return day;
	},
	WEEKNUM:function (date) {//TODO: implement week starting
		date = dates.get(date);
		return dates.week(date) + 1;
	},
	YEAR:function (date) {
		date = dates.get(date);
		return date.getFullYear();
	},
	DAYSFROM:function (year, month, day) {
		return Math.floor((new Date() - new Date(year, (month - 1), day)) / dates.dayDiv);
	},
	DAYS:function (v1, v2) {
		var date1 = dates.get(v1),
			date2 = dates.get(v2),
			ONE_DAY = 1000 * 60 * 60 * 24;
		return Math.round(Math.abs(date1.getTime() - date2.getTime()) / ONE_DAY);
	},
	DAY:function (date) {
		date = dates.get(date);
		return date.getDate();
	},
	DAYS360:function (date1, date2, method) {
		date1 = dates.get(date1);
		date2 = dates.get(date2);

		var startDate = date1.getDate(),
			endDate = date2.getDate(),
			startIsLastDay = dates.isLastDayOfMonth(date1),
			endIsLastDay = dates.isLastDayOfMonth(date2),
			monthCount = dates.diffMonths(date1, date2);

		if (method) {//Euro method
			startDate = Math.min(startDate, 30);
			endDate = Math.min(endDate, 30);
		} else { //Standard
			if (startIsLastDay) {
				startDate = 30;
			}
			if (endIsLastDay) {
				if (startDate < 30) {
					monthCount++;
					endDate = 1;
				} else {
					endDate = 30;
				}
			}
		}

		return (monthCount * 30) + (endDate - startDate);
	},
	DATE:function (year, month, day) {
		var date = new Date(year, month - 1, day);
		return {
			html:dates.toString(date, 'd'),
			value:dates.toCentury(date)
		};
	},
	DATEVALUE:function (date) {
		date = dates.get(date);
		return {
			html:dates.toString(date, 'd'),
			value:dates.toCentury(date)
		}
	},
	EDATE:function (date, months) {
		date = dates.get(date),
			date.setMonth(date.getMonth() + months);
		return {
			html:dates.toString(date, 'd'),
			value:dates.toCentury(date)
		};
	},
	EOMONTH:function (date, months) {
		date = dates.get(date),
			date.setMonth(date.getMonth() + months + 1);
		date = new Date(date.getFullYear(), date.getMonth(), 0);
		return {
			html:dates.toString(date, 'd'),
			value:dates.toCentury(date)
		};
	},
	HOUR:function (time) {
		return times.fromMath(time).hour;
	},
	MINUTE:function (time) {
		return times.fromMath(time).minute;
	},
	MONTH:function (date) {
		date = dates.get(date);
		return date.getMonth() + 1;
	},
	SECOND:function (time) {
		return times.fromMath(time).second;
	},
	TIME:function (hour, minute, second) {
		var date = new Date();
		second = (second ? second : 0),
			minute = (minute ? minute : 0),
			hour = (hour ? hour : 0);

		if (second && second > 60) {
			var minuteFromSecond = (((second / 60) + '').split('.')[0]) * 1;
			second = second - (minuteFromSecond * 60);
			minute += minuteFromSecond;
		}

		if (minute && minute > 60) {
			var hourFromMinute = (((minute / 60) + '').split('.')[0]) * 1;
			minute = minute - (hourFromMinute * 60);
			hour += hourFromMinute;
		}

		var millisecond = (hour * 60 * 60 * 1000) + (minute * 60 * 1000) + (second * 1000);

		return millisecond / dates.dayDiv;
	},
	TIMEVALUE:function (time) {
		if (!isNaN(time)) {
			return time;
		}
		if (/([0]?[1-9]|1[0-2])[:][0-5][0-9]([:][0-5][0-9])?[ ]?(AM|am|aM|Am|PM|pm|pM|Pm)/.test(time)) {
			return times.fromString(time, true);
		} else if (/([0]?[0-9]|1[0-9]|2[0-3])[:][0-5][0-9]([:][0-5][0-9])?/.test(time)) {
			return times.fromString(time);
		}
		return 0;
	},
	WORKDAY:function (startDate, days, holidays) {
		var workDays = {1:true, 2:true, 3:true, 4:true, 5:true},
			startDate = dates.get(startDate),
			days = (days && !isNaN(days) ? days : 0),
			dayCounter = 0,
			daysSoFar = 0,
			workingDate = new Date();

		workingDate = startDate;

		if (holidays) {
			if (!jQuery.isArray(holidays)) {
				holidays = [holidays];
			}
			holidays = arrHelpers.flatten(holidays);
			var holidaysTemp = {};
			jQuery.each(holidays, function (i) {
				if (holidays[i]) {
					holidaysTemp[dates.toString(dates.get(holidays[i]), 'd')] = true;
				}
			});
			holidays = holidaysTemp;
		} else {
			holidays = {};
		}

		while (daysSoFar < days) {
			workingDate = new Date(workingDate.setDate(workingDate.getDate() + 1));
			if (workDays[workingDate.getDay()]) {
				if (!holidays[dates.toString(workingDate, 'd')]) {
					daysSoFar++;
				}
			}
			dayCounter++;
		}

		return {
			html:dates.toString(workingDate, 'd'),
			value:dates.toCentury(workingDate)
		};
	},
	YEARFRAC:function (startDate, endDate, basis) {
		startDate = dates.get(startDate);
		endDate = dates.get(endDate);

		if (!startDate || !endDate) {
			return this.error({error:'#VALUE!'});
		}

		basis = (basis ? basis : 0);

		var numerator = dates.diff(startDate, endDate, basis),
			denom = dates.calcAnnualBasis(startDate, endDate, basis);
		return numerator / denom;
	},
	//logical functions
	AND:function () {
		var args = arguments,
			res;
		jQuery.each(args, function (i) {
			if (args[i] !== true && res == undefined) {
				res = jFN.FALSE();
			}
		});
		if (!res) {
			res = jFN.TRUE();
		}
		return res;
	},
	FALSE:function () {
		return {
			value:false,
			html:'FALSE'
		};
	},
	IF:function (expression, resultTrue, resultFalse) {
		var value, html;
		if (expression) {
			value = resultTrue;
			html = this.html[1];
		} else {
			value = resultFalse;
			html = this.html[2];
		}

		return {
			value:value,
			html:html
		};
	},
	NOT:function (v) {
		if (v) {
			return jFN.FALSE();
		}
		return jFN.TRUE();
	},
	OR:function () {
		var args = arguments,
			or;
		jQuery.each(args, function (i) {
			if (args[i] === true && or == undefined) {
				or = jFN.TRUE();
			}
		});
		if (!or) {
			or = jFN.FALSE();
		}
		return or;
	},
	TRUE:function () {
		return {
			value:true,
			html:'TRUE'
		};
	},
	//html function
	IMG:function (v) {
		return {
			html:jQuery('<img />')
				.attr('src', v)
		};
	},
	GETHTML:function () {
		return this.html[0];
	},
	TRIM:function (v) {
		if (typeof(v) == 'string') {
			v = jQuery.trim(v);
		}
		return v;
	},
	HYPERLINK:function (link, name) {
		name = (name ? name : 'LINK');
		return {
			html:jQuery('<a href="' + link + '" target="_new">' + name + '</a>')
		};
	},
	DROPDOWN:function () {
		var cell = this.obj,
			jS = this.jS,
			v = arrHelpers.flatten(arguments),
			html,
			loc = jS.getTdLocation(cell.td);
		v = arrHelpers.unique(v);

		if (this.s.editable) {

			var id = "dropdown" + this.sheet + "_" + loc.row + "_" + loc.col + '_' + this.jS.I;
			html = jQuery('<select style="width: 100%;" name="' + id + '" id="' + id + '" />')
				.mousedown(function () {
					jS.cellEdit(jQuery(this).parent(), null, true);
				})
				.change(function () {
					cell.value = jQuery(this).val();
					jS.calcDependencies(cell.sheet, loc.row, loc.col);
				});

			for (var i = 0; i < (v.length <= 50 ? v.length : 50); i++) {
				if (v[i]) {
					html.append('<option value="' + v[i] + '">' + v[i] + '</option>');
				}
			}

			//here we find out if it is on initial calc, if it is, the value we an use to set the dropdown
			if (jS.getTd(this.sheet, this.row, this.col).find('#' + id).length == 0) {
				cell.value = jS.spreadsheets[this.sheet][this.row][this.col].value;
			}

			html.val(cell.value);
		}
		return {value:cell.value, html:html};
	},
	RADIO:function () {
		var cell = this.obj,
			jS = this.jS,
			v = arrHelpers.flatten(arguments),
			html,
			loc = jS.getTdLocation(cell.td);
		v = arrHelpers.unique(v);


		if (this.s.editable) {
			var id = "radio" + this.sheet + "_" + loc.row + "_" + loc.col + '_' + this.jS.I;

			html = jQuery('<span />')
				.mousedown(function () {
					jS.cellEdit(jQuery(this).parent());
				});

			for (var i = 0; i < (v.length <= 25 ? v.length : 25); i++) {
				if (v[i]) {
					var input = jQuery('<input type="radio" name="' + id + '" class="' + id + '" />')
						.val(v[i])
						.change(function () {
							cell.value = jQuery(this).val();
							jS.calcDependencies(cell.sheet, loc.row, loc.col);
						});

					if (v[i] == cell.value) {
						input.attr('checked', 'true');
					}

					html
						.append(input)
						.append('<span>' + v[i] + '</span>')
						.append('<br />');
				}
			}

			//here we find out if it is on initial calc, if it is, the value we an use to set the radio
			if (jS.getTd(this.sheet, this.row, this.col).find('.' + id).length == 0) {
				cell.value = jS.spreadsheets[this.sheet][this.row][this.col].value;
			}
		}
		return {value:cell.value, html:html};
	},
	CHECKBOX:function (v) {
		if (jQuery.isArray(v)) v = v[0];

		var cell = this.obj,
			jS = this.jS,
			html,
			loc = jS.getTdLocation(cell.td);

		if (this.s.editable) {

			var id = "checkbox" + this.sheet + "_" + loc.row + "_" + loc.col + '_' + this.jS.I,
				checkbox = jQuery('<input type="checkbox" name="' + id + '" class="' + id + '" />')
					.val(v)
					.change(function () {
						cell.value = (jQuery(this).is(':checked') ? jQuery(this).val() : '');
						jS.calcDependencies(cell.sheet, loc.row, loc.col);
					});

			html = jQuery('<span />')
				.append(checkbox)
				.append('<span>' + v + '</span><br />')
				.mousedown(function () {
					jS.cellEdit(jQuery(this).parent());
				});

			if (v == cell.value) {
				checkbox.attr('checked', true);
			}

			var td = jS.getTd(this.sheet, this.row, this.col);
			if (!td.children().length) {
				if (td.html() == cell.value) {
					checkbox.attr('checked', true);
				}
			}

			//here we find out if it is on initial calc, if it is, the value we an use to set the checkbox
			if (jS.getTd(this.sheet, this.row, this.col).find('.' + id).length == 0) {
				var checked = jS.spreadsheets[this.sheet][this.row][this.col].value;
				cell.value = (checked == 'true' || checked == true ? v : '');
			}
		}
		return {value:cell.value, html:html};
	},
	BARCHART:function (values, legend, title) {
		return {
			value:'',
			html:jSE.chart.apply(this, [
				{
					type:'bar',
					data:values,
					legend:legend,
					title:title
				}
			])
		};
	},
	HBARCHART:function (values, legend, title) {
		return {
			value:'',
			html:jSE.chart.apply(this, [
				{
					type:'hbar',
					data:values,
					legend:legend,
					title:title
				}
			])
		};
	},
	LINECHART:function (valuesX, valuesY) {
		return {
			value:'',
			html:jSE.chart.apply(this, [
				{
					type:'line',
					x:{
						data:valuesX
					},
					y:{
						data:valuesY
					},
					title:""
				}
			])
		};
	},
	PIECHART:function (values, legend, title) {
		return {
			value:'',
			html:jSE.chart.apply(this, [
				{
					type:'pie',
					data:values,
					legend:legend,
					title:title
				}
			])
		};
	},
	DOTCHART:function (valuesX, valuesY, values, legendX, legendY, title) {
		return {
			value:'',
			html:jSE.chart.apply(this, [
				{
					type:'dot',
					data:(values ? values : valuesX),
					x:{
						data:valuesX,
						legend:legendX
					},
					y:{
						data:(valuesY ? valuesY : valuesX),
						legend:(legendY ? legendY : legendX)
					},
					title:title
				}
			])
		};
	},
	CELLREF:function (v) {
		return (this.jS.spreadsheets[v] ? this.jS.spreadsheets[v] : 'Cell Reference Not Found');
	},
	CALCTIME:function () {
		var owner = this;
		this.s.parent.one('sheetCalculation', function () {
			owner.jS.getTd(owner.sheet, owner.row, owner.col)
				.text(owner.jS.time.diff());
		});
		return "";
	},
	//cell functions
	HLOOKUP:function (value, tableArray, indexNumber, notExactMatch) {
		var lookupTable = this.jS.cellLookup.apply(this);

		for (var i = 0; i < tableArray[0].length; i++) {
			if (tableArray[0][i] == value) {
				return this.jS.updateCellValue(lookupTable[i].sheet, indexNumber - 1, lookupTable[i].col);
			}
		}

		return notExactMatch;
	},
	VLOOKUP:function (value, tableArray, indexNumber, notExactMatch) {
		var lookupTable = this.jS.cellLookup.apply(this);

		for (var i = 0; i < tableArray[0].length; i++) {
			if (tableArray[0][i] == value) {
				return this.jS.updateCellValue(lookupTable[i].sheet, lookupTable[i].row, indexNumber);
			}
		}

		return notExactMatch;
	},
	THISROWCELL:function (col) {
		if (isNaN(col)) {
			col = jSE.columnLabelIndex(col);
		}
		return this.jS.updateCellValue(this.sheet, this.row, col);
	},
	THISCOLCELL:function (row) {
		return this.jS.updateCellValue(this.sheet, row, this.col);
	}
};

var key = { /* key objects, makes it easier to develop */
	BACKSPACE: 			8,
	CAPS_LOCK: 			20,
	COMMA: 				188,
	CONTROL: 			17,
	ALT:				18,
	DELETE: 			46,
	DOWN: 				40,
	END: 				35,
	ENTER: 				13,
	ESCAPE: 			27,
	HOME: 				36,
	INSERT: 			45,
	LEFT: 				37,
	NUMPAD_ADD: 		107,
	NUMPAD_DECIMAL: 	110,
	NUMPAD_DIVIDE: 		111,
	NUMPAD_ENTER: 		108,
	NUMPAD_MULTIPLY: 	106,
	NUMPAD_SUBTRACT: 	109,
	PAGE_DOWN: 			34,
	PAGE_UP: 			33,
	PERIOD: 			190,
	RIGHT: 				39,
	SHIFT: 				16,
	SPACE: 				32,
	TAB: 				9,
	UP: 				38,
	C:                  67,
	F:					70,
	V:					86,
	X:                  88,
	Y:					89,
	Z:					90
};

var arrHelpers = {
	toNumbers:function (arr) {
		arr = this.flatten(arr);

		for (i in arr) {
			if (arr[i]) {
				arr[i] = jQuery.trim(arr[i]);
				if (isNaN(arr[i])) {
					arr[i] = 0;
				} else {
					arr[i] = arr[i] * 1;
				}
			} else {
				arr[i] = 0;
			}
		}

		return arr;
	},
	unique:function (arr) {
		var a = [],
			l = arr.length;
		for (var i = 0; i < l; i++) {
			for (var j = i + 1; j < l; j++) {
				// If this[i] is found later in the array
				if (arr[i] === arr[j])
					j = ++i;
			}
			a.push(arr[i]);
		}
		return a;
	},
	flatten:function (arr) {
		var flat = [];
		for (var i = 0, l = arr.length; i < l; i++) {
			var type = Object.prototype.toString.call(arr[i]).split(' ').pop().split(']').shift().toLowerCase();
			if (type) {
				flat = flat.concat(/^(array|collection|arguments|object)$/.test(type) ? this.flatten(arr[i]) : arr[i]);
			}
		}
		return flat;
	},
	insertAt:function (arr, val, index) {
		jQuery(val).each(function () {
			if (index > -1 && index <= arr.length) {
				arr.splice(index, 0, this);
			}
		});
		return arr;
	},
	closest:function (array, num, min) {
		array = array || [];
		num = num || 0;
		min = min || 0;

		var closest = array[min],
			diff = Math.abs(num - closest);

		for (var i = min; i < array.length; i++) {
			var newDiff = Math.abs(num - array[i])
			if (newDiff < diff) {
				diff = newDiff;
				closest = array[i];
			}
		}

		return closest;
	}
};

var dates = {
	dayDiv:86400000,
	toCentury:function (date) {
		return Math.round(Math.abs((new Date(1900, 0, -1)) - date) / this.dayDiv);
	},
	get:function (date) {
		if (date.getMonth) {
			return date;
		} else if (isNaN(date)) {
			return new Date(Globalize.parseDate(date));
		} else {
			date *= this.dayDiv;
			//date = new Date(date);
			var newDate = (new Date(1900, 0, -1)) * 1;
			date += newDate;
			date = new Date(date);
			return date;
		}
	},
	week:function (date) {
		var onejan = new Date(date.getFullYear(), 0, 1);
		return Math.ceil((((date - onejan) / this.dayDiv) + onejan.getDay() + 1) / 7);
	},
	toString:function (date, pattern) {
		if (!pattern) {
			return Globalize.format(date);
		}
		return Globalize.format(date, Globalize.culture().calendar.patterns[pattern]);
	},
	diff:function (start, end, basis) {
		switch (basis) {
			case 0:
				return this.days360Nasd(start, end, 0, true);
			case 1:
			case 2:
			case 3:
				var result = Math.abs(end - start) / this.dayDiv;
				return result;
			case 4:
				return this.days360Euro(start, end);
		}
	},
	diffMonths:function (start, end) {
		var months;
		months = (end.getFullYear() - start.getFullYear()) * 12;
		months -= start.getMonth() + 1;
		months += end.getMonth() + 1;
		return months;
	},
	days360:function (startYear, endYear, startMonth, endMonth, startDate, endDate) {
		return ((endYear - startYear) * 360) + ((endMonth - startMonth) * 30) + (endDate - startDate)
	},
	days360Nasd:function (start, end, method, useEom) {
		var startDate = start.getDate(),
			startMonth = start.getMonth(),
			startYear = start.getFullYear(),
			endDate = end.getDate(),
			endMonth = end.getMonth(),
			endYear = end.getFullYear();

		if (
			(endMonth == 2 && this.isEndOfMonth(endDate, endMonth, endYear)) &&
				(
					(startMonth == 2 && this.isEndOfMonth(startDate, startMonth, startYear)) ||
						method == 3
					)
			) {
			endDate = 30;
		}

		if (endDate == 31 && (startDate >= 30 || method == 3)) {
			endDate = 30;
		}

		if (startDate == 31) {
			startDate = 30;
		}

		if (useEom && startMonth == 2 && this.isEndOfMonth(startDate, startMonth, startYear)) {
			startDate = 30;
		}

		return this.days360(startYear, endYear, startMonth, endMonth, startDate, endDate);
	},
	days360Euro:function (start, end) {
		var startDate = start.getDate(),
			startMonth = start.getMonth(),
			startYear = start.getFullYear(),
			endDate = end.getDate(),
			endMonth = end.getMonth(),
			endYear = end.getFullYear();

		if (startDate == 31) startDate = 30;
		if (endDate == 31) endDate = 30;

		return this.days360(startYear, endYear, startMonth, endMonth, startDate, endDate);
	},
	isEndOfMonth:function (day, month, year) {
		return day == (new Date(year, month + 1, 0, 23, 59, 59)).getDate();
	},
	isLeapYear:function (year) {
		return new Date(year, 1, 29).getMonth() == 1;
	},
	calcAnnualBasis:function (start, end, basis) {
		switch (basis) {
			case 0:
			case 2:
			case 4: return 360;
			case 3: return 365;
			case 1:
				var startDate = start.getDate(),
					startMonth = start.getMonth(),
					startYear = start.getFullYear(),
					endDate = end.getDate(),
					endMonth = end.getMonth(),
					endYear = end.getFullYear(),
					result;

				if (startYear == endYear) {
					if (this.isLeapYear(startYear)) {
						result = 366;
					} else {
						result = 365;
					}
				} else if (((endYear - 1) == startYear) && ((startMonth > endMonth) || ((startMonth == endMonth) && startDate >= endDate))) {
					if (this.isLeapYear(startYear)) {
						if (startMonth < 2 || (startMonth == 2 && startDate <= 29)) {
							result = 366;
						} else {
							result = 365;
						}
					} else if (this.isLeapYear(endYear)) {
						if (endMonth > 2 || (endMonth == 2 && endDate == 29)) {
							result = 366;
						} else {
							result = 365;
						}
					} else {
						result = 365;
					}
				} else {
					for (var iYear = startYear; iYear <= endYear; iYear++) {
						if (this.isLeapYear(iYear)) {
							result += 366;
						} else {
							result += 365;
						}
					}
					result = result / (endYear - startYear + 1);
				}
				return result;
		}
	},
	lastDayOfMonth:function (date) {
		date.setDate(0);
		return date.getDate();
	},
	isLastDayOfMonth:function (date) {
		return (date.getDate() == this.lastDayOfMonth(date));
	}
};

var times = {
	fromMath:function (time) {
		var result = {};

		result.hour = ((time * 24) + '').split('.')[0];

		result.minute = function (time) {
			time = Math.round(time * 24 * 100) / 100;
			time = (time + '').split('.');
			var minute = 0;
			if (time[1]) {
				if (time[1].length < 2) {
					time[1] += '0';
				}
				minute = time[1] * 0.6;
			}
			return Math.round(minute);
		}(time);

		result.second = function (time) {
			time = Math.round(time * 24 * 10000) / 10000;
			time = (time + '').split('.');
			var second = 0;
			if (time[1]) {
				for (var i = 0; i < 4; i++) {
					if (!time[1].charAt(i)) {
						time[1] += '0';
					}
				}
				var secondDecimal = ((time[1] * 0.006) + '').split('.');
				if (secondDecimal[1]) {
					if (secondDecimal[1] && secondDecimal[1].length > 2) {
						secondDecimal[1] = secondDecimal[1].substr(0, 2);
					}

					return Math.round(secondDecimal[1] * 0.6);
				}
			}
			return second;
		}(time);

		return result;
	},
	fromString:function (time, isAMPM) {
		var date = new Date(), timeParts = time, timeValue, hour, minute, second, meridiem;
		if (isAMPM) {
			meridiem = timeParts.substr(-2).toLowerCase(); //get ampm;
			timeParts = timeParts.replace(/(am|pm)/i, '');
		}

		timeParts = timeParts.split(':');
		hour = timeParts[0] * 1;
		minute = timeParts[1] * 1;
		second = (timeParts[2] ? timeParts[2] : 0) * 1;

		if (isAMPM && meridiem == 'pm') {
			hour += 12;
		}

		return jFN.TIME(hour, minute, second);
	}
};

var math = {
	log10:function (arg) {
		// http://kevin.vanzonneveld.net
		// +   original by: Philip Peterson
		// +   improved by: Onno Marsman
		// +   improved by: Tod Gentille
		// +   improved by: Brett Zamir (http://brett-zamir.me)
		// *	 example 1: log10(10);
		// *	 returns 1: 1
		// *	 example 2: log10(1);
		// *	 returns 2: 0
		return Math.log(arg) / 2.302585092994046; // Math.LN10
	},
	signum:function (x) {
		return (x / Math.abs(x)) || x;
	}
};
