<?php

$GLOBALS["conexion"] = new PDO('mysql:host=localhost; dbname=dbesp32p', 'root', '');
$GLOBALS["conexion"] -> exec("set names utf8");

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header("Access-Control-Allow-Headers: X-Requested-With");

$json = file_get_contents('php://input');
$data = json_decode($json);
$temp = $data->tempe;
$desc = $data->descr;

$sq = $conexion -> prepare("INSERT INTO `temperatura` (`temperatura`, `descripcion`) VALUES ('$temp','$desc')");
$sq -> execute();

echo json_encode("ok");

?>