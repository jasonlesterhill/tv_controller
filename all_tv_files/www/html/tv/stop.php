<?php include 'header.php' ?>
<?php
$fp = fopen('/tmp/tv_dir', 'w');
$response = array();
$response['dir'] = 'stop';
fwrite($fp, json_encode($response));
fclose($fp);
usleep(250000);
?>
<?php include 'footer.php' ?>
