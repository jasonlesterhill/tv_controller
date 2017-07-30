<?php include 'header.php' ?>
<?php
$cmd = "/usr/bin/python ./tv_motion.py 0 " . time() ;
echo $cmd;
exec('bash -c "exec nohup setsid ' . $cmd . ' > /tmp/phplog 2>&1 &"');
?>

<?php include 'footer.php' ?>

