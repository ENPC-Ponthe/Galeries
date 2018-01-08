<?php
if ($_FILES["file"]["error"] > 0)
  {
  echo "Error: " . $_FILES["file"]["error"] . "<br>";
  }
else
  {
  echo "Upload: " . $_FILES["file"]["name"] . "<br>";
  echo "Type: " . $_FILES["file"]["type"] . "<br>";
  echo "Size: " . ($_FILES["file"]["size"] / 1024) . " kB<br>";
  echo "Stored in: " . $_FILES["file"]["tmp_name"];
  
	$uploads_dir = '../uploads';
	if ($_FILES["file"]["error"] == UPLOAD_ERR_OK) {
	    $tmp_name = $_FILES["file"]["tmp_name"];
	    // basename() may prevent filesystem traversal attacks;
	    // further validation/sanitation of the filename may be appropriate
	    $name = basename($_FILES["file"]["name"]);
	    move_uploaded_file($tmp_name, "$uploads_dir/$name");
	}
  }
?>
