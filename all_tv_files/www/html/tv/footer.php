<?php 

$str = file_get_contents('/tmp/tv_stats');
$json = json_decode($str, true);
echo '<pre>' . print_r($json, true) . '</pre>';

$str = file_get_contents('/tmp/tv_dir');
$json = json_decode($str, true);
echo '<pre>' . print_r($json, true) . '</pre>';

?>
