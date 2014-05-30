var fs = require('fs');
var clientFilePath = "../js/state_client.js";
var clientFileContents = fs.readFileSync(clientFilePath).toString();
eval(clientFileContents);

var devUpdateURL = 'http://localhost:8081/';
var io = require("socket.io-client");

var socketURL = devUpdateURL;

var clientId = 0;
function instantiateClient()
{
	clientId++;
	console.log("Instantiated client:" + clientId);
	new StateClient(global).init(socketURL, 
		function onConnect()
		{
			console.log('connect');
		},
		function onReconnect()
		{
			console.log('reconnect');
			/*
			$.get("/current_state").done(function(data)
			{
				new StateData(JSON.parse(data)).apply()
			})
			*/
		},
		function onStateChange(data)
		{
			console.log('state change');
			//processState(JSON.parse(data));
		},
		function onDisconnect()
		{
			console.log("disconnect");
			//setFridgeStateUnknown();
		}
	)
}

instantiateClient();

var app = require("express")();
app.listen(8082, "127.0.0.1");
app.get("/dump", function(req, res) {
  res.send("test");
});