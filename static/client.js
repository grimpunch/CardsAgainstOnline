var ws;
var user;
var host = null;
var pregame;

function sendMessage() {
var data = { type: 'chat_message',
             author: document.getElementById("username").value,
             message: document.getElementById("message").value };

if(data.author && data.message) {
  ws.send(JSON.stringify(data));
    }
}

window.onload = function() {
    user = $().load('/user');
    pregame = $().load('/pregame');
    if (window.location.pathname == '/host'){
        host = true;
    }
    if (!host){
        $('.hand_area').load('/hand');
    }
    else {
        if (pregame){
            var join_header = $('#join_header');
            join_header.show();
            join_header.text('Go to '+
            window.location.host + ' on your phone!');
        }
    }

    $('#current_czar_header').load('/czar');

    $('#message').keyup(function(evt) {
      if ((evt.keyCode || evt.which) == 13) {
        sendMessage()
        $('#message').val('');
        return false;
      }
    });
};
