

var ws;
var host;


function sendMessage() {
var data = { type: 'chat_message',
             author: document.getElementById("username").value,
             message: document.getElementById("message").value };

if(data.author && data.message) {
  ws.send(JSON.stringify(data));
}
}

window.onload = function() {

host = $()
$('.hand_area').load('/hand');

$('#current_czar_header').load('/czar');

$('#message').keyup(function(evt) {
  if ((evt.keyCode || evt.which) == 13) {
    sendMessage()
    $('#message').val('');
    return false;
  }
});
}
