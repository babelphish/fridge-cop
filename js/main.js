var timer = null;
var currentState = null;
var receivedStates = [];

var IMAGE =
	{
		FRIDGE_CLOSED: 0,
		OPEN: 1,
		FAST_POLLING: 2,
		SLOW_POLLING: 3,
		SUCCESS: 4,
		FAILURE: 5
	}

var images = [
		'/images/fridge_closed2.png',
		'/images/fridge_open2.png',
		'/images/fridge_unknown.png',
		'/images/rabbit.png',
		'/images/snail.png',
		'/images/success.png',
		'/images/failure.png'
	]

var updateURL = 'http://node.fridge-cop.com/';
	
$(function()
{	
	preload(images);

	var spinner = new GameSpinner("fridgeClickVerifying");
	var endPoint = "state_changes";
	var reconnect = false;
	
	if (document.location.hostname == "localhost")
	{
		endPoint = "dev/" + endPoint;
	}
	var socket = io.connect(updateURL + endPoint);
	socket.on('connect', function()
	{
		if (reconnect) //then we disconnected, get the latest state again and it's party time
		{
		}
	});
	socket.on('new_states', function (data) 
	{
		processState(JSON.parse(data))
	});
	socket.on('disconnect', function()
	{
		reconnect = true;
		new StateData({ "s" : 3, "type" : "fridge" }).apply();
	});
	
	if (userLoggedIn())
	{
		$("#fridgeWhiteboard").text(points)
	}
	else
	{
		$("#fridgeWhiteboard").text("Log in")
	}
	
	$("#fridgeClickOverlay").on("click", function()
	{
		if (userLoggedIn() && fridgeIsOpen())
		{
			spinner.setText("Verifying Click...");
			spinner.setImage(IMAGE.FRIDGE_CLOSED);
			spinner.spin();
			spinner.show();
			$.get("/fridge_point_click").done(function(result)
			{
				result = JSON.parse(result)
				if (result.error)
				{
					spinner.setText(result.errorMessage);
					spinner.setImage(IMAGE.FAILURE);
				}
				else
				{
					spinner.setText("+1 FRIDGE POINTS YEAHHHH");
					spinner.setImage(IMAGE.SUCCESS);
					$("#fridgeWhiteboard").text(result.points);
				}
			}).fail(function()
			{
				spinner.setText('Click failed! :(');
				spinner.setImage(IMAGE.FAILURE);
			}).always(function()
			{
				spinner.stop();
			})
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
            text: $("#fridgeClickToolTip")
        },
		position: 
		{
			my: "center left",
			at: "center right"
		}
	})
	
	processState(currentState);
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

function getImage(imageIndex)
{
	return images[imageIndex];
}

var stateChangeTimer = null

//this function waits the appropriate amount of time for a delayed state change
function processState(state)
{	
	new StateData(state).apply();
}

function preload(arrayOfImages) {
	$("body").append('<div id="imagePreloadArea" style="width: 0px; height: 0px; position: absolute;">');
	$(arrayOfImages).each(function(index, imageLocation){
		$("#imagePreloadArea").append('<img style="width:0px; height:0px" src="' + imageLocation + '"/>');
	});
}

function fridgeIsOpen()
{
	return (currentState == "fridgeStateOpen");
}

function userLoggedIn()
{
	return (loggedIn)
}

function GameSpinner(id)
{
	var that = this;
	var spinner = $("#" + id)
	spinner.on("click", function() {
		that.hide();
	});

	init()
	
	//generate 
	function init()
	{
		spinner.addClass("spinContainer gradientBackground")
		spinner.html(
			'<p class="spinText">' +
			'</p>' +
			'<div class="spinImage"></div>'
		)
	}
	
	this.setText = function(text)
	{
		spinner.find(".spinText").text(text);
	}

	this.spin = function()
	{
		spinner.find(".spinImage").addClass("spinning")
	}

	this.stop = function()
	{
		spinner.find(".spinImage").removeClass("spinning")
	}
	
	this.setImage = function(imageURL)
	{
		spinner.find(".spinImage").css("background-image", 'url(' + getImage(imageURL) + ')')
	}
	
	this.show = function()
	{
		spinner.show();
	}
	
	this.hide = function()
	{
		spinner.hide();
	}
	
	this.fadeOut = function()
	{
		spinner.delay(5000).fadeOut({ "duration" : 3000});
	}
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
				if (newState == 'fridgeStateOpen')
				{
					if (userLoggedIn())
					{
						$("#fridgeClickToolTip").text("It's open! Click it for sweet fridge points!")
					}
					else
					{
						$("#fridgeClickToolTip").text("My fridge is open, but you aren't logged in.  Log in to earn fridge points.");
					}
				}
				else
				{
					$("#fridgeClickToolTip").html('My fridge.  Right now it\'s <span style="font-weight: bold">closed</span>.');
				}
			
				$("#fridgeStateContainer").removeClass(currentState).addClass(newState);
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