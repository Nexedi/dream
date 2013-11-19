<?php
/* Jison generated parser */

class Parser
{
	var $symbols_ = array();
	var $terminals_ = array();
	var $productions_ = array();
	var $table = array();
	var $defaultActions = array();
	var $debug = false;
	
	function __construct()
	{
		//ini_set('error_reporting', E_ALL);
		//ini_set('display_errors', 1);
		
		$accept = 'accept';
		$end = 'end';
		
		//parser
		$this->symbols_ = 		json_decode('{"error":2,"expressions":3,"e":4,"EOF":5,"=":6,"<":7,">":8,"NOT":9,"+":10,"-":11,"*":12,"/":13,"^":14,"(":15,")":16,"%":17,"NUMBER":18,"E":19,"FIXEDCELL":20,":":21,"CELL":22,"SHEET":23,"!":24,"STRING":25,"IDENTIFIER":26,"expseq":27,";":28,",":29,"$accept":0,"$end":1}', true);
		$this->terminals_ = 	json_decode('{"2":"error","5":"EOF","6":"=","7":"<","8":">","9":"NOT","10":"+","11":"-","12":"*","13":"/","14":"^","15":"(","16":")","17":"%","18":"NUMBER","19":"E","20":"FIXEDCELL","21":":","22":"CELL","23":"SHEET","24":"!","25":"STRING","26":"IDENTIFIER","28":";","29":","}', true);
		$this->productions_ = 	json_decode('[0,[3,2],[4,3],[4,4],[4,4],[4,4],[4,3],[4,3],[4,3],[4,3],[4,3],[4,3],[4,3],[4,3],[4,2],[4,2],[4,3],[4,2],[4,1],[4,1],[4,1],[4,3],[4,1],[4,3],[4,3],[4,5],[4,1],[4,3],[4,4],[27,1],[27,3],[27,3]]', true);
		$this->table = 			json_decode('[{"3":1,"4":2,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"1":[3]},{"5":[1,13],"6":[1,14],"7":[1,15],"8":[1,16],"9":[1,17],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"17":[1,23]},{"4":24,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":25,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":26,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"5":[2,18],"6":[2,18],"7":[2,18],"8":[2,18],"9":[2,18],"10":[2,18],"11":[2,18],"12":[2,18],"13":[2,18],"14":[2,18],"16":[2,18],"17":[2,18],"28":[2,18],"29":[2,18]},{"5":[2,19],"6":[2,19],"7":[2,19],"8":[2,19],"9":[2,19],"10":[2,19],"11":[2,19],"12":[2,19],"13":[2,19],"14":[2,19],"16":[2,19],"17":[2,19],"28":[2,19],"29":[2,19]},{"5":[2,20],"6":[2,20],"7":[2,20],"8":[2,20],"9":[2,20],"10":[2,20],"11":[2,20],"12":[2,20],"13":[2,20],"14":[2,20],"16":[2,20],"17":[2,20],"21":[1,27],"28":[2,20],"29":[2,20]},{"5":[2,22],"6":[2,22],"7":[2,22],"8":[2,22],"9":[2,22],"10":[2,22],"11":[2,22],"12":[2,22],"13":[2,22],"14":[2,22],"16":[2,22],"17":[2,22],"21":[1,28],"28":[2,22],"29":[2,22]},{"24":[1,29]},{"5":[2,26],"6":[2,26],"7":[2,26],"8":[2,26],"9":[2,26],"10":[2,26],"11":[2,26],"12":[2,26],"13":[2,26],"14":[2,26],"16":[2,26],"17":[2,26],"28":[2,26],"29":[2,26]},{"15":[1,30]},{"1":[2,1]},{"4":31,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":34,"6":[1,32],"8":[1,33],"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":36,"6":[1,35],"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":37,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":38,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":39,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":40,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":41,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":42,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"5":[2,17],"6":[2,17],"7":[2,17],"8":[2,17],"9":[2,17],"10":[2,17],"11":[2,17],"12":[2,17],"13":[2,17],"14":[2,17],"16":[2,17],"17":[2,17],"28":[2,17],"29":[2,17]},{"5":[2,14],"6":[2,14],"7":[2,14],"8":[2,14],"9":[2,14],"10":[2,14],"11":[2,14],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,14],"17":[1,23],"28":[2,14],"29":[2,14]},{"5":[2,15],"6":[2,15],"7":[2,15],"8":[2,15],"9":[2,15],"10":[2,15],"11":[2,15],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,15],"17":[1,23],"28":[2,15],"29":[2,15]},{"6":[1,14],"7":[1,15],"8":[1,16],"9":[1,17],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[1,43],"17":[1,23]},{"20":[1,44]},{"22":[1,45]},{"22":[1,46]},{"4":49,"10":[1,4],"11":[1,3],"15":[1,5],"16":[1,47],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12],"27":48},{"5":[2,2],"6":[2,2],"7":[1,15],"8":[1,16],"9":[1,17],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,2],"17":[1,23],"28":[2,2],"29":[2,2]},{"4":50,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"4":51,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"5":[2,8],"6":[2,8],"7":[2,8],"8":[2,8],"9":[2,8],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,8],"17":[1,23],"28":[2,8],"29":[2,8]},{"4":52,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12]},{"5":[2,7],"6":[2,7],"7":[2,7],"8":[2,7],"9":[2,7],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,7],"17":[1,23],"28":[2,7],"29":[2,7]},{"5":[2,6],"6":[2,6],"7":[1,15],"8":[1,16],"9":[2,6],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,6],"17":[1,23],"28":[2,6],"29":[2,6]},{"5":[2,9],"6":[2,9],"7":[2,9],"8":[2,9],"9":[2,9],"10":[2,9],"11":[2,9],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,9],"17":[1,23],"28":[2,9],"29":[2,9]},{"5":[2,10],"6":[2,10],"7":[2,10],"8":[2,10],"9":[2,10],"10":[2,10],"11":[2,10],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,10],"17":[1,23],"28":[2,10],"29":[2,10]},{"5":[2,11],"6":[2,11],"7":[2,11],"8":[2,11],"9":[2,11],"10":[2,11],"11":[2,11],"12":[2,11],"13":[2,11],"14":[1,22],"16":[2,11],"17":[1,23],"28":[2,11],"29":[2,11]},{"5":[2,12],"6":[2,12],"7":[2,12],"8":[2,12],"9":[2,12],"10":[2,12],"11":[2,12],"12":[2,12],"13":[2,12],"14":[1,22],"16":[2,12],"17":[1,23],"28":[2,12],"29":[2,12]},{"5":[2,13],"6":[2,13],"7":[2,13],"8":[2,13],"9":[2,13],"10":[2,13],"11":[2,13],"12":[2,13],"13":[2,13],"14":[2,13],"16":[2,13],"17":[1,23],"28":[2,13],"29":[2,13]},{"5":[2,16],"6":[2,16],"7":[2,16],"8":[2,16],"9":[2,16],"10":[2,16],"11":[2,16],"12":[2,16],"13":[2,16],"14":[2,16],"16":[2,16],"17":[2,16],"28":[2,16],"29":[2,16]},{"5":[2,21],"6":[2,21],"7":[2,21],"8":[2,21],"9":[2,21],"10":[2,21],"11":[2,21],"12":[2,21],"13":[2,21],"14":[2,21],"16":[2,21],"17":[2,21],"28":[2,21],"29":[2,21]},{"5":[2,23],"6":[2,23],"7":[2,23],"8":[2,23],"9":[2,23],"10":[2,23],"11":[2,23],"12":[2,23],"13":[2,23],"14":[2,23],"16":[2,23],"17":[2,23],"28":[2,23],"29":[2,23]},{"5":[2,24],"6":[2,24],"7":[2,24],"8":[2,24],"9":[2,24],"10":[2,24],"11":[2,24],"12":[2,24],"13":[2,24],"14":[2,24],"16":[2,24],"17":[2,24],"21":[1,53],"28":[2,24],"29":[2,24]},{"5":[2,27],"6":[2,27],"7":[2,27],"8":[2,27],"9":[2,27],"10":[2,27],"11":[2,27],"12":[2,27],"13":[2,27],"14":[2,27],"16":[2,27],"17":[2,27],"28":[2,27],"29":[2,27]},{"16":[1,54]},{"6":[1,14],"7":[1,15],"8":[1,16],"9":[1,17],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,29],"17":[1,23],"28":[1,55],"29":[1,56]},{"5":[2,3],"6":[2,3],"7":[2,3],"8":[2,3],"9":[2,3],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,3],"17":[1,23],"28":[2,3],"29":[2,3]},{"5":[2,5],"6":[2,5],"7":[2,5],"8":[2,5],"9":[2,5],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,5],"17":[1,23],"28":[2,5],"29":[2,5]},{"5":[2,4],"6":[2,4],"7":[2,4],"8":[2,4],"9":[2,4],"10":[1,18],"11":[1,19],"12":[1,20],"13":[1,21],"14":[1,22],"16":[2,4],"17":[1,23],"28":[2,4],"29":[2,4]},{"22":[1,57]},{"5":[2,28],"6":[2,28],"7":[2,28],"8":[2,28],"9":[2,28],"10":[2,28],"11":[2,28],"12":[2,28],"13":[2,28],"14":[2,28],"16":[2,28],"17":[2,28],"28":[2,28],"29":[2,28]},{"4":49,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12],"27":58},{"4":49,"10":[1,4],"11":[1,3],"15":[1,5],"18":[1,6],"19":[1,7],"20":[1,8],"22":[1,9],"23":[1,10],"25":[1,11],"26":[1,12],"27":59},{"5":[2,25],"6":[2,25],"7":[2,25],"8":[2,25],"9":[2,25],"10":[2,25],"11":[2,25],"12":[2,25],"13":[2,25],"14":[2,25],"16":[2,25],"17":[2,25],"28":[2,25],"29":[2,25]},{"16":[2,30]},{"16":[2,31]}]', true);
		$this->defaultActions = json_decode('{"13":[2,1],"58":[2,30],"59":[2,31]}', true);
		
		//lexer
		$this->rules = 			array("/^\\s+/","/^\"(\\\\[\"]|[^\"])*\"/","/^'(\\\\[']|[^'])*'/","/^SHEET[0-9]+/","/^\\$[A-Za-z]+\\$[0-9]+/","/^[A-Za-z]+[0-9]+/","/^[A-Za-z]+/","/^[0-9]+(\\.[0-9]+)?/","/^\\$/","/^ /","/^\\./","/^:/","/^;/","/^,/","/^\\*/","/^\\//","/^-/","/^\\+/","/^\\^/","/^\\(/","/^\\)/","/^>/","/^</","/^NOT\\b/","/^PI\\b/","/^E\\b/","/^\"/","/^'/","/^!/","/^=/","/^%/","/^$/");
		$this->conditions = 	json_decode('{"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],"inclusive":true}}', true);
	}
	
	function trace()
	{
		
	}
	
	function parser_performAction(&$thisS, $yytext, $yyleng, $yylineno, $yystate, $S, $_S, $O)
	{
		


switch ($yystate) {
case 1:return $S[$O-1];
break;
case 2:$thisS = ($S[$O-2]) == ($S[$O]);
break;
case 3:$thisS = ($S[$O-3] * 1) <= ($S[$O] * 1);
break;
case 4:$thisS = ($S[$O-3] * 1) >= ($S[$O] * 1);
break;
case 5:$thisS = ($S[$O-3] * 1) != ($S[$O] * 1);
break;
case 6:$thisS = ($S[$O-2] * 1) != ($S[$O] * 1);
break;
case 7:$thisS = ($S[$O-2] * 1) > ($S[$O] * 1);
break;
case 8:$thisS = ($S[$O-2] * 1) < ($S[$O] * 1);
break;
case 9:$thisS = jSE.cFN.sanitize($S[$O-2]) + jSE.cFN.sanitize($S[$O]);
break;
case 10:$thisS = ($S[$O-2] * 1) - ($S[$O] * 1);
break;
case 11:$thisS = ($S[$O-2] * 1) * ($S[$O] * 1);
break;
case 12:$thisS = ($S[$O-2] * 1) / ($S[$O] * 1);
break;
case 13:$thisS = Math.pow(($S[$O-2] * 1), ($S[$O] * 1));
break;
case 14:$thisS = $S[$O] * -1;
break;
case 15:$thisS = $S[$O] * 1;
break;
case 16:$thisS = $S[$O-1];
break;
case 17:$thisS = $S[$O-1] * 0.01;
break;
case 18:$thisS = Number(yytext);
break;
case 19:$thisS = Math.E;
break;
case 20:$thisS = yy->lexer.cellHandler.fixedCellValue.apply(yy->lexer.cell, [$S[$O]]);
break;
case 21:$thisS = yy->lexer.cellHandler.fixedCellRangeValue.apply(yy->lexer.cell, [$S[$O-2], $S[$O]]);
break;
case 22:$thisS = yy->lexer.cellHandler.cellValue.apply(yy->lexer.cell, [$S[$O]]);
break;
case 23:$thisS = yy->lexer.cellHandler.cellRangeValue.apply(yy->lexer.cell, [$S[$O-2], $S[$O]]);
break;
case 24:$thisS = yy->lexer.cellHandler.remoteCellValue.apply(yy->lexer.cell, [$S[$O-2], $S[$O]]);
break;
case 25:$thisS = yy->lexer.cellHandler.remoteCellRangeValue.apply(yy->lexer.cell, [$S[$O-4], $S[$O-2], $S[$O]]);
break;
case 26:$thisS = $S[$O].substring(1, $S[$O].length - 1);
break;
case 27:$thisS = yy->lexer.cellHandler.callFunction($S[$O-2], '', yy->lexer.cell);
break;
case 28:$thisS = yy->lexer.cellHandler.callFunction($S[$O-3], $S[$O-1], yy->lexer.cell);
break;
case 30:
 		$thisS = ($.isArray($S[$O]) ? $S[$O] : [$S[$O]]);
	 	$thisS.push($S[$O-2]);
 	
break;
case 31:
 		$thisS = ($.isArray($S[$O]) ? $S[$O] : [$S[$O]]);
	 	$thisS.push($S[$O-2]);
 	
break;
}

	}

	function parser_lex()
	{
		$token = $this->lexer_lex(); // $end = 1
		$token = (isset($token) ? $token : 1);
		
		// if token isn't its numeric value, convert
		if (isset($this->symbols_[$token]))
			return $this->symbols_[$token];
		
		return $token;
	}
	
	function parseError($str = "", $hash = array())
	{
		throw new Exception($str);
	}
	
	function parse($input)
	{
		$stack = array(0);
		$stackCount = 1;
		
		$vstack = array(null);
		$vstackCount = 1;
		// semantic value stack
		
		$lstack = array($this->yyloc);
		$lstackCount = 1;
		//location stack
		
		$shifts = 0;
		$reductions = 0;
		$recovering = 0;
		$TERROR = 2;
		$EOF = 1;
		
		$this->setInput($input);
		
		$yyval = (object)array();
		$recovered = false;
		
		while (true) {
			// retreive state number from top of stack
			$state = $stack[$stackCount - 1];
			// use default actions if available
			if (isset($this->defaultActions[$state])) {
				$action = $this->defaultActions[$state];		
			} else {
				if (empty($symbol)) {
					$symbol = $this->parser_lex();
				}
				// read action for current state and first input
				if (isset($this->table[$state][$symbol])) {
					$action = $this->table[$state][$symbol];
				}
			}
			
			if (empty($action) == true) {
				if (empty($recovering) == false) {
					// Report error
					$expected = array();
					foreach($this->table[$state] as $p) {
						if ($p > 2) {
							$expected[] = implode($p);
						}
					}
					
					$errStr = 'Parse error on line ' . ($this->yylineno + 1) . ":\n" . $this->showPosition() . '\nExpecting ' . implode(', ', $expected);
			
					$this->parseError($errStr, array(
						"text"=> $this->match,
						"token"=> $symbol,
						"line"=> $this->yylineno,
						"loc"=> $this->yyloc,
						"expected"=> $expected
					));
				}
	
				// just recovered from another error
				if ($recovering == 3) {
					if ($symbol == $EOF) {
						$this->parseError(isset($errStr) ? $errStr : 'Parsing halted.');
					}
		
					// discard current lookahead and grab another
					$symbol = $this->parser_lex();
				}
	
				// try to recover from error
				while (true) {
					// check for error recovery rule in this state
					if (isset($this->table[$state][$TERROR])) {
						break 2;
					}
					if ($state == 0) {
						$this->parseError(isset($errStr) ? $errStr : 'Parsing halted.');
					}
					
					array_slice($stack, 0, 2);
					$stackCount -= 2;
					
					array_slice($vstack, 0, 1);
					
					$state = $stack[$stackCount - 1];
				}
	
				$preErrorSymbol = $symbol; // save the lookahead token
				$symbol = $TERROR; // insert generic error symbol as new lookahead
				$state = $stack[$stackCount - 1];
				if (isset($this->table[$state][$TERROR])) {
					$action = $this->table[$state][$TERROR];
				}
				$recovering = 3; // allow 3 real symbols to be shifted before reporting a new error
			}
	
			// this shouldn't happen, unless resolve defaults are off
			if (isset($action[2])) {
				$this->parseError('Parse Error: multiple actions possible at state: ' . $state . ', token: ' . $symbol);
			}
			
			switch ($action[0]) {
				case 1:
					// shift
					//$this->shiftCount++;
					$stack[] = $symbol;
					$stackCount++;
					
					$vstack[] = $this->yytext;
					$vstackCount++;
					
					$lstack[] = $this->yyloc;
					$lstackCount++;
					
					$stack[] = $action[1]; // push state
					$stackCount++;

					$symbol = "";
					if (empty($preErrorSymbol)) { // normal execution/no error
						if ($recovering > 0) $recovering--;
					} else { // error just occurred, resume old lookahead f/ before error
						$symbol = $preErrorSymbol;
						$preErrorSymbol = "";
					}
					break;
		
				case 2:
					// reduce
					$len = $this->productions_[$action[1]][1];
					// perform semantic action
					$yyval->S = $vstack[$vstackCount - $len];// default to $S = $1
					// default location, uses first token for firsts, last for lasts
					$yyval->_S = array(
                        "first_line"=> 		$lstack[$lstackCount - (isset($len) ? $len : 1)]['first_line'],
                        "last_line"=> 		$lstack[$lstackCount - 1]['last_line'],
                        "first_column"=> 	$lstack[$lstackCount - (isset($len) ? $len : 1)]['first_column'],
                        "last_column"=> 	$lstack[$lstackCount - 1]['last_column']
                    );
					
					$r = $this->parser_performAction($yyval->S, $this->yytext, $this->yyleng, $this->yylineno, $action[1], $vstack, $lstack, $vstackCount - 1);
					
					if (empty($r) == false) {
						return $r;
					}
					
					// pop off stack		
					if ($len > 0) {
						$stack = array_slice($stack, 0, -1 * $len * 2);
						$stackCount -= $len * 2;
					
						$vstack = array_slice($vstack, 0, -1 * $len);
						$vstackCount -= $len;
						
						$lstack = array_slice($lstack, 0, -1 * $len);
						$lstackCount -= $len;
					}
					
					$stack[] = $this->productions_[$action[1]][0]; // push nonterminal (reduce)
					$stackCount++;
					
					$vstack[] = $yyval->S;
					$vstackCount++;
					
					$lstack[] = $yyval->_S;
					$lstackCount++;
					
					// goto new state = table[STATE][NONTERMINAL]
					$newState = $this->table[$stack[$stackCount - 2]][$stack[$stackCount - 1]];
					
					$stack[] = $newState;
					$stackCount++;
					
					break;
		
				case 3:
					// accept
					return true;
			}

		}

		return true;
	}


	/* Jison generated lexer */
	var $EOF = 1;
	var $S = "";
	var $yy = "";
	var $yylineno = "";
	var $yyleng = "";
	var $yytext = "";
	var $match = "";
	var $matched = "";
	var $matches = "";
	var $yyloc = array();
	var $conditionsStack = array();
	var $conditionStackCount = 0;
	var $rules = array();
	var $conditions = array();
	var $done = false;
	var $less;
	var $more;
	var $_input;
	
	function setInput($input)
	{
		$this->_input = $input;
		$this->more = $this->less = $this->done = false;
		$this->yylineno = $this->yyleng = 0;
		$this->yytext = $this->matched = $this->match = '';
		$this->conditionStack = array('INITIAL');
		$this->yyloc = array(
			"first_line"=> 1,
			"first_column"=> 0,
			"last_line"=> 1,
			"last_column"=> 0
		);
	}
	
	function input()
	{
		$ch = $this->_input[0];
		$this->yytext .= $ch;
		$this->yyleng++;
		$this->match .= $ch;
		$this->matched .= $ch;
		$lines = preg_match("/\n/", $ch);
		if (count($lines) > 0) $this->yylineno++;
		array_slice($this->_input, 1);
		return $ch;
	}
	
	function unput($ch)
	{
		$this->_input = $ch . $this->_input;
		return $this;
	}
	
	function more()
	{
		$this->more = true;
		return $this;
	}
	
	function pastInput()
	{
		$past = substr($this->matched, 0, count($this->matched) - count($this->match));
		return (strlen($past) > 20 ? '...' : '') . preg_replace("/\n/", "", substr($past, -20));
	}
	
	function upcomingInput()
	{
		$next = $this->match;
		if (strlen($next) < 20) {
			$next .= substr($this->_input, 0, 20 - strlen($next));
		}
		return preg_replace("/\n/", "", substr($next, 0, 20) . (strlen($next) > 20 ? '...' : ''));
	}
	
	function showPosition()
	{
		$pre = $this->pastInput();
		$c = implode(array(strlen($pre) + 1), "-");
		return $pre . $this->upcomingInput() . "\n" . $c . "^";
	}
	
	function next()
	{
		if ($this->done == true) return $this->EOF;
		
		if (empty($this->_input)) $this->done = true;

		if ($this->more == false) {
			$this->yytext = '';
			$this->match = '';
		}
		
		$rules = $this->_currentRules();
		for ($i = 0, $j = count($rules); $i < $j; $i++) {
			preg_match($this->rules[$rules[$i]], $this->_input, $match);
			if ( isset($match[0]) ) {
				$matchCount = strlen($match[0]);
				$lineCount = preg_match("/\n.*/", $match[0], $lines);
				
				if ($lineCount > 1) $this->yylineno += $lineCount;
				$this->yyloc = array(
					"first_line"=> $this->yyloc['last_line'],
					"last_line"=> $this->yylineno + 1,
					"first_column"=> $this->yyloc['last_column'],
					"last_column"=> $lines ? count($lines[$lineCount - 1]) - 1 : $this->yyloc['last_column'] + $matchCount
				);
				$this->yytext .= $match[0];
				$this->match .= $match[0];
				$this->matches = $match[0];
				$this->yyleng = strlen($this->yytext);
				$this->more = false;
				$this->_input = substr($this->_input, $matchCount, strlen($this->_input));
				$this->matched .= $match[0];
				$token = $this->lexer_performAction($this->yy, $this, $rules[$i], $this->conditionStack[$this->conditionStackCount]);
				
				if (empty($token) == false) {
					return $token;
				} else {
					return;
				}
			}
		}
		
		if (empty($this->_input)) {
			return $this->EOF;
		} else {
			$this->parseError('Lexical error on line ' . ($this->yylineno + 1) . '. Unrecognized text.\n' . $this->showPosition(), array(
				"text"=> "",
				"token"=> null,
				"line"=> $this->yylineno
			));
		}
	}
	
	function lexer_lex()
	{
		$r = $this->next();
		
		while (empty($r) && $this->done == false) {
			$r = $this->next();
		}
		
		return $r;
	}
	
	function begin($condition)
	{
		$this->conditionStackCount++;
		$this->conditionStack[] = $condition;
	}
	
	function popState()
	{
		$this->conditionStackCount--;
		return array_pop($this->conditionStack);
	}
	
	function _currentRules()
	{
		return $this->conditions[
			$this->conditionStack[
				$this->conditionStackCount
			]
		]['rules'];
	}
	
	function lexer_performAction(&$yy, $yy_, $avoiding_name_collisions, $YY_START = null)
	{
		$YYSTATE = $YY_START;
		


switch($avoiding_name_collisions) {
case 0:/* skip whitespace */
break;
case 1:return 25;
break;
case 2:return 25;
break;
case 3:return 23;
break;
case 4:return 20;
break;
case 5:return 22;
break;
case 6:return 26;
break;
case 7:return 18;
break;
case 8:/* skip whitespace */
break;
case 9:return ' ';
break;
case 10:return '.';
break;
case 11:return 21;
break;
case 12:return 28;
break;
case 13:return 29;
break;
case 14:return 12;
break;
case 15:return 13;
break;
case 16:return 11;
break;
case 17:return 10;
break;
case 18:return 14;
break;
case 19:return 15;
break;
case 20:return 16;
break;
case 21:return 8;
break;
case 22:return 7;
break;
case 23:return 9;
break;
case 24:return 'PI';
break;
case 25:return 19;
break;
case 26:return '"';
break;
case 27:return "'";
break;
case 28:return "!";
break;
case 29:return 6;
break;
case 30:return 17;
break;
case 31:return 5;
break;
}

	}
}
