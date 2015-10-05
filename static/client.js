var ws;
var user;
var host = null;
var pregame;
var user_id;

function sendMessage(message) {
var data = { type: 'game_state_message',
             user_id: user_id,
             user: user,
             message: message };

if(data.author && data.message) {
  socket.emit('my event', (JSON.stringify(data)));
    }
}

$(document).ready(function(){
            namespace = '/test'; // change to an empty string to use the global namespace
            // the socket.io documentation recommends sending an explicit package upon connection
            // this is specially important when using the global namespace
            var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
            socket.on('connect', function() {
                socket.emit('my event', {data: 'I\'m connected!'});
            });
            // event handler for server sent data
            // the data is displayed in the "Received" section of the page
            socket.on('my response', function(msg) {
                console.log('<br>Received #' + msg.count + ': ' + msg.data);
            });
            // handlers for the different forms in the page
            // these send data to the server in a variety of ways
            $('form#emit').submit(function(event) {
                socket.emit('my event', {data: $('#emit_data').val()});
                return false;
            });
            $('form#broadcast').submit(function(event) {
                socket.emit('my broadcast event', {data: $('#broadcast_data').val()});
                return false;
            });
            $('form#join').submit(function(event) {
                socket.emit('join', {room: $('#join_room').val()});
                return false;
            });
            $('form#leave').submit(function(event) {
                socket.emit('leave', {room: $('#leave_room').val()});
                return false;
            });
            $('form#send_room').submit(function(event) {
                socket.emit('my room event', {room: $('#room_name').val(), data: $('#room_data').val()});
                return false;
            });
            $('form#close').submit(function(event) {
                socket.emit('close room', {room: $('#close_room').val()});
                return false;
            });
            $('form#disconnect').submit(function(event) {
                socket.emit('disconnect request');
                return false;
            });
        });

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
