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
    $.get('/user',function(data) {
        user = data;
    });
    $.get('/pregame',function(data) {
        pregame = data;
    });

    if (window.location.pathname != '/host') {
        $('.hand_area').load('/hand', function() {
            console.log('starting unslider');
            var hand_banner = $('.hand_banner');
            var slidey = hand_banner.unslider();
            data = slidey.data('unslider');
            data.dots();
        });

    } else {
        host = true;
        $('#hand_header').hide();
        $.get("/address", function (data) {
                console.log(data);
                if (pregame) {
                    console.log('callback called');
                    var join_header = $('#join_header');
                    join_header.text('Go to '
                    + data +
                    ' now!');
                    join_header.show();
                }
        });
    }

    $.get("/czar", function (data) {
        var czar_header = $('#current_czar_header');
        var json_resp = data;
        if (json_resp['czar_chosen'] == true){
            czar_header.show();
            czar_header.text('Czar: ' + json_resp['czar']);
        }
        else{
            czar_header.hide();
        }
    });

    $('#message').keyup(function(evt) {
      if ((evt.keyCode || evt.which) == 13) {
        sendMessage();
        $('#message').val('');
        return false;
      }
    });
};
