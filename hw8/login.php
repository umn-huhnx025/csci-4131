<?php
include_once 'database.php';

$error = False;

if (isset($_POST['username'])) {
  $con=new mysqli($db_servername, $db_username, $db_password, $db_name);

  if (mysqli_connect_errno()) {
    echo 'Failed to connect to MySQL:' . mysqli_connect_error();
  }

  $username = $_POST['username'];
  $password = sha1($_POST['password']);
  $result = mysqli_query($con, "SELECT acc_name, acc_password FROM tbl_accounts WHERE acc_login = '$username'");
  $con->close();

  if (mysqli_num_rows($result) < 1) {
    $error = True;
  }

  $row = mysqli_fetch_row($result);

  if ($row[1] != $password) {
    $error = True;
  }

  if (!$error) {
    $_SESSION['name'] = $row[0];
    header('Location: favplaces.php');
    exit;
  }
}
?>

<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="style.css">

  <title>Login</title>
</head>

<body>
  <h1>Login</h1>
  <div class="container">
    <form id="login" action="login.php" method="post">
      <div class="form-group">
        <label for="username">Username:</label>
        <input class="form-control" type="text" name="username" id="username" required>
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input class="form-control" type="password" name="password" id="password" required>
      </div>

      <input class="btn btn-default" type="submit" value="Submit" id="submit">
    </form>
    <div id="error"><?php if ($error) echo "Error: Invalid credentials" ?></div>
  </div>

</body>

</html>
