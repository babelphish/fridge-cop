var timer = null;
var currentState = null;
var receivedStates = [];

$(function()
{	
	preload([
		'/images/fridge_closed2.png',
		'/images/fridge_open2.png',
		'/images/rabbit.png',
		'/images/snail.png'
	]);
	
	if (channelData) //then it's channel time baby
	{
		startListeningChannel(channelData.token);
	}
	else //start polling
	{
		updateFridgeStatus(); //do initial update
		timer = setInterval(updateFridgeStatus, delaySeconds * 1000); //start polling
	}
	
	$("#fridgeClickOverlay").on("click", function()
	{
		if (userLoggedIn())
		{
			if ($(this).hasClass("fridgeStateOpen"))
			{
				$.get("/fridge_click").done(function(result) 
				{
					result = JSON.parse(result)
					if (result.error)
					{
						alert(result.errorMessage);
					}
				}).fail(function()
				{
					alert('Click failed! :(');
				})
			}
		}
		else
		{
			//let the person know they need to be logged in
		}
	})
	
	$("#lastOpenedOverlay").qtip({
		style: 
		{
			classes: 'qtip-bootstrap',
			width: 150, // Overrides width set by CSS (but no max-width!)
		},
		content: 
		{
            text: "This is the last time the fridge was open."
        },
		position: 
		{
			my: "center left",
			at: "center right"
		}
	});
	
	$("#fridgeClickOverlay").qtip({
		style: 
		{
			classes: 'qtip-bootstrap',
			width: 150
		},
		content:
		{
            text: function()
			{
				if (currentState == "fridgeStateClosed")
				{
					return "The fridge is closed right now."
				}
				else if (currentState == "fridgeStateOpen")
				{
					return "The fridge is open."
				}
			}
        },
		position: 
		{
			my: "center left",
			at: "center right"
		}
	})
	
})

var updateInProgress = false;
function updateFridgeStatus()
{
	$.get("/delayed_states").done(function(delayedStateSerialized) 
	{
		var delayedStateData = JSON.parse(delayedStateSerialized)
		appendStateData(delayedStateData);
	}).always(function() {
		updateInProgress = false;
	})
}

function appendStateData(stateDataList)
{
	if (stateDataList.states.length == 0)
		return;
	
	$.each(stateDataList.states, function(index, stateData)
	{
		var stateData = new StateData(stateData)
		doInsert = true;
		index = receivedStates.length - 1;
		while ((index >= 0) && (receivedStates[index].timeDiff(stateData) > 0))
		{
			index--;
		}
		while ((index >= 0) && (receivedStates[index].timeDiff(stateData) == 0))
		{
			if (receivedStates[index].equals(stateData))
			{
				doInsert = false;
				break;
			}
		}
		if (doInsert) //not a duplicate
		{
			receivedStates.splice(index + 1, 0, stateData);
		}
	})
	
	processStates()
}

var stateChangeTimer = null

//this function waits the appropriate amount of time for a delayed state change
function processStates()
{
	if(receivedStates.length == 0)
		return;
	
	//this is the current delayed time
	adjustedTime = calculateDelayedTime(delaySeconds, offsetMilliseconds)
	
	var index = 0;
	var nextStateChange = null;
	while (index < receivedStates.length)
	{
		var stateTime = receivedStates[index].getChangeTime();
		if (adjustedTime.diff(stateTime) < 0)
		{
			nextStateChange = receivedStates[index];
			break;
		}
		index++;
	}
	
	if (nextStateChange == null) //find that last state and set it to that
	{
		receivedStates[receivedStates.length - 1].apply()
	}
	else //we wait for the next state change
	{
		window.clearTimeout(stateChangeTimer)
		stateChangeTimer = setTimeout(function() 
		{ 
			nextStateChange.apply();
			processStates();
		}, nextStateChange.getChangeTime().diff(adjustedTime))
	}
}

function calculateDelayedTime(delaySeconds, offsetMilliseconds)
{
	return (moment().subtract(offsetMilliseconds).subtract(delaySeconds * 2 * 1000))
}

function preload(arrayOfImages) {
	$("body").append('<div id="imagePreloadArea" style="width: 0px; height: 0px; position: absolute;">');
	$(arrayOfImages).each(function(index, imageLocation){
		$("#imagePreloadArea").append('<img style="width:0px; height:0px" src="' + imageLocation + '"/>');
	});
}

function startListeningChannel(token)
{
	var channel = new goog.appengine.Channel(token);
	var socket = channel.open();
	socket.onopen = function() {  };
	socket.onmessage = function(e) 
	{
		var data = JSON.parse(e.data);
		appendStateData(data)
		processStates();
	};
	socket.onerror = function(e) 
	{
		$.get("/request_new_channel").done(function(newChannelData)
		{
			newChannelData = JSON.parse(newChannelData);
			setTimeout(function() {startListeningChannel(newChannelData.token) }, 5000)
		})
	}
	socket.onclose = function(e) 
	{ 
		//alert('close!') 
	};
}

function userLoggedIn()
{
	return (channelData != null)
}

function StateData(stateData)
{
	var that = this;
	that.stateType = stateData.type;
	that.eventTime = moment(stateData.t, serverDateFormat);
	that.lastState = stateData.ls;
	that.state = stateData.s;
	
	this.isFridgeData = function()
	{
		return (that.stateType == "fridge");
	}
	
	this.getChangeTime = function()
	{
		return that.eventTime;
	}
	
	this.getLastState = function()
	{
		return that.lastState;
	}
	
	this.getState = function()
	{
		return that.state;
	}
	
	this.getType = function()
	{
		return that.stateType;
	}
	
	this.equals = function(b)
	{
		var a = that;
		return ((a.getState() == b.getState()) && (a.getChangeTime().diff(b.getChangeTime()) == 0) && (a.getType() == b.getType()))
	}
	
	this.apply = function()
	{
		var fridgeStates = ["", "fridgeStateOpen", "fridgeStateClosed", "fridgeStateUnknown", "fridgeStateTransition"]
		var stateToApply = that.state;
		if (that.isFridgeData())
		{
			newState = "";
			if (stateToApply > 0 && stateToApply < fridgeStates.length)
			{
				newState = fridgeStates[stateToApply]
			}
			
			if (newState != currentState)
			{
				if ((newState != 'fridgeStateClosed') || !userLoggedIn())
					$("#fridgeWhiteboard").hide()
				else
					$("#fridgeWhiteboard").show()
				
				$("#fridgeStateContainer, #pollingSpeed, #lastOpenedTime").removeClass(currentState).addClass(newState);
				currentState = newState;

				updateLastOpenedTime(that.getChangeTime())
			}
		}
		
		function updateLastOpenedTime(lastOpenedDate)
		{
			$("#lastOpenedText").text(lastOpenedDate.format("hh:mm")).attr("title", lastOpenedDate.toString());
		}
	}
	
	this.timeDiff = function(otherState)
	{
		return that.getChangeTime().diff(otherState.getChangeTime())
	}
}