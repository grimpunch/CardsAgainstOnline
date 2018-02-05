var ws;
var username; // string
var user_is_host = false; // bool
var is_pregame = false; // bool
var user_id; // stringy int
var white_card_id; // int
var round = 0; // int (current turn)
var player_count = 0;

var lobby_state = 0; // state machine tracker for lobby state
var game_state = 0; // state machine tracker for game state
var turn_state = 0; // state machine tracker for turn state

const LOBBY_STATE_WAITING_FOR_HOST = 1;
const LOBBY_STATE_WAITING_FOR_GAME_START = 2;
const LOBBY_STATE_IN_GAME = 3;

const GAME_STATE_WAITING_FOR_ENOUGH_PLAYERS = 1;
const GAME_STATE_PLAYING = 2;
const GAME_STATE_END = 3;

const TURN_STATE_DRAW = 1;
const TURN_STATE_SUBMISSION = 2;
const TURN_STATE_JUDGING = 3;
const TURN_STATE_RESULTS = 4;

function load_player_hand() {
    $('.hand_area').load('/hand', function (data) {
        var hand_banner = $('.hand_banner');
        var slidey = hand_banner.unslider({
            dots: true,
            complete: function (el) {
                if (slider_data) {
                    slider_data.items.removeClass('active');
                    $(slider_data.items[slider_data.current]).addClass('active');
                    white_card_id = el.find('.active').children("div").attr("id");
                }
            }
        });
        var slider_data = slidey.data('unslider');
        if (slider_data) {
            slider_data.items.removeClass('active');
            $(slider_data.items[slider_data.current]).addClass('active');
            white_card_id = slidey.find('.active').children("div").attr("id");
        }
    });
}

function get_current_player_count(){
     $.get('/player_count', function(data) {
         player_count = data['player_count'];
         var player_count_header = $('#player_count_header');
         console.log("Player count == " + player_count);
         player_count_header.text('Players: ' + player_count);
     });
}

window.onload = function() {
    $.when( $.get('/user'), $.get('/lobby_state')).then(
        function(d1,d2) {
            username = d1[0].name;
            user_id = d1[0].id;
            lobby_state = d2[0].lobby_state;
        if (window.location.pathname != '/host') {
            load_player_hand();
        } else {
            // HOST pregame flow
            user_is_host = true;
            $('#hand_header').hide();
            $('.hand_banner').hide();
            $("#submit_white_card_button").hide();
            $.get("/address", function (data) {
                    console.log(data);
                    if (lobby_state == LOBBY_STATE_WAITING_FOR_GAME_START) {
                        console.log('host requested server address for display');
                        var join_header = $('#join_header');
                        var address = data.split("or ")[1];
                        join_header.append('<a href="' + address + '" target="_blank">Go to ' + data +
                        ' now!');
                        join_header.show();
                        user_id = '0000';
                        username = 'HOST';
                    }
            }).then(function () {
                get_current_player_count();
            });
        }
        get_czar();
        //get_current_player_count();
    });

};

function get_czar(){
    $.get("/czar", function (data) {
        var czar_header = $('#current_czar_header');
        var json_resp = data;
        console.log('Czar: ' + data);
        if (json_resp['czar_chosen'] == true){
            czar_header.show();
            czar_header.text('Czar: ' + json_resp['czar']);
            czar_header.after('<span>' + json_resp['current_black_card_text'] + '</span>');
        }
        else{
            czar_header.hide();
        }
    });
}

$(document).ready(function(){
    console.log("document actually ready");
    namespace = '/ws'; // change to an empty string to use the global namespace
    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);
    socket.on('connect', function() {
        console.log('sending client message');
        socket.emit(
            'user_connected',
            data = { type: 'client_connect',
                     user_id: user_id,
                     user: username
                     }
        );
        return false;
    });

    socket.on('player_connected', function (data) {
       // On player connected
        console.log('username: '+ data['username']);
        console.log('player_count: '+ data['player_count']);
        get_current_player_count();
    });

    socket.on('game_ready', function(msg) {
        // Show the 'Start Game' button when enough players
    });

    socket.on('no_host', function(event) {
        // Show 'Please wait for the game to be hosted' message
        document.cookie = 'username=; path=/; domain='+document.domain+'; expires=' + new Date(0).toUTCString();
    });

    socket.on('czar_chosen', function(event){
       // When server says czar is chosen, show this on the clients.
        get_czar();
    });

    $("#submit_white_card_button").click(function(){
        // need to handle case where white_card_id isn't set on load.
        socket.emit("user_submit_white_card",
                   { user_id: user_id,
                     user: username,
                     submitted_white_card_id: white_card_id
                   });
    });

});
