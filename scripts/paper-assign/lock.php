<?php
	session_start();
	$sess = session_id();
	date_default_timezone_set("America/New_York");
	$date_string = date(DATE_ATOM);
	file_put_contents("lock", "{\n\t\"session\":\"" . $sess . "\", \n\t\"date\": \"" . $date_string . "\"\n}", LOCK_EX);
?>