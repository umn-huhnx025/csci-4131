<?php
session_start();
error_reporting(E_ALL);
ini_set('display_errors','1');
$xml = simplexml_load_file("dbconfig.xml") or die("Error");
$db_servername = $xml->host;
$db_username = $xml->user;
$db_password = $xml->password;
$db_name = $xml->database;
$db_port = $xml->port;
?>
