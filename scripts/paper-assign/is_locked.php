<?php
	session_start();
	$sess = session_id();

	if (!file_exists("lock")) {
		print "0";
		exit();
	}
	$data = file_get_contents("lock");
	$dict = json_decode($data,true);

	if ($dict["session"] == $sess) {
		print "1";
	} else {
		print "2";
	}
?>