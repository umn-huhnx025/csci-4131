// YOU CAN USE THIS FILE AS REFERENCE FOR SERVER DEVELOPMENT

// include the express module
var express = require("express");

// create an express application
var app = express();

// helps in extracting the body portion of an incoming request stream
var bodyparser = require('body-parser');

// fs module - provides an API for interacting with the file system
var fs = require("fs");

// helps in managing user sessions
var session = require('express-session');

// native js function for hashing messages with the SHA-1 algorithm
var sha1 = require('sha1');

// include the mysql module
var mysql = require("mysql");

// apply the body-parser middleware to all incoming requests
app.use(bodyparser());

// use express-session
// in memory session is sufficient for this assignment
app.use(session({
  secret: "csci4131secretkey",
  saveUninitialized: true,
  resave: false
}
));

// server listens on port 9007 for incoming connections
app.listen(9007, () => console.log('Listening on port 9007!'));


var con = mysql.createConnection({
  host: "cse-curly.cse.umn.edu",
  user: "C4131S18U44", // replace with the database user provided to you
  password: "49", // replace with the database password provided to you
  database: "C4131S18U44", // replace with the database user provided to you
  port: 3306
});

// // GET method route for the favourites page.
// It serves favourites.html present in client folder
app.get('/favourites', function (req, res) {
  // If not logged in, redirect to login
  if (!req.session.authenticated) {
    res.redirect('/login');
  }
  else {
    res.sendFile(__dirname + '/client/favourites.html');
  }
});

// GET method route for the addPlace page.
// It serves addPlace.html present in client folder
app.get('/addPlace', function (req, res) {
  // If not logged in, redirect to login
  if (!req.session.authenticated) {
    res.redirect('/login');
  }
  else {
    res.sendFile(__dirname + '/client/addPlace.html');
  }
});

// GET method route for the login page.
// It serves login.html present in client folder
app.get('/login', function (req, res) {
  res.sendFile(__dirname + '/client/login.html');
});

// GET method to return the list of favourite places
// The function queries the table tbl_places for the list of places and sends the response back to client
app.get('/getListOfFavPlaces', function (req, res) {
  con.query('SELECT * FROM tbl_places', function (err, result) {
    if (err) throw err;
    res.statusCode = 200;
    res.setHeader('Content-type', 'application/json');
    res.write(JSON.stringify(result, null, 2));
    res.end();
  });
});

// POST method to insert details of a new place to tbl_places table
app.post('/postPlace', function (req, res) {
  var rowToBeInserted = {
    place_name: req.body.placename,
    addr_line1: req.body.addressline1,
    addr_line2: req.body.addressline2,
    open_time: req.body.opentime,
    close_time: req.body.closetime,
    add_info: req.body.additionalinfo,
    add_info_url: req.body.additionalinfourl
  };
  con.query('INSERT tbl_places SET ?', rowToBeInserted, function (err, result) {
    if (err) {
      throw err;
    }
    console.log("Value inserted");
    res.statusCode = 302;
    res.setHeader('Location', '/favourites');
    res.end();
  });
});

// POST method to validate user login
// upon successful login, user session is created
app.post('/validateLoginDetails', function (req, res) {
  var username = req.body.username;
  var password = sha1(req.body.password);

  var sql = `SELECT acc_password FROM tbl_accounts WHERE acc_login = '${username}'`;
  con.query(sql, function (err, result) {
    if (err) {
      throw err;
    }
    var stored_password = result[0].acc_password;
    if (stored_password === password) {
      console.log("Password is correct");
      req.session.authenticated = true;
      res.send('/favourites');
      // res.redirect('/favourites');
    }
    else {
      console.log("Password is incorrect");
      res.status(500).send('Error: Invalid credentials');
    }
  });
});

// log out of the application
// destroy user session
app.get('/logout', function (req, res) {
  req.session.authenticated = false;
  res.redirect('/login');
});

// middle ware to server static files
app.use('/client', express.static(__dirname + '/client'));


// function to return the 404 message and error to client
app.get('*', function (req, res) {
  res.sendFile(__dirname + '/client/404.html');
});
