/**
 * @project jQuery.sheet() The Ajax Spreadsheet - http://code.google.com/p/jquerysheet/
 * @author RobertLeePlummerJr@gmail.com
 * $Id: jquery.sheet.financefn.js 646 2013-01-25 14:44:44Z RobertLeePlummerJr@gmail.com $
 * Licensed under MIT
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */
var jSF = jQuery.sheet.financefn = {
	NPV: function(rate) {
		rate = rate * 1;
		var factor = 1;
		var sum = 0;
		
		for(var i = 1; i < arguments.length; i++) {
			var factor = factor * (1 + rate);
			sum += arguments[i] / factor;
		}
		
		return {
			value: sum,
			html: Globalize.format( sum, "c" )
		};
	},
	PV: function(rate, nper, pmt, fv, type) {
		fv = fv || 0;
		type = type || 0;

		var pv;
		if (rate != 0) {
			pv = (-pmt * (1 + rate * type) * ((Math.pow(1 + rate, nper) - 1) / rate) - fv) / Math.pow(1 + rate, nper);
		} else {
			pv = -fv - pmt * nper;
		}

		return {
			value: pv,
			html: Globalize.format( pv, "c" )
		};
	},
	RATE: function(nper, pmt, pv, fv, type, estimate) {
		fv = fv || 0;
		type = type || 0;
		estimate = estimate || 0.1;

		var rate = estimate, y = 0, f = 0,
			FINANCIAL_MAX_ITERATIONS = 128,
			FINANCIAL_PRECISION = 1.0e-08;
		if (Math.abs(rate) < FINANCIAL_PRECISION) {
			y = pv * (1 + nper * rate) + pmt * (1 + rate * type) * nper + fv;
		} else {
			f = Math.exp(nper * Math.log(1 + rate));
			y = pv * f + pmt * (1 / rate + type) * (f - 1) + fv;
		}
		var y0 = pv + pmt * nper + fv,
			y1 = pv * f + pmt * (1 / rate + type) * (f - 1) + fv;

		// find root by secant method
		var i = 0, x0 = 0,
			x1 = rate;
		while ((Math.abs(y0 - y1) > FINANCIAL_PRECISION) && (i < FINANCIAL_MAX_ITERATIONS)) {
			rate = (y1 * x0 - y0 * x1) / (y1 - y0);
			x0 = x1;
			x1 = rate;

			if (Math.abs(rate) < FINANCIAL_PRECISION) {
				y = pv * (1 + nper * rate) + pmt * (1 + rate * type) * nper + fv;
			} else {
				f = Math.exp(nper * Math.log(1 + rate));
				y = pv * f + pmt * (1 / rate + type) * (f - 1) + fv;
			}

			y0 = y1;
			y1 = y;
			++i;
		}

		return {
			value: rate,
			html: Globalize.format( rate, "p" )
		};
	},
	IPMT: function(rate, per, nper, pv, fv, type) {
		var pmt = jFN.PMT(rate, nper, pv, fv, type).value,
			fv = jFN.FV(rate, per - 1, pmt, pv, type).value,
			result = fv * rate;

		// account for payments at beginning of period versus end.
		if (type) {
			result /= (1 + rate);
		}

		// return results to caller.
		return {
			value: result,
			html: Globalize.format( result, "c" )
		};
	},
	PMT: function(rate, nper, pv, fv, type){
		fv = fv || 0;
		type = type || 0;

		// pmt = rate / ((1 + rate)^N - 1) * -(pv * (1 + r)^N + fv)
		var pmt = rate / (Math.pow(1 + rate, nper) - 1)
			* -(pv * Math.pow(1 + rate, nper) + fv);

		// account for payments at beginning of period versus end.
		if (type == 1) {
			pmt = pmt / (1 + rate);
		}

		// return results to caller.
		return {
			value: pmt,
			html: Globalize.format( pmt, "c" )
		};
	},
	NPER: function(rate, pmt, pv, fv, type) { //not working yet
		type = type || 0;
		if ((rate == 0) && (pmt != 0)) {
			var nper = (-(fv + pv) / pmt);
		} else if (rate <= 0.0) {
			return null;
		} else {
			var tmp = (pmt * (1.0 + rate * type) - fv * rate) /
				(pv * rate + pmt * (1.0 + rate * type));
			if (tmp <= 0.0) {
				return null;
			}
			var nper = (math.log10(tmp) / math.log10(1.0 + rate));
		}
		return (isFinite(nper) ? nper: null);
	},
	FV: function(rate, nper, pmt, pv, type) { //not working yet
		pv = (pv ? pv : 0);
		type = (type ? type : 0);
		var result = -(
			pv*Math.pow(1.0+rate, nper)
			+ pmt * (1.0 + rate*type)
				* (Math.pow(1.0+rate, nper) - 1.0) / rate
		);
		return {
			value: result,
			html: Globalize.format( result, "c" )
		};
	}
}; 
