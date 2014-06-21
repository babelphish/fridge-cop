var fs = require('fs');
var clientFilePath = "../js/state_client.js";
var clientFileContents = fs.readFileSync(clientFilePath).toString();
var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
eval(clientFileContents);

var moment = require('moment')

var results = {};
var instances = 500;
var devUpdateURL = 'http://localhost:8081/state_changes';
//var devUpdateURL = 'http://node.fridge-cop.com/state_changes';

var io = require("socket.io-client");
var heartbeatMilliseconds = 5 * 1000;
var lastBroadcast = null;

function instantiateNew(instance)
{
	results[instance] = {};
	results[instance].startTryConnectTime = moment();
	var socket = io.connect(devUpdateURL, {"forceNew" : true});

	socket.on('connect', function()
	{
		results[instance].connectTime = moment();
		console.log("Instance " + instance + " connected.")
		socket.on('new_states', function (data)
		{
			if (instance == 1)
			{
				lastBroadcast = data;
			}
			results[instance].messageTime = moment();
		});

		socket.on('disconnect', function()
		{
		});
	});
}

function getInstance(i)
{
	return function()
	{
		instantiateNew(i);		
	}
}

for (var i = 0; i < instances; i++)
{		
	setTimeout(getInstance(i), parseInt((heartbeatMilliseconds / instances) * i));
}

var app = require("express")();
app.listen(8082, "127.0.0.1");
app.get("/dump", function(req, res)
{
	var output = "";
	var lastTime = moment(JSON.parse(lastBroadcast).t, serverDateFormat);
	var connectionTimes = [];
	var messageTimes = [];
	for (var i = 0; i < instances; i++)
	{
		messageTimes.push(results[i].messageTime)
		connectionTimes.push(results[i].connectTime.diff(results[i].startTryConnectTime))
	}
	connectionTimes.sort(function(a,b) 
	{
		return a - b;
	});
	messageTimes.sort(function(a,b)
	{
		return a.diff(b);
	});

	var min = messageTimes[0];
	var max = messageTimes[messageTimes.length - 1];
	
	var connectionTimesMean = 0;
	for (var i = 0; i < instances; i++)
	{
		connectionTimesMean += connectionTimes[i];
	}
	connectionTimesMean /= connectionTimes.length;

	var messageTimesMean = 0;
	for (var i = 0; i < instances; i++)
	{
		var difference = messageTimes[i].diff(min)
		messageTimesMean += difference;
	}
	messageTimesMean /= messageTimes.length

	output += "Mean time to connect: " + connectionTimesMean + " ms<br>";
	output += "Mean time to transmit message: " + messageTimesMean + " ms<br>";
	
	res.send(output)
});