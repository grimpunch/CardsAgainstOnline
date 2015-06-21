

var ws;
var clientID;

function createChatEntry(username, message) {
var entry = document.createElement("div");
entry.class = "chat_entry";

var dom_uname = document.createElement("span");
dom_uname.class = "chat_username";
dom_uname.textContent = username+": ";
entry.appendChild(dom_uname);

var dom_msg = document.createElement("span");
dom_msg.class = "chat_message";
dom_msg.textContent = message;
entry.appendChild(dom_msg);
return entry;
}

function openChatWS(messageContainer) {
    var host = window.location.host;
    ws = new WebSocket("ws://"+ host +"/chat");

    ws.onmessage = function(e) {
      var data = JSON.parse(e.data);
        console.log(data.type);
        switch(data.type){
            case "chat_message":
              clientID = data.author;
              messageContainer.appendChild(createChatEntry(data.author, data.message));
              break;
            //case "username":
            //  text = "<b>User <em>" + msg.name + "</em> signed in at " + timeStr + "</b><br>";
            //  break;
            //case "message":
            //  text = "(" + timeStr + ") <b>" + msg.name + "</b>: " + msg.text + "<br>";
            //  break;
            //case "rejectusername":
            //  text = "<b>Your username has been set to <em>" + msg.name + "</em> because the name you chose is in use.</b><br>"
            //  break;
            case "client_list_update":
              var ul = "";
                var str = data.clients_list;
                str = str.replace('\'','');
                var res = str.split("[")[1].split(']')[0].split(',');

              for (i=0; i < res.length; i++) {
                ul += res[i].trim() + "<br>";
              }
              document.getElementById("userlistbox").innerHTML = ul;
              break;
            }
    };

    ws.onclose = function(e) {
      openChatWS(messageContainer);
    };
}

function sendMessage() {
var data = { type: 'chat_message',
             author: document.getElementById("username").value,
             message: document.getElementById("message").value };

if(data.author && data.message) {
  ws.send(JSON.stringify(data));
}
}

window.onload = function() {
var messageContainer = document.getElementById("chat");
if("WebSocket" in window) {
  messageContainer.appendChild(createChatEntry("[SYSTEM]", "WebSocket is supported by your browser!"));
  messageContainer.appendChild(createChatEntry("[SYSTEM]", "Pick a username and start sending out messages."));
  openChatWS(messageContainer);
}
else {
  messageContainer.appendChild(createChatEntry("[SYSTEM]", "WebSocket is NOT supported by your browser!"));
}

$('.hand_area').load('/hand');

$('#message').keyup(function(evt) {
  if ((evt.keyCode || evt.which) == 13) {
    sendMessage()
    $('#message').val('');
    return false;
  }
});
}
