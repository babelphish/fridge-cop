var timer = null;

$(function()
{
	preload([
		'/images/fridge_closed2.png',
		'/images/fridge_open2.png',
		'/images/rabbit.png',
		'/images/snail.png'
	]);
	
	if (token && token != '') //then it's channel time baby
	{
		startListeningChannel(token);
	}
	else //start polling
	{
		timer = setInterval(updateFridgeStatus, delaySeconds * 1000);
	}
})

var updateInProgress = false;
function updateFridgeStatus()
{
	if (!updateInProgress)
	{
		updateInProgress = true;
		$.get("/delayed_states").done(function(delayedStateSerialized) 
		{
			var delayedStateData = JSON.parse(delayedStateSerialized)
			appendStateData(delayedStateData.states);
		}).always(function() {
			updateInProgress = false;
		})
	}
}

function appendStateData(stateDataList)
{
	if (stateDataList.length == 0)
		return;
	
	$.each(stateDataList, function(index, stateData)
	{
		receivedStates.push(new StateData(stateData));
	})
	
	receivedStates.sort(function(a,b) 
	{
		return a.timeDiff(b)
	})
	
	processStates()
}

var stateChangeTimer = null

//this function waits the appropriate amount of time for a delayed state change
function waitForDelayedStateChange()
{
	if(receivedStates.length == 0)
		return;
	
	//this is the current delayed time
	adjustedTime = calculateDelayedTime(delaySeconds, offsetMilliseconds)
	
	var index = 0;
	var nextStateChange = null;
	var mostRecentStateChange = null;
	
	while (index < receivedStates.length)
	{
		var stateTime = receivedStates[index].getChangeTime();
		if (adjustedTime.unix() < stateTime.unix())
		{
			nextStateChange = receivedStates[index];
			break;
		}
		index++;
	}
	
	if (mostRecentStateChange != null) //we just make double sure that 
	{
		
	}
	
	if (nextStateChange != null) //then we have an upcoming state change
	{
		//make sure we cancel
	}
}

function calculateDelayedTime(delaySeconds, offsetMilliseconds)
{
	return (moment().subtract(offsetMilliseconds).subtract(delay_seconds * 1000))
}

function preload(arrayOfImages) {
	$(arrayOfImages).each(function(){
		$('<img/>')[0].src = this;
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
		receivedStates.push(new StateData(e.data))
		
		updateFridgeState(data.fridge.state)
	};
	socket.onerror = function(e) 
	{
		if (e.code == 401)
		{
			$.get("/request_channel").done(function(newChannel)
			{
				setTimeout(function() {startListeningChannel(newChannel) }, 5000)
			})
		}
		else
		{
			alert('unknown error')
		};
	}
	socket.onclose = function(e) 
	{ 
		//alert('close!') 
	};
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
		return (that.stateType == "fridge")
	}
	
	this.getChangeTime = function()
	{
		return that.eventTime
	}
	
	this.getLastState = function()
	{
		return that.lastState
	}
	
	this.state = function()
	{
		return that.state
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
				if (newState != 'fridgeStateClosed')
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