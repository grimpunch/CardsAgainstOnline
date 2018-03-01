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

var hand_slider = null;

function load_player_hand() {
    $('.hand_area').load('/hand', function(data) {
        $(function() {
            var hand_banner = $('.hand_banner');

            var firstChild = $(".hand_banner li:first-child").clone(),
                lastChild = $(".hand_banner li:last-child").clone(),
                container = $(".hand_banner ul");

            firstChild.appendTo(container);
            lastChild.prependTo(container);
            hand_slider = hand_banner;
            hand_banner.dragend({
                pageClass: "hand_card",
                direction: "horizontal",
                duration: 120,
                onSwipeEnd: function() {
                    var first = this.pages[0],
                        last = this.pages[this.pages.length - 1];

                    if (first === this.activeElement) {
                        this.jumpToPage(this.pages.length - 1);
                    }

                    if (last === this.activeElement) {
                        this.jumpToPage(2);
                    }

                    white_card_id = this.activeElement.childNodes[0].id;
                },
                afterInitialize: function() {
                    this.container.style.visibility = "visible";
                    white_card_id = this.activeElement.childNodes[0].id;
                }
            });
        });
    });
}

function get_current_player_count() {
    $.get('/player_count', function(data) {
        player_count = data['player_count'];
        var player_count_header = $('#player_count_header');
        console.log("Player count == " + player_count);
        player_count_header.text('Players: ' + player_count);
    });
}

function set_current_player_count(players) {
    player_count = players;
    console.log('players ' + player_count);
    var player_count_header = $('#player_count_header');
    player_count_header.text('Players: ' + player_count);
}

var client_init = function(callback_func) {
    $.when($.get('/user'), $.get('/lobby_state')).then(
        function(d1, d2) {
            username = d1[0].name;
            user_id = d1[0].id;
            lobby_state = d2[0].lobby_state;
            if (window.location.pathname != '/host') {
                load_player_hand();
                callback_func();
            } else {
                // HOST pregame flow
                user_is_host = true;
                $('#hand_header').hide();
                $('.hand_banner').hide();
                $("#submit_white_card_button").hide();
                $.get("/address", function(data) {
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
                }).then(function() {
                    get_current_player_count();
                    callback_func();
                });
            }
            get_czar();
        });
};

function get_czar() {
    $.get("/czar", function(data) {
        var czar_header = $('#current_czar_header');
        var json_resp = data;
        console.log('Czar: ' + data);
        if (json_resp['czar_chosen'] == true) {
            czar_header.show();
            czar_header.text('Czar: ' + json_resp['czar']);
            czar_header.after('<span>' + json_resp['current_black_card_text'] + '</span>');
        } else {
            czar_header.hide();
        }
    });
}

function delete_cookie(name) {
    document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function checkCookie() {
    if (document.cookie == false) {
        console.log("alive");
    } else if (document.cookie.indexOf("killswitch") >= 0) {
        delete_cookie("killswitch");
        window.location.href = "/";
    }
}

var checkKillSwitch = setInterval(checkCookie, 2000);

$(document).ready(function() {
    console.log("client ready to connect");
    checkCookie();
    namespace = '/ws'; // change to an empty string to use the global namespace
    // the socket.io documentation recommends sending an explicit package upon connection
    // this is specially important when using the global namespace
    var server = io.connect('http://' + document.domain + ':' + location.port + namespace);
    server.on('connect', function() {
        checkCookie();
        console.log('a client connected to the server');
        client_init(function() {
            console.log(username + ' initialised');
            server.emit('user_connected', {
                type: 'client_connect',
                user_id: user_id,
                user: username
            });
        });
    });

    server.on('player_connected', function(data) {
        // On player connected
        console.log('username: ' + data['username']);
        console.log('player_count: ' + data['player_count']);
        set_current_player_count(data['player_count']);
    });

    server.on('game_ready', function(msg) {
        // Show the 'Start Game' button when enough players
    });

    //server.on('no_host', function(event) {
    //    // Show 'Please wait for the game to be hosted' message
    //    document.cookie = 'username=; path=/; domain='+document.domain+'; expires=' + new Date(0).toUTCString();
    //});

    server.on('czar_chosen', function(event) {
        // When server says czar is chosen, show this on the clients.
        get_czar();
    });

    server.on('redirect', function(destination) {
        window.location.href = destination;
    });

    $("#submit_white_card_button").click(function() {
        // need to handle case where white_card_id isn't set on load.
        server.emit("user_submit_white_card", {
            user_id: user_id,
            user: username,
            submitted_white_card_id: white_card_id
        });
        var sel = '#'+white_card_id;
        $(sel)[0].className += " submit-anim";
        setTimeout(function(){
            $('.hand_banner').dragend("left");
        }, 800);
    });
});