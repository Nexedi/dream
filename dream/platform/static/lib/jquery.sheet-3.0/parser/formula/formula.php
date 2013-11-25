<?php
/* Jison generated parser */

class Formula
{
	var $symbols_ = array();
	var $terminals_ = array();
	var $productions_ = array();
	var $table = array();
	var $defaultActions = array();
	var $version = '0.3.12';
	var $debug = false;

	function __construct()
	{
		//ini_set('error_reporting', E_ALL);
		//ini_set('display_errors', 1);
		
		$accept = 'accept';
		$end = 'end';
		
		//parser
		$this->symbols_ = 		json_decode('{"error":2,"expressions":3,"expression":4,"EOF":5,"variableSequence":6,"TIME_AMPM":7,"TIME_24":8,"number":9,"STRING":10,"=":11,"+":12,"(":13,")":14,"<":15,">":16,"NOT":17,"-":18,"*":19,"/":20,"^":21,"E":22,"FUNCTION":23,"expseq":24,"cell":25,"FIXEDCELL":26,":":27,"CELL":28,"SHEET":29,"!":30,";":31,",":32,"VARIABLE":33,"DECIMAL":34,"NUMBER":35,"%":36,"$accept":0,"$end":1}', true);
		$this->terminals_ = 	json_decode('{"2":"error","5":"EOF","7":"TIME_AMPM","8":"TIME_24","10":"STRING","11":"=","12":"+","13":"(","14":")","15":"<","16":">","17":"NOT","18":"-","19":"*","20":"/","21":"^","22":"E","23":"FUNCTION","26":"FIXEDCELL","27":":","28":"CELL","29":"SHEET","30":"!","31":";","32":",","33":"VARIABLE","34":"DECIMAL","35":"NUMBER","36":"%"}', true);
		$this->productions_ = 	json_decode('[0,[3,2],[4,1],[4,1],[4,1],[4,1],[4,1],[4,3],[4,3],[4,3],[4,4],[4,4],[4,4],[4,3],[4,3],[4,3],[4,3],[4,3],[4,3],[4,3],[4,2],[4,2],[4,1],[4,3],[4,4],[4,1],[25,1],[25,3],[25,1],[25,3],[25,3],[25,5],[24,1],[24,3],[24,3],[6,1],[6,3],[9,1],[9,3],[9,2]]', true);
		$this->table = 			json_decode('[{"3":1,"4":2,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"1":[3]},{"5":[1,19],"11":[1,20],"12":[1,21],"15":[1,22],"16":[1,23],"17":[1,24],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28]},{"5":[2,2],"11":[2,2],"12":[2,2],"14":[2,2],"15":[2,2],"16":[2,2],"17":[2,2],"18":[2,2],"19":[2,2],"20":[2,2],"21":[2,2],"31":[2,2],"32":[2,2],"34":[1,29]},{"5":[2,3],"11":[2,3],"12":[2,3],"14":[2,3],"15":[2,3],"16":[2,3],"17":[2,3],"18":[2,3],"19":[2,3],"20":[2,3],"21":[2,3],"31":[2,3],"32":[2,3]},{"5":[2,4],"11":[2,4],"12":[2,4],"14":[2,4],"15":[2,4],"16":[2,4],"17":[2,4],"18":[2,4],"19":[2,4],"20":[2,4],"21":[2,4],"31":[2,4],"32":[2,4]},{"5":[2,5],"11":[2,5],"12":[2,5],"14":[2,5],"15":[2,5],"16":[2,5],"17":[2,5],"18":[2,5],"19":[2,5],"20":[2,5],"21":[2,5],"31":[2,5],"32":[2,5],"36":[1,30]},{"5":[2,6],"11":[2,6],"12":[2,6],"14":[2,6],"15":[2,6],"16":[2,6],"17":[2,6],"18":[2,6],"19":[2,6],"20":[2,6],"21":[2,6],"31":[2,6],"32":[2,6]},{"4":31,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":32,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":33,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"5":[2,22],"11":[2,22],"12":[2,22],"14":[2,22],"15":[2,22],"16":[2,22],"17":[2,22],"18":[2,22],"19":[2,22],"20":[2,22],"21":[2,22],"31":[2,22],"32":[2,22]},{"13":[1,34]},{"5":[2,25],"11":[2,25],"12":[2,25],"14":[2,25],"15":[2,25],"16":[2,25],"17":[2,25],"18":[2,25],"19":[2,25],"20":[2,25],"21":[2,25],"31":[2,25],"32":[2,25]},{"5":[2,35],"11":[2,35],"12":[2,35],"14":[2,35],"15":[2,35],"16":[2,35],"17":[2,35],"18":[2,35],"19":[2,35],"20":[2,35],"21":[2,35],"31":[2,35],"32":[2,35],"34":[2,35]},{"5":[2,37],"11":[2,37],"12":[2,37],"14":[2,37],"15":[2,37],"16":[2,37],"17":[2,37],"18":[2,37],"19":[2,37],"20":[2,37],"21":[2,37],"31":[2,37],"32":[2,37],"34":[1,35],"36":[2,37]},{"5":[2,26],"11":[2,26],"12":[2,26],"14":[2,26],"15":[2,26],"16":[2,26],"17":[2,26],"18":[2,26],"19":[2,26],"20":[2,26],"21":[2,26],"27":[1,36],"31":[2,26],"32":[2,26]},{"5":[2,28],"11":[2,28],"12":[2,28],"14":[2,28],"15":[2,28],"16":[2,28],"17":[2,28],"18":[2,28],"19":[2,28],"20":[2,28],"21":[2,28],"27":[1,37],"31":[2,28],"32":[2,28]},{"30":[1,38]},{"1":[2,1]},{"4":39,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":40,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":43,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"11":[1,41],"12":[1,10],"13":[1,8],"16":[1,42],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":45,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"11":[1,44],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":46,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":47,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":48,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":49,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":50,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"33":[1,51]},{"5":[2,39],"11":[2,39],"12":[2,39],"14":[2,39],"15":[2,39],"16":[2,39],"17":[2,39],"18":[2,39],"19":[2,39],"20":[2,39],"21":[2,39],"31":[2,39],"32":[2,39],"36":[2,39]},{"11":[1,20],"12":[1,21],"14":[1,52],"15":[1,22],"16":[1,23],"17":[1,24],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28]},{"5":[2,20],"11":[2,20],"12":[2,20],"14":[2,20],"15":[2,20],"16":[2,20],"17":[2,20],"18":[2,20],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,20],"32":[2,20]},{"5":[2,21],"11":[2,21],"12":[2,21],"14":[2,21],"15":[2,21],"16":[2,21],"17":[2,21],"18":[2,21],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,21],"32":[2,21]},{"4":55,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"14":[1,53],"18":[1,9],"22":[1,11],"23":[1,12],"24":54,"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"35":[1,56]},{"26":[1,57]},{"28":[1,58]},{"28":[1,59]},{"5":[2,7],"11":[2,7],"12":[1,21],"14":[2,7],"15":[1,22],"16":[1,23],"17":[1,24],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,7],"32":[2,7]},{"5":[2,8],"11":[2,8],"12":[2,8],"14":[2,8],"15":[2,8],"16":[2,8],"17":[2,8],"18":[2,8],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,8],"32":[2,8]},{"4":60,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":61,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"5":[2,15],"11":[2,15],"12":[1,21],"14":[2,15],"15":[2,15],"16":[2,15],"17":[2,15],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,15],"32":[2,15]},{"4":62,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"5":[2,14],"11":[2,14],"12":[1,21],"14":[2,14],"15":[2,14],"16":[2,14],"17":[2,14],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,14],"32":[2,14]},{"5":[2,13],"11":[2,13],"12":[1,21],"14":[2,13],"15":[1,22],"16":[1,23],"17":[2,13],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,13],"32":[2,13]},{"5":[2,16],"11":[2,16],"12":[2,16],"14":[2,16],"15":[2,16],"16":[2,16],"17":[2,16],"18":[2,16],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,16],"32":[2,16]},{"5":[2,17],"11":[2,17],"12":[2,17],"14":[2,17],"15":[2,17],"16":[2,17],"17":[2,17],"18":[2,17],"19":[2,17],"20":[2,17],"21":[1,28],"31":[2,17],"32":[2,17]},{"5":[2,18],"11":[2,18],"12":[2,18],"14":[2,18],"15":[2,18],"16":[2,18],"17":[2,18],"18":[2,18],"19":[2,18],"20":[2,18],"21":[1,28],"31":[2,18],"32":[2,18]},{"5":[2,19],"11":[2,19],"12":[2,19],"14":[2,19],"15":[2,19],"16":[2,19],"17":[2,19],"18":[2,19],"19":[2,19],"20":[2,19],"21":[2,19],"31":[2,19],"32":[2,19]},{"5":[2,36],"11":[2,36],"12":[2,36],"14":[2,36],"15":[2,36],"16":[2,36],"17":[2,36],"18":[2,36],"19":[2,36],"20":[2,36],"21":[2,36],"31":[2,36],"32":[2,36],"34":[2,36]},{"5":[2,9],"11":[2,9],"12":[2,9],"14":[2,9],"15":[2,9],"16":[2,9],"17":[2,9],"18":[2,9],"19":[2,9],"20":[2,9],"21":[2,9],"31":[2,9],"32":[2,9]},{"5":[2,23],"11":[2,23],"12":[2,23],"14":[2,23],"15":[2,23],"16":[2,23],"17":[2,23],"18":[2,23],"19":[2,23],"20":[2,23],"21":[2,23],"31":[2,23],"32":[2,23]},{"14":[1,63]},{"11":[1,20],"12":[1,21],"14":[2,32],"15":[1,22],"16":[1,23],"17":[1,24],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[1,64],"32":[1,65]},{"5":[2,38],"11":[2,38],"12":[2,38],"14":[2,38],"15":[2,38],"16":[2,38],"17":[2,38],"18":[2,38],"19":[2,38],"20":[2,38],"21":[2,38],"31":[2,38],"32":[2,38],"36":[2,38]},{"5":[2,27],"11":[2,27],"12":[2,27],"14":[2,27],"15":[2,27],"16":[2,27],"17":[2,27],"18":[2,27],"19":[2,27],"20":[2,27],"21":[2,27],"31":[2,27],"32":[2,27]},{"5":[2,29],"11":[2,29],"12":[2,29],"14":[2,29],"15":[2,29],"16":[2,29],"17":[2,29],"18":[2,29],"19":[2,29],"20":[2,29],"21":[2,29],"31":[2,29],"32":[2,29]},{"5":[2,30],"11":[2,30],"12":[2,30],"14":[2,30],"15":[2,30],"16":[2,30],"17":[2,30],"18":[2,30],"19":[2,30],"20":[2,30],"21":[2,30],"27":[1,66],"31":[2,30],"32":[2,30]},{"5":[2,10],"11":[2,10],"12":[1,21],"14":[2,10],"15":[2,10],"16":[2,10],"17":[2,10],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,10],"32":[2,10]},{"5":[2,12],"11":[2,12],"12":[1,21],"14":[2,12],"15":[2,12],"16":[2,12],"17":[2,12],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,12],"32":[2,12]},{"5":[2,11],"11":[2,11],"12":[1,21],"14":[2,11],"15":[2,11],"16":[2,11],"17":[2,11],"18":[1,25],"19":[1,26],"20":[1,27],"21":[1,28],"31":[2,11],"32":[2,11]},{"5":[2,24],"11":[2,24],"12":[2,24],"14":[2,24],"15":[2,24],"16":[2,24],"17":[2,24],"18":[2,24],"19":[2,24],"20":[2,24],"21":[2,24],"31":[2,24],"32":[2,24]},{"4":55,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"24":67,"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"4":55,"6":3,"7":[1,4],"8":[1,5],"9":6,"10":[1,7],"12":[1,10],"13":[1,8],"18":[1,9],"22":[1,11],"23":[1,12],"24":68,"25":13,"26":[1,16],"28":[1,17],"29":[1,18],"33":[1,14],"35":[1,15]},{"28":[1,69]},{"14":[2,33]},{"14":[2,34]},{"5":[2,31],"11":[2,31],"12":[2,31],"14":[2,31],"15":[2,31],"16":[2,31],"17":[2,31],"18":[2,31],"19":[2,31],"20":[2,31],"21":[2,31],"31":[2,31],"32":[2,31]}]', true);
		$this->defaultActions = json_decode('{"19":[2,1],"67":[2,33],"68":[2,34]}', true);
		
		//lexer
		$this->rules = 			array("/^(?:\\s+)/","/^(?:\"(\\\\[\"]|[^\"])*\")/","/^(?:'(\\\\[']|[^'])*')/","/^(?:[A-Za-z]{1,}[A-Za-z_0-9]+(?=[(]))/","/^(?:([0]?[1-9]|1[0-2])[:][0-5][0-9]([:][0-5][0-9])?[ ]?(AM|am|aM|Am|PM|pm|pM|Pm))/","/^(?:([0]?[0-9]|1[0-9]|2[0-3])[:][0-5][0-9]([:][0-5][0-9])?)/","/^(?:SHEET[0-9]+)/","/^(?:\\$[A-Za-z]+\\$[0-9]+)/","/^(?:[A-Za-z]+[0-9]+)/","/^(?:[A-Za-z]+(?=[(]))/","/^(?:[A-Za-z]{1,}[A-Za-z_0-9]+)/","/^(?:[A-Za-z_]+)/","/^(?:[0-9]+)/","/^(?:\\$)/","/^(?: )/","/^(?:[.])/","/^(?::)/","/^(?:;)/","/^(?:,)/","/^(?:\\*)/","/^(?:\\/)/","/^(?:-)/","/^(?:\\+)/","/^(?:\\^)/","/^(?:\\()/","/^(?:\\))/","/^(?:>)/","/^(?:<)/","/^(?:NOT\\b)/","/^(?:PI\\b)/","/^(?:E\\b)/","/^(?:\")/","/^(?:')/","/^(?:!)/","/^(?:=)/","/^(?:%)/","/^(?:$)/");
		$this->conditions = 	json_decode('{"INITIAL":{"rules":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36],"inclusive":true}}', true);
		
		$this->options =		json_decode('{}', true);
	}
	
	function trace()
	{
		
	}
	
	function parser_performAction(&$thisS, $yytext, $yyleng, $yylineno, $yystate, $S, $_S, $O)
	{
		


switch ($yystate) {
case 1:return $S[$O-1];
break;
case 2:
            $thisS = $this->variable($S[$O]);
		
break;
case 3:
		
break;
case 4:
		
break;
case 5:$thisS = $S[$O] * 1;
break;
case 6:
			$thisS = substr($S[$O], 1, -1);
		
break;
case 7:$thisS = $S[$O-2] == $S[$O];
break;
case 8:

			if (is_numeric($S[$O-2]) && is_numeric($S[$O])) {
			  $thisS = $S[$O-2] + $S[$O];
			} else {
			  $thisS = $S[$O-2] . $S[$O];
			}
		
break;
case 9:$thisS = $S[$O-1] * 1;
break;
case 10:$thisS = ($S[$O-3] * 1) <= ($S[$O] * 1);
break;
case 11:$thisS = ($S[$O-3] * 1) >= ($S[$O] * 1);
break;
case 12:$thisS = ($S[$O-3] * 1) != ($S[$O] * 1);
break;
case 13:$thisS = $S[$O-2] != $S[$O];
break;
case 14:$thisS = ($S[$O-2] * 1) > ($S[$O] * 1);
break;
case 15:$thisS = ($S[$O-2] * 1) < ($S[$O] * 1);
break;
case 16:$thisS = ($S[$O-2] * 1) - ($S[$O] * 1);
break;
case 17:$thisS = ($S[$O-2] * 1) * ($S[$O] * 1);
break;
case 18:$thisS = ($S[$O-2] * 1) / ($S[$O] * 1);
break;
case 19:
			$thisS = pow(($S[$O-2] * 1), ($S[$O] * 1));
		
break;
case 20:$thisS = $S[$O] * -1;
break;
case 21:$thisS = $S[$O] * 1;
break;
case 22:/*$thisS = Math.E;*/;
break;
case 23:
			$thisS = $this->callFunction($S[$O-2]);
		
break;
case 24:
			$thisS = $this->callFunction($S[$O-3], $S[$O-1]);
		
break;
case 26:
			$thisS = $this->fixedCellValue($S[$O]);
		
break;
case 27:
			$thisS = $this->fixedCellRangeValue($S[$O-2], $S[$O]);
		
break;
case 28:
			$thisS = $this->cellValue($S[$O]);
		
break;
case 29:
			$thisS = $this->cellRangeValue($S[$O-2], $S[$O]);
		
break;
case 30:
			$thisS = $this->remoteCellValue($S[$O-2], $S[$O]);
		
break;
case 31:
			$thisS = $this->remoteCellRangeValue($S[$O-4], $S[$O-2], $S[$O]);
		
break;
case 32:
			$thisS = array($S[$O]);
		
break;
case 33:

			$thisS = (is_array($S[$O]) ? $S[$O] : array());
			$thisS[] = $S[$O-2];
	    
break;
case 34:

			$thisS = (is_array($S[$O]) ? $S[$O] : array());
			$thisS[] = $S[$O-2];
	    
break;
case 35:
			$thisS = array($S[$O]);
		
break;
case 36:

            $thisS = (is_array($S[$O-2]) ? $S[$O-2] : array());
            $thisS[] = $S[$O];
		
break;
case 37:
			$thisS = $S[$O] * 1;
		
break;
case 38:
			$thisS = $S[$O-2] . '.' . $S[$O];
		
break;
case 39:
			$thisS = $S[$O-1] * 0.01;
		
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
		
		$this->setInput($input);
		
		$yyval = (object)array();
		$yyloc = $this->yyloc;
		$lstack[] = $yyloc;

		while (true) {
			// retreive state number from top of stack
			$state = $stack[$stackCount - 1];
			// use default actions if available
			if (isset($this->defaultActions[$state])) {
				$action = $this->defaultActions[$state];		
			} else {
				if (empty($symbol) == true) {
					$symbol = $this->parser_lex();
				}
				// read action for current state and first input
				if (isset($this->table[$state][$symbol])) {
					$action = $this->table[$state][$symbol];
				} else {
					$action = '';
				}
			}

			if (empty($action) == true) {
				if (!$recovering) {
					// Report error
					$expected = array();
					foreach($this->table[$state] as $p => $item) {
						if (!empty($this->terminals_[$p]) && $p > 2) {
							$expected[] = $this->terminals_[$p];
						}
					}
					
					$errStr = "Parse error on line " . ($this->yylineno + 1) . ":\n" . $this->showPosition() . "\nExpecting " . implode(", ", $expected) . ", got '" . (isset($this->terminals_[$symbol]) ? $this->terminals_[$symbol] : 'NOTHING') . "'";
			
					$this->parseError($errStr, array(
						"text"=> $this->match,
						"token"=> $symbol,
						"line"=> $this->yylineno,
						"loc"=> $yyloc,
						"expected"=> $expected
					));
				}
	
				// just recovered from another error
				if ($recovering == 3) {
					if ($symbol == $this->EOF) {
						$this->parseError(isset($errStr) ? $errStr : 'Parsing halted.');
					}

					// discard current lookahead and grab another
					$yyleng = $this->yyleng;
					$yytext = $this->yytext;
					$yylineno = $this->yylineno;
					$yyloc = $this->yyloc;
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
					$vstackCount -= 1;

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
			if (is_array($action[0])) {
				$this->parseError("Parse Error: multiple actions possible at state: " . $state . ", token: " . $symbol);
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
						$yyleng = $this->yyleng;
						$yytext = $this->yytext;
						$yylineno = $this->yylineno;
						$yyloc = $this->yyloc;
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
					
					$r = $this->parser_performAction($yyval->S, $yytext, $yyleng, $yylineno, $action[1], $vstack, $lstack, $vstackCount - 1);
					
					if (isset($r)) {
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
	var $yyloc = array(
		"first_line"=> 1,
		"first_column"=> 0,
		"last_line"=> 1,
		"last_column"=> 0,
		"range"=> array()
	);
	var $conditionsStack = array();
	var $conditionStackCount = 0;
	var $rules = array();
	var $conditions = array();
	var $done = false;
	var $less;
	var $more;
	var $_input;
	var $options;
	var $offset;
	
	function setInput($input)
	{
		$this->_input = $input;
		$this->more = $this->less = $this->done = false;
		$this->yylineno = $this->yyleng = 0;
		$this->yytext = $this->matched = $this->match = '';
		$this->conditionStack = array('INITIAL');
		$this->yyloc["first_line"] = 1;
		$this->yyloc["first_column"] = 0;
		$this->yyloc["last_line"] = 1;
		$this->yyloc["last_column"] = 0;
		if (isset($this->options->ranges)) {
			$this->yyloc['range'] = array(0,0);
		}
		$this->offset = 0;
		return $this;
	}
	
	function input()
	{
		$ch = $this->_input[0];
		$this->yytext .= $ch;
		$this->yyleng++;
		$this->offset++;
		$this->match .= $ch;
		$this->matched .= $ch;
		$lines = preg_match("/(?:\r\n?|\n).*/", $ch);
		if (count($lines) > 0) {
			$this->yylineno++;
			$this->yyloc['last_line']++;
		} else {
			$this->yyloc['last_column']++;
		}
		if (isset($this->options->ranges)) $this->yyloc['range'][1]++;
		
		$this->_input = array_slice($this->_input, 1);
		return $ch;
	}
	
	function unput($ch)
	{
		$len = strlen($ch);
		$lines = explode("/(?:\r\n?|\n)/", $ch);
		$linesCount = count($lines);
		
		$this->_input = $ch . $this->_input;
		$this->yytext = substr($this->yytext, 0, $len - 1);
		//$this->yylen -= $len;
		$this->offset -= $len;
		$oldLines = explode("/(?:\r\n?|\n)/", $this->match);
		$oldLinesCount = count($oldLines);
		$this->match = substr($this->match, 0, strlen($this->match) - 1);
		$this->matched = substr($this->matched, 0, strlen($this->matched) - 1);
		
		if (($linesCount - 1) > 0) $this->yylineno -= $linesCount - 1;
		$r = $this->yyloc['range'];
		$oldLinesLength = (isset($oldLines[$oldLinesCount - $linesCount]) ? strlen($oldLines[$oldLinesCount - $linesCount]) : 0);
		
		$this->yyloc["first_line"] = $this->yyloc["first_line"];
		$this->yyloc["last_line"] = $this->yylineno + 1;
		$this->yyloc["first_column"] = $this->yyloc['first_column'];
		$this->yyloc["last_column"] = (empty($lines) ?
			($linesCount == $oldLinesCount ? $this->yyloc['first_column'] : 0) + $oldLinesLength :
			$this->yyloc['first_column'] - $len);
		
		if (isset($this->options->ranges)) {
			$this->yyloc['range'] = array($r[0], $r[0] + $this->yyleng - $len);
		}
		
		return $this;
	}
	
	function more()
	{
		$this->more = true;
		return $this;
	}
	
	function pastInput()
	{
		$past = substr($this->matched, 0, strlen($this->matched) - strlen($this->match));
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

		$c = '';
		for($i = 0, $preLength = strlen($pre); $i < $preLength; $i++) {
			$c .= '-';
		}

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
			preg_match($this->rules[$rules[$i]], $this->_input, $tempMatch);
            if ($tempMatch && (empty($match) || count($tempMatch[0]) > count($match[0]))) {
                $match = $tempMatch;
                $index = $i;
                if (isset($this->options->flex) && $this->options->flex == false) break;
            }
		}
		if ( $match ) {
			$matchCount = strlen($match[0]);
			$lineCount = preg_match("/\n.*/", $match[0], $lines);

			$this->yylineno += $lineCount;
			$this->yyloc["first_line"] = $this->yyloc['last_line'];
			$this->yyloc["last_line"] = $this->yylineno + 1;
			$this->yyloc["first_column"] = $this->yyloc['last_column'];
			$this->yyloc["last_column"] = $lines ? count($lines[$lineCount - 1]) - 1 : $this->yyloc['last_column'] + $matchCount;
			
			$this->yytext .= $match[0];
			$this->match .= $match[0];
			$this->matches = $match;
			$this->yyleng = strlen($this->yytext);
			if (isset($this->options->ranges)) {
				$this->yyloc['range'] = array($this->offset, $this->offset += $this->yyleng);
			}
			$this->more = false;
			$this->_input = substr($this->_input, $matchCount, strlen($this->_input));
			$this->matched .= $match[0];
			$token = $this->lexer_performAction($this->yy, $this, $rules[$index], $this->conditionStack[$this->conditionStackCount]);

			if ($this->done == true && empty($this->_input) == false) $this->done = false;

			if (empty($token) == false) {
				return $token;
			} else {
				return;
			}
		}
		
		if (empty($this->_input)) {
			return $this->EOF;
		} else {
			$this->parseError("Lexical error on line " . ($this->yylineno + 1) . ". Unrecognized text.\n" . $this->showPosition(), array(
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
case 1:return 10;
break;
case 2:return 10;
break;
case 3:return 23;
break;
case 4:return 7;
break;
case 5:return 8;
break;
case 6:

	if ($this->type == 'cell') return 'SHEET';
	return 'VARIABLE';

break;
case 7:

	if ($this->type == 'cell') return 'FIXEDCELL';
    return 'VARIABLE';

break;
case 8:

	if ($this->type == 'cell') return 'CELL';
    return 'VARIABLE';

break;
case 9:return 23;
break;
case 10:return 33;
break;
case 11:return 33;
break;
case 12:return 35;
break;
case 13:/* skip whitespace */
break;
case 14:return ' ';
break;
case 15:return 34;
break;
case 16:return 27;
break;
case 17:return 31;
break;
case 18:return 32;
break;
case 19:return 19;
break;
case 20:return 20;
break;
case 21:return 18;
break;
case 22:return 12;
break;
case 23:return 21;
break;
case 24:return 13;
break;
case 25:return 14;
break;
case 26:return 16;
break;
case 27:return 15;
break;
case 28:return 17;
break;
case 29:return 'PI';
break;
case 30:return 22;
break;
case 31:return '"';
break;
case 32:return "'";
break;
case 33:return "!";
break;
case 34:return 11;
break;
case 35:return 36;
break;
case 36:return 5;
break;
}

	}
}