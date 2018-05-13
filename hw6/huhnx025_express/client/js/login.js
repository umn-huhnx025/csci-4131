$('#login').submit(function (event) {
  event.preventDefault();
  $.ajax({
    type: 'POST',
    url: '/validateLoginDetails',
    data: { username: $('#username').val(), password: $('#password').val() },
    success: function (data, textStatus, jqXHR) {
      window.location.replace(data);
    },
    error: function (jqXHR, textStatus, errorThrown) {
      $('#error').text('Error: Invalid credentials');
    }
  });
});
