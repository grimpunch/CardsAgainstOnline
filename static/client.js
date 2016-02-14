var ws;
var user;
var host = null;
var pregame;
var user_id;
var white_card_id;

window.onload = function() {
    $.when( $.get('/user'), $.get('/pregame')).then(
        function(d1,d2) {
            user = d1[0].name;
            user_id = d1[0].id;
            pregame = d2[0].pregame;
        if (window.location.pathname != '/host') {
            $('#judgement_header').hide();
            $('#submit_judged_card_button').hide();
            $('.hand_area').load('/hand', function(data) {
                var hand_banner = $('.hand_banner');
                var slidey = hand_banner.unslider({
                    dots: true,
                    complete: function(el) {
                        if(slider_data)
                        {
                            slider_data.items.removeClass('active');
                            $(slider_data.items[slider_data.current]).addClass('active');
                            white_card_id = el.find('.active').children("div").attr("id");
                        }
                    }
                });
                var slider_data = slidey.data('unslider');
                if(slider_data)
                {
                    slider_data.items.removeClass('active');
                    $(slider_data.items[slider_data.current]).addClass('active');
                    white_card_id = slidey.find('.active').children("div").attr("id");
                }
            });
        } else {
            host = true;
            $('#hand_header').hide();
            $('#judgement_header').hide();
            $('#submit_judged_card_button').hide();
            $("#submit_white_card_button").hide();
            $.get("/address", function (data) {
                    console.log(data);
                    if (pregame) {
                        console.log('callback called');
                        var join_header = $('#join_header');
                        var address = data.split("or ")[1];
                        join_header.append('<a href="' + address + '" target="_blank">Go to ' + data +
                        ' now!');
                        join_header.show();
                        user_id = '0000';
                        user = 'HOST';
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
        console.log(data);
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

function set_judgement_screen() {
    if (window.location.host == true) {
        $.get("/judgement", function (data) {
            var judgement_area = $('.judgement_area');
            judgement_area.load('/judgement');
        });
        $('#submit_judged_card_button').hide();
    }
    else {
        $('#submit_judged_card_button').hide();
        $('#submit_white_card_button').hide();
        $('#hand_header').hide();
        $('#hand_area').hide();
        $.get("/judgement", function (data) {
            var judgement_area = $('.judgement_area');
            judgement_area.load('/judgement');
        });
    }
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
                     user: user
                     }
        );
        return false;
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

    socket.on('show_waiting_for_cards', function(event){
       // Incomplete stub, requires showing a screen before all cards are submitted.
    });

    socket.on('show_judged_cards', function(event){
         // Show the cards being judged by the czar
            set_judgement_screen();
        }
    );

    $("#submit_white_card_button").click(function(){
        // need to handle case where white_card_id isn't set on load.
        socket.emit("user_submit_white_card",
                   { user_id: user_id,
                     user: user,
                     submitted_white_card_id: white_card_id
                   });
        set_judgement_screen();
    });

});
