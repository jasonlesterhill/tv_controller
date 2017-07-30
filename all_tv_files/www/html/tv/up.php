<?php include 'header.php' ?>
<?php
$cmd = "/usr/bin/python ./tv_motion.py 1 " . time() ;
echo $cmd;
exec('bash -c "exec nohup setsid ' . $cmd . ' > /dev/null 2>&1 &"');
?>

<?php include 'footer.php' ?>

