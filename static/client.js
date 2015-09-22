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
    user = $.get('/user',function(text) {msg = text;});
    pregame = $().load('/pregame');
    if (window.location.pathname != '/host') {
        $('.hand_area').load('/hand');
        console.log('user func called');
    } else {
        host = true;
        console.log('host function called');
        $.get("/address", function (data) {
                console.log(data);
                if (pregame) {
                    console.log('callback called');
                    var join_header = $('#join_header');
                    join_header.show();
                    join_header.text('Go to '
                    + data +
                    ' now!');
                }
        });
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
