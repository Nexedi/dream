<?php

ini_set('error_reporting', E_ALL);
ini_set('display_errors', 1);

include_once '../parser/formula/formula.php';
include_once 'handler.php';
include_once 'formulas.php';

if (empty($_REQUEST['ss'])) {
	echo "Spreadsheet needed";
	exit();
}

$spreadsheets = json_decode($_REQUEST['ss']);

$formulas = new formulas();

$handler = ParserHandler::initSimpleJson($spreadsheets, $formulas);
$handler->calc();

if (isset($_REQUEST['c'])) {
	$cell = $_REQUEST['c'];
	$sheet = (isset($_REQUEST['s']) ? $_REQUEST['s'] : 0);
	$handler->setSheet($sheet);
	echo json_encode($handler->cellValue($cell));
} else if (isset($_REQUEST['cr'])) {
	$cells = explode(':', $_REQUEST['cr']);
	$sheet = (isset($_REQUEST['s']) ? $_REQUEST['s'] : 0);
	$handler->setSheet($sheet);
	echo json_encode($handler->cellRangeValue($cells[0], $cells[1]));
} else {
	echo json_encode($handler->toArray(isset($_REQUEST['s']) ? $_REQUEST['s'] : null));
}