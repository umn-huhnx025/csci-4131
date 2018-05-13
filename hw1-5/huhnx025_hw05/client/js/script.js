"use strict";

(function () {
	// the API end point
	var url = "getListOfFavPlaces";

	$.ajax({
		url: url, success: function (result) {
			result.res.placeList.forEach(function (el) {
				$('#myFavTable').append(`<tr><td>${el.placename}</td><td>${el.addressline1}<br>${el.addressline2}</td><td>${el.opentime}<br>${el.closetime}</td><td>${el.additionalinfo}</td><td><a href="${el.additionalinfourl}">${el.additionalinfourl}</a></td></tr>`);
			});
		}
	});

})();
