jQuery.fn.extend({
	pseudoSheet: function(settings) {
		settings = jQuery.extend({
			error: function(e) { return e.error; },
			dataHandler: {
				visible: function(visible) {
					if (visible) {
						this.$obj.show();
					} else {
						this.$obj.hide();
					}
				},
				enabled: function(enabled) {
					if (enabled) {
						this.$obj.removeAttr('disabled');
					} else {
						this.$obj.attr('disabled', true);
					}
				}
			},
			attrHandler: {
				visible: function() {
					return (this.$obj.is(':visible') ? true : false);
				},
				enabled: function() {
					return (this.$obj.is(':enabled') ? true : false);
				},
				value:   function() {
					return jP.objHandler.getObjectValue(this.$obj);
				}
			},
			formulaFunctions: {}
		}, settings);

		var jP = jQuery.pseudoSheet.createInstance(this, settings);
		jP.calc();

		return this;
	}
});

jQuery.pseudoSheet = { //jQuery.pseudoSheet
	createInstance: function(obj, s) {
		var jP = {
			obj: obj,
			calc: function() {
				jP.calcLast = new Date();
				jPE.calc(jP, jP.updateObjectValue);
			},
			calcLast: 0,
			callStack: 0,
			fn: {
				OBJVAL: function (selector) {
					var values = [];
					jQuery(selector).each(function() {
						var value = jP.updateObjectValue(this);
						if (!isNaN(value)) {
							value *= 1;
						}
						values.push(value ? value : '');
					});

					return (values.length > 1 ? values : values[0]);
				}
			},
			updateObjectValue: function(obj) {
				//first detect if the object exists if not return nothing
				if (!obj) return s.error({error: 'Object not found'});

				var	$obj = jQuery(obj),
					isInput = $obj.is(':input');

				if (isInput) {
					if ($obj.is(':radio,:checkbox')) {
						if ($obj.is(':checked')) {
							obj.val = $obj.filter(':checked').val();
						} else {
							obj.val = '';
						}
					} else {
						obj.val = $obj.val();
					}
				} else {
					obj.val = $obj.html();
				}

				$obj.data('oldValue', obj.val); //we detect the last value, so that we don't have to update all objects, thus saving resources

				if ($obj.data('state')) {
					return s.error({error: "Loop Detected"});
				}

				$obj.data('state', 'red');
				obj.html = [];
				obj.fnCount = 0;
				obj.calcCount = (obj.calcCount ? obj.calcCount : 0);
				obj.calcLast = (obj.calcLast ? obj.calcLast : 0);

				if (obj.calcCount < 1 && obj.calcLast != jP.calcLast) {
					obj.calcLast = jP.calcLast;
					obj.calcCount++;
					var formulaParser;
					if (jP.callStack) { //we prevent parsers from overwriting each other
						if (!obj.formulaParser) { //cut down on un-needed parser creation
							obj.formulaParser = (new jP.formulaParser);
						}
						formulaParser = obj.formulaParser
					} else {//use the sheet's parser if there aren't many calls in the callStack
						formulaParser = jP.FormulaParser;
					}

					jP.callStack++
					formulaParser.lexer.obj = {
						obj: obj,
						type: 'object',
						jP: jP
					};
					formulaParser.lexer.handler = jP.objHandler;

					var data = $obj.data();
					jQuery.each(data, function(i) {
						if (s.dataHandler[i]) {
							var canParse = (data[i].charAt(0) == '='),
								formula = (data[i].charAt(0) == '=' ? data[i].substring(1, data[i].length) : data[i]),
								resultFn = function () {
									var result = jP.filterValue({result: formulaParser.parse(formula)});
									return result.val;
								};

							s.dataHandler[i].apply({
								obj: obj,
								$obj: $obj,
								formula: formula
							}, [resultFn()]);
						}
					});


					if (data.formula) {
						try {
							if (data.formula.charAt(0) == '=') {
								data.formula = data.formula.substring(1, data.formula.length);
							}

							obj.result = formulaParser.parse(data.formula);
						} catch(e) {
							console.log(e);
							obj.val = e.toString().replace(/\n/g, '<br />'); //error
						}
						jP.callStack--;

						obj = jP.filterValue(obj);

						if (isInput) {
							$obj.val(obj.val);
						} else {
							$obj.html(obj.result.html);
						}
					}
				}

				$obj.removeData('state');

				return obj.val;
			},
			filterValue: function (obj) {
				if (typeof obj.result != 'undefined') {
					if (obj.result.value) {
						obj.val = obj.result.value;
					} else {
						obj.val = obj.result;
					}
					if (!obj.result.html && !obj.result.value) {
						obj.result = {val: obj.result, html: obj.result};
					} else {
						obj.result.html = obj.val;
					}
				} else {
					obj.result = {html: obj.val};
				}
				return obj;
			},
			objHandler: {
				callFunction: function(fn, args, obj) {
					if (!args) {
						args = [''];
					} else if (jQuery.isArray(args)) {
						args = args.reverse();
					} else {
						args = [args];
					}

					if (jP.fn[fn]) {
						obj.obj.fnCount++;
						var values = [],
							html = [];

						for(i in args) {
							if (args[i].value && args[i].html) {
								values.push(args[i].value);
								html.push(args[i].html);
							} else {
								values.push(args[i]);
								html.push(args[i]);
							}
						}

						obj.html = html;

						return jP.fn[fn].apply(obj, values);
					} else {
						return s.error({error: "Function Not Found"});
					}
				},
				variable: function() {
					var vars = arguments;

					if (vars.length == 1) {
						switch (vars[0].toLowerCase()) {
							case "true" :   return true;
							case "false":   return false;
						}
					}

					var $obj = jQuery('#' + vars[0]);
					if (!$obj.length) $obj = jQuery('[name="' + vars[0] + '"]');
					if (!$obj.length) return s.error({error: "Object not found"});

					if (vars.length > 1) {
						if (s.attrHandler[vars[1]]) {
							return s.attrHandler[vars[1]].apply({
								$obj: $obj,
								vars: vars
							});
						}
						return s.error({error: "Attribute not found"});
					}

					return jP.objHandler.getObjectValue($obj);
				},
				time: function(time, isAMPM) {
					return times.fromString(time, isAMPM);
				},
				getObjectValue: function($obj) {
					if ($obj.is(':radio,:checkbox')) {
						$obj = $obj.filter(':checked');
					}

					//We don't throw an error here if the item doesn't exist, because we have ensured it does, it is most likely filtered at this point
					if (!$obj[0]) {
						$obj[0] = jQuery('<div />');
					}

					return jP.updateObjectValue($obj[0]);
				},
				concatenate: function() {
					return jFN.CONCATENATE.apply(this, arguments).value;
				}
			}
		};

		if (jQuery.sheet.fn) { //If the new calculations engine is alive, fill it too, we will remove above when no longer needed.
			//Extend the calculation engine plugins
			jP.fn = jQuery.extend(jQuery.sheet.fn, jP.fn);

			//Extend the calculation engine with advanced functions
			if (jQuery.sheet.advancedfn) {
				jP.fn = jQuery.extend(jP.fn, jQuery.sheet.advancedfn);
			}

			//Extend the calculation engine with finance functions
			if (jQuery.sheet.financefn) {
				jP.fn = jQuery.extend(jP.fn, jQuery.sheet.financefn);
			}

			if (s.formulaFunctions) {
				jP.fn = jQuery.extend(jP.fn, s.formulaFunctions);
			}
		}

		//ready the sheet's formulaParser
		jP.formulaLexer = function() {};
		jP.formulaLexer.prototype = formula.lexer;
		jP.formulaParser = function() {
			this.lexer = new jP.formulaLexer();
			this.yy = {};
		};
		jP.formulaParser.prototype = formula;

		jP.FormulaParser = new jP.formulaParser;

		return jP;
	}
};


var jPE = jQuery.pseudoSheetEngine = {//Pseudo Sheet Formula Engine
	calc: function(jP, ignite) {
		for (var i = 0; i < jP.obj.length; i++) {
			jP.obj[i].calcCount = 0;
		}

		for (var i = 0; i < jP.obj.length; i++) {
			ignite(jP.obj[i]);
		}
	}
};