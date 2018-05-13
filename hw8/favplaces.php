<?php
include_once 'database.php';

if (!isset($_SESSION['name'])) {
  header('Location: login.php');
  exit;
}

$con=new mysqli($db_servername, $db_username, $db_password, $db_name);

if (mysqli_connect_errno()) {
  echo 'Failed to connect to MySQL:' . mysqli_connect_error();
}

if (!empty($_POST['place-id'])) {
  $id = $_POST['place-id'];
  $squery = "SELECT * FROM tbl_places WHERE place_id=$id";
} else if (!empty($_POST['place-name'])) {
  $name = $_POST['place-name'];
  $squery = "SELECT * FROM tbl_places WHERE place_name LIKE '%$name%'";
} else {
  $squery = "SELECT * FROM tbl_places";
}

$result = mysqli_query($con, $squery);
if (!$result) print(mysqli_error($con));
$con->close();
?>

<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
  <link rel="stylesheet" href="style.css">
  <title>My favourite places</title>
</head>

<body>
  <nav class="navbar navbar-default">
    <div class="container-fluid">
      <ul class="nav navbar-nav">
        <li>
          <a href="favplaces.php">
            <b>Favourite places</b>
          </a>
        </li>
        <li>
          <a href="logout.php">
            <span class="glyphicon glyphicon-log-out"></span>
          </a>
        </li>
      </ul>
      <p id="user">Welcome, <?php print($_SESSION['name']) ?></p>
    </div>
  </nav>
  <div class="container">
    <h2>Favorite Places</h2>
    <table class="table" id="myFavTable">
      <thead>
        <tr>
          <th scope="col">Id</th>
          <th scope="col">Name</th>
          <th scope="col">Address</th>
          <th scope="col">Open / Close</th>
          <th scope="col">Information</th>
          <th scope="col">URL</th>
        </tr>
      </thead>
      <tbody>
        <?php
          while($row = mysqli_fetch_row($result)) {
            print("<tr>");
            print("<td>$row[0]</td>");
            print("<td>$row[1]</td>");
            print("<td>$row[2], $row[3]</td>");
            print("<td>$row[4] / $row[5]</td>");
            print("<td>$row[6]</td>");
            print("<td>$row[7]</td>");
            print("</tr>");
          }
        ?>
      </tbody>
    </table>

    <h2>Filter Criteria</h2>
    <form id="filter" action="favplaces.php" method="post">
      <div class="form-group">
        <label for="place-id">Place Id:</label>
        <input class="form-control" type="text" name="place-id" id="place-id" placeholder="Enter place id">
      </div>

      <div class="form-group">
        <label for="place-name">Place Name:</label>
        <input class="form-control" type="text" name="place-name" id="place-name" placeholder="Enter place name">
      </div>

      <input class="btn btn-primary btn-block" type="submit" value="Filter" id="submit">
    </form>
  </div>
</body>

</html>
