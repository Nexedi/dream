<?php
class formulas
{
	public $inputs;
	public $outputs;

	function sum($cell, $array)
	{
		return array_sum($array);
	}

	function divide($cell, $array)
	{
		return array_sum($array);
	}

	function average($cell, $array)
	{
		$total = 0;
		$count = count($array);
		foreach ($array as $value) {
			$total = $total + $value;
		}
		$average = ($total / $count);
		return $average;
	}

	function avg($cell, $array)
	{
		return $this->average($cell, $array);
	}

	function count($cell, $array)
	{
		$count = 0;

		foreach ($array as $value) {
			if ($value != null) $count++;
		}

		return $count;
	}

	function counta($cell, $array)
	{
		$count = 0;

		foreach ($array as $value) {
			if (!empty($value)) $count++;
		}

		return $count;
	}

	function max($cell, $array)
	{
		return max($array);
	}

	function min($cell, $array)
	{
		return min($array);
	}

	function mean($cell, $array)
	{
		sort($array);
		$count = count($array); //total numbers in array
		$middleval = floor(($count-1)/2); // find the middle value, or the lowest middle value
		if($count % 2) { // odd number, middle is the median
			$median = $array[$middleval];
		} else { // even number, calculate avg of 2 medians
			$low = $array[$middleval];
			$high = $array[$middleval+1];
			$median = (($low+$high)/2);
		}
		return $median;
	}

	function abs($cell, $array)
	{
		return abs($array);
	}

	function ceiling($cell, $array)
	{
		return ceil($array);
	}

	function floor($cell, $array)
	{
		return floor($array);
	}

	function int($cell, $array)
	{
		return floor($array);
	}

	function round($cell, $array)
	{
		return round($array);
	}

	function rand($cell, $array)
	{
		return rand();
	}

	function rnd($cell, $array)
	{
		return $this->rand($cell, $array);
	}

	function true($cell, $array)
	{
		return 'TRUE';
	}

	function false($cell, $array)
	{
		return 'FALSE';
	}

	function pi($cell, $array)
	{
		return pi();
	}

	function power($cell, $array)
	{
		return pow($array[0], $array[1]);
	}

	function sqrt($cell, $array)
	{
		return sqrt($array);
	}

	function input($cell, $array)
	{
		return (!empty($this->inputs[$array[0]]) ? $this->inputs[$array[0]] : 0);
	}

	function output($cell, $array)
	{
		$this->outputs[$array[0]] = (!empty($array[1]) ? $array[1] : 0);
		return '';
	}
}