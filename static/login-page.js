//$('#login-form').on('submit', function(e){
//      e.preventDefault();
//      var data={
//         userName:$('#username-input').val(),
//         password:$('#password-input').val()
//      };
//    var postData = data.serialize()
//    var loginForm = $("#login-form");
//    var postRequest = loginForm.attr("action");
//    $.post(postRequest, postData);
//});

$(document)
.on('click', '#host-button', function(){
    var loginForm = $("#login-form");
        loginForm.attr("action", "/host");
})
.on('click', '#login-button', function(){
    var loginForm = $("#login-form");
    loginForm.attr("action", "/add_player");
});