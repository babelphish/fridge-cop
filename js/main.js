var timer = null;
var currentState = null;
var receivedStates = [];
var io = null;

var IMAGE =
	{
		FRIDGE_CLOSED: 0,
		FRIDGE_OPEN: 1,
		FRIDGE_UNKNOWN : 2,
		FAST_POLLING: 3,
		SLOW_POLLING: 4,
		SUCCESS: 5,
		FAILURE: 6
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

	var endPoint = "state_changes";
	var reconnect = false;
	
	if (document.location.hostname == "localhost")
	{
		endPoint = "dev/" + endPoint;
	}
	
	if (io) //we can't connect to our node :(
	{
		var socket = io.connect(updateURL + endPoint);
		socket.on('connect', function()
		{
			if (reconnect) //then we disconnected, get the latest state again and it's party time
			{
				$.get("/current_state").done(function(data)
				{
					new StateData(JSON.parse(data)).apply()
				})
				reconnect = false;
			}
		});
		socket.on('new_states', function (data) 
		{
			processState(JSON.parse(data))
		});
		socket.on('disconnect', function()
		{
			setFridgeStateUnknown();
			reconnect = true;
		});
	}
	
	//setup points
	if (userLoggedIn())
	{	
		displayWhiteBoardPoints();
		var logoutContent = '<span class="accessText">Log Out</span>';
		$("#fridgeWhiteboard").on('mouseenter',  function() { $(this).html(logoutContent) })
							  .on('mouseleave',  function() { displayWhiteBoardPoints() })
	}
	else
	{
		var loginContent = '<span class="accessText">Log In</span>'; 
		$("#fridgeWhiteboard").html(loginContent); //default blank
	}
	
	attachEvents();
	
	processState(currentState);
})

function displayWhiteBoardPoints()
{
	var pointsContent = function() { return '<span class="pointsText">' + fridgePoints + '</span>'};
	$("#fridgeWhiteboard").html(pointsContent())
};

function attachEvents()
{
	$("#fridgeWhiteboard").on('click', function() { window.location = userURL  });


	var spinner = new GameSpinner("fridgeClickVerifying");

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
					fridgePoints = result.points;
					displayWhiteBoardPoints();
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
            text: $("#lastOpenedToolTipText")
        },
		position: 
		{
			my: "center left",
			at: "center right"
		}
	});
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

function setFridgeStateUnknown()
{
	new StateData({ "s" : 3, "type" : "fridge" }).apply();
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
				$("#fridgeStateContainer").removeClass(currentState).addClass(newState);
				currentState = newState;
				
				updateLastOpenedTime(that.getChangeTime())
			}
		}
		
		function updateLastOpenedTime(lastOpenedDate)
		{
			$("#lastOpenedToolTipText").html("Last opened <br><span class='toolTipTime'>" + lastOpenedDate.format("h:mm:ss A") + "</span>");
			$("#lastOpenedText").text(lastOpenedDate.format("hh:mm")).attr("title", lastOpenedDate.toString());
		}
	}
	
	this.timeDiff = function(otherState)
	{
		return that.getChangeTime().diff(otherState.getChangeTime())
	}
}