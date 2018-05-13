
!function (d, s, id) { var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? 'http' : 'https'; if (!d.getElementById(id)) { js = d.createElement(s); js.id = id; js.src = p + "://platform.twitter.com/widgets.js"; fjs.parentNode.insertBefore(js, fjs); } }(document, "script", "twitter-wjs");

function $(id) {
  return document.getElementById(id);
}

function getPlaces() {
  var t = $('table').tBodies[0].rows;
  var places = [];
  for (var i = 0; i < t.length; i++) {
    var name = t[i].cells[0].innerText;
    var address = t[i].cells[1].innerText;
    places.push({
      'name': name,
      'address': address
    });
  }
  return places;
}

var map;
var markers = [];
var infoWindow;
var service;
var directionsDisplay;
var directionsService;
var places = getPlaces();
var tileListener;
var userLocation = null;

function initMap() {
  directionsService = new google.maps.DirectionsService();
  directionsDisplay = new google.maps.DirectionsRenderer();
  map = new google.maps.Map($('map'), {
    center: { lat: 44.9727, lng: -93.23540000000003 },
    zoom: 14,
    styles: [{
      stylers: [{ visibility: 'simplified' }]
    }, {
      elementType: 'labels',
      stylers: [{ visibility: 'off' }]
    }]
  });

  infoWindow = new google.maps.InfoWindow();
  service = new google.maps.places.PlacesService(map);
  directionsDisplay.setMap(map);
  directionsDisplay.setPanel($('right-panel'));

  // The idle event is a debounced event, so we can query & listen without
  // throwing too many requests at the server.
  google.maps.event.addListenerOnce(map, 'tilesloaded', showMyPlaces);


}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
  infoWindow.setPosition(pos);
  infoWindow.setContent(browserHasGeolocation ?
    'Error: The Geolocation service failed.' :
    'Error: Your browser doesn\'t support geolocation.');
  infoWindow.open(map);
}

function getUserLocation(callback) {
  if (userLocation !== null) {
    callback(userLocation);
  }
  else if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function (position) {
      userLocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      callback(userLocation);
    }, function () {
      handleLocationError(true, infoWindow, map.getCenter());
    });
  }
  else {
    // Browser doesn't support Geolocation
    handleLocationError(false, infoWindow, map.getCenter());
  }
}

function showMyPlaces() {
  clearMap();
  for (var i = 0; i < places.length; i++) {
    var request = {
      bounds: map.getBounds(),
      name: places[i].name,
      keyword: places[i].address
    };
    service.nearbySearch(request, callback);
  }
}

function callback(results, status) {
  if (status !== google.maps.places.PlacesServiceStatus.OK) {
    console.error(status);
    return;
  }
  for (var i = 0, result; result = results[i]; i++) {
    addMarker(result);
  }
}

function addMarker(place) {
  var marker = new google.maps.Marker({
    map: map,
    position: place.geometry.location,
    animation: google.maps.Animation.DROP
  });

  google.maps.event.addListener(marker, 'click', function () {
    service.getDetails(place, function (result, status) {
      if (status !== google.maps.places.PlacesServiceStatus.OK) {
        console.error(status);
        return;
      }
      infoWindow.setContent(`<strong>${result.name}</strong><br>${result.formatted_address}`);
      infoWindow.open(map, marker);
    });
  });

  markers.push(marker);
}

function clearMap() {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(null);
  }
  markers = [];
  directionsDisplay.setMap(null);
}


function searchNearby() {
  var radius = parseFloat($('radius').value);
  var nearby = $('nearby').value;
  getUserLocation(function (location) {
    var request = {
      location: location,
      type: nearby,
      radius: radius
    };
    clearMap();
    service.nearbySearch(request, callback);
    map.setCenter(userLocation);
    map.setZoom(14);
  });
}

function getDirections() {
  clearMap();
  var mode = $('mode').value;
  var dest = $('destination').value;
  getUserLocation(function (location) {
    request = {
      origin: location,
      destination: dest,
      travelMode: mode
    };
    directionsDisplay.setMap(map);
    directionsService.route(request, function (result, status) {
      if (status == 'OK') {
        directionsDisplay.setDirections(result);
      }
    });
  });
}
