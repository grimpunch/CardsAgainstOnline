var ws;
var user;
var host = null;
var pregame;
var user_id;

var websocket = new WebSocket("ws://"+window.location.hostname+":8889");

function sendMessage(message) {
var data = { type: 'game_state_message',
             user_id: user_id,
             user: user,
             message: message };

if(data.author && data.message) {
  websocket.send(JSON.stringify(data));
    }
}

window.onload = function() {
    $.when( $.get('/user'), $.get('/pregame')).then(
        function(d1,d2) {
            user = d1[0].name;
            user_id = d1[0].id;
            pregame = d2[0].pregame;
        console.log(user);
        console.log(user_id);
        console.log(pregame);
        if (window.location.pathname != '/host') {
            $('.hand_area').load('/hand', function(data) {
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
                        user_id = '0000';
                        sendMessage('Host is ready');
                    }
            });
        }
        get_czar();
    });

};

function get_czar(){
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
}
