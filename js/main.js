google.load("visualization", "1"); //loads visualization
			
var timer = null;
var receivedStates = [];
var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
var updateURL = 'http://node.fridge-cop.com/';
var devUpdateURL = 'http://localhost:8081/';
var timeline = null;
var currentState = null;

vex.defaultOptions.className = 'vex-theme-default';

var images = [
		'/images/success.png',
		'/images/failure.png'
	]

$(function()
{
	processState(currentSerializedState);
	preload(images);
		
	var socketURL = updateURL;	
	if (document.location.hostname == "localhost")
	{
		socketURL = devUpdateURL;
	}
	
	new StateClient(window).init(socketURL, 
		function onReconnect()
		{
			$.get("/current_state").done(function(data)
			{
				new StateData(JSON.parse(data)).apply()
			})
		},
		function onStateChange(data)
		{
			processState(JSON.parse(data));
		},
		function onDisconnect()
		{
			setFridgeStateUnknown();
		}
	)
	
	//setup points
	if (userLoggedIn())
	{
		displayWhiteBoardPoints();
		var logoutContent = '<span class="accessText">Log Out</span>';
		$("#fridgeWhiteboard").on('mouseenter',  function() { $("#whiteboardLink").html(logoutContent) })
							  .on('mouseleave',  function() { displayWhiteBoardPoints() })
	}
	else
	{
		var loginContent = '<span class="accessText">Log In</span>'; 
		$("#whiteboardLink").html(loginContent); //default blank
	}
		
	attachEvents();	
})

function StateClient(global)
{
	var that = this;	
	var reconnect = false;
	var socket = null;

	that.init = function(socketURL, onReconnect, onStateChange, onDisconnect)
	{
		socketURL += "state_changes";
	
		if (global.io && io) //otherwise we can't connect to our node :(
		{			
			socket = io.connect(socketURL);
	
			socket.on('connect', function()
			{
				if (reconnect) //then we disconnected, get the latest state again and it's party time
				{
					onReconnect();
					reconnect = false;
				}
			});
			
			socket.on('new_states', function (data)
			{
				onStateChange(data);
			});
			
			socket.on('disconnect', function()
			{
				onDisconnect();
				reconnect = true;
			});
			

		}
	}
}

function displayWhiteBoardPoints()
{
	var pointsContent = function() { return '<span class="pointsText">' + fridgePoints + '</span>'};
	$("#whiteboardLink").html(pointsContent())
};

function attachEvents()
{
	var spinner = new GameSpinner("fridgeClickVerifying");

	$("#fridgeClickOverlay").on("click", function()
	{
		if (userLoggedIn() && fridgeIsOpen())
		{
			spinner.setText("Verifying Click...");
			spinner.setImage("./images/sprites/fridge_open.png");
			spinner.spin();
			spinner.show();
			$.get("/fridge_point_click").done(function(result)
			{
				result = JSON.parse(result)
				if (result.error)
				{
					spinner.setText(result.errorMessage);
					spinner.setImage("./images/failure.png");
				}
				else
				{
					spinner.setText("+1 FRIDGE POINTS YEAHHHH");
					spinner.setImage("./images/success.png");
					fridgePoints = result.points;
					displayWhiteBoardPoints();
				}
			}).fail(function()
			{
				spinner.setText('Click failed! :(');
				spinner.setImage("./images/failure.png");
			}).always(function()
			{
				spinner.stop();
			})
		}
	})
	
	$("#statPopupButton").on("click", function()
	{
		vex.dialog.open({
			message: '<div id="timeline" class="hidden">test</div>',
		  buttons: [
		  ],
		  callback: function(data) 
		  {
		  },
		  contentCSS :
		  {
			"width" : 700
		  },
		  css :
		  {
		  
		  }
		  
		});
		
		// Instantiate our timeline object.
		timeline = new links.Timeline(document.getElementById('timeline'));
		redrawTimeline(timeline);
	});
	
	$(window).resize(function() 
	{
		var timelineContent = $(".vex-content");
		var windowHeight = $(window).height();
		var contentHeight = timelineContent.height() + 30;
		var heightDifference = windowHeight - contentHeight;

		timelineContent.css("margin-top", parseInt(heightDifference / 2))
	
		if (timeline)
		{
			timeline.checkResize();
		}
	})
	
	$("#lastOpenedOverlay").qtip({
		style: 
		{
			classes: 'qtip-bootstrap',
			width: 150 // Overrides width set by CSS (but no max-width!)
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

timelineRequests = {};
var requestIndex = 0;

function redrawTimeline(timeline) 
{
	$.each(timelineRequests, function(index, request) 
	{
		request.abort();
	})

	requestIndex++;

	makeRequest(requestIndex);
	
	function makeRequest(requestIndex)
	{
	
		timelineRequests[requestIndex] = 
		$.get("/timeline_states")
		.done(
			function(timelineStates)
			{
				$("#timeline").show();

				renderTimeline(JSON.parse(timelineStates));
			})
		.always(
			function()
			{
				delete timelineRequests[requestIndex]
			})
	}
	
	function renderTimeline(timelineStates)
	{
		// Create and populate a data table.
		var data = new google.visualization.DataTable();
		data.addColumn('datetime', 'start');
		data.addColumn('datetime', 'end');
		data.addColumn('string', 'content');
		data.addColumn('string', 'type');
		data.addColumn('string', 'group');
		data.addColumn('string', 'className');	

		//construct timeline
		
		var lookingForFridgeState = 1;
		
		var statePair = {};
				
		$.each(timelineStates.data, function(index, state)
		{ 
			var state = new StateData(state);
			state.setTimeZone("America/New_York");
			if (state.isFridgeData())
			{
				if (!statePair.startState)
				{
					if (state.getState() == 1)
					{
						statePair.startState = state;
					}
				}
				else //we do have a start state, now we need an end state
				{
					if (state.getState() == 2)
					{
						//add the timeline elements

						var seconds = state.getChangeTime().diff(statePair.startState.getChangeTime(), "seconds");
						var eventText = seconds + " sec"
						if (seconds > 60)
						{
							eventText = parseInt(seconds / 60) + " min"
						}
						else if (seconds == 0)
						{
							eventText = "1 sec";
						}
						
						data.addRow([statePair.startState.getChangeTime().toDate(), , eventText, "box", "Open",""]);
						statePair = {};  //clear out pair
					}
				}
			}
		});
	
		// specify options
		var start = moment(timelineStates.start, serverDateFormat);
		var end = moment(timelineStates.end, serverDateFormat);
		
		var visibleStart = start.add("hours", -1);
		var visibleEnd = end.add("hours", 1);

		var initialStart = end.clone().add("hours", -12);
		var initialEnd = end.clone()
		
		var startDay = start.clone().hour(0).minute(0).second(0).millisecond(0)
		var endDay = end.clone().hour(0).minute(0).second(0).millisecond(0)

		var dayIndex = startDay.clone();
		while (endDay.diff(dayIndex) >= 0)
		{
			breakfastStart = dayIndex.clone().hour(6).minute(30);
			breakfastEnd = dayIndex.clone().hour(9);
			
			if ((breakfastStart.diff(start) > 0) && (end.diff(breakfastEnd) > 0))
			{
				data.addRow([breakfastStart.toDate(), breakfastEnd.toDate(), "Breakfast", "range", "Meals", "meal"]);
			}

			lunchStart = dayIndex.clone().hour(11).minute(30);
			lunchEnd = dayIndex.clone().hour(13).minute(30);
			
			if ((lunchStart.diff(start) > 0) && (end.diff(lunchEnd) > 0))
			{
				data.addRow([lunchStart.toDate(), lunchEnd.toDate(), "Lunch", "range", "Meals", "meal"]);
			}
			
			dinnerStart = dayIndex.clone().hour(18);
			dinnerEnd = dayIndex.clone().hour(20).minute(30);
			
			if ((dinnerStart.diff(start) > 0) && (end.diff(dinnerEnd) > 0))
			{
				data.addRow([dinnerStart.toDate(), dinnerEnd.toDate(), "Dinner", "range", "Meals", "meal"]);
			}

			dayIndex.add('days', 1);
		}

		var options = {
			"style": "box",
			"cluster" : true,
			"stackEvents" : true,
			"showMajorLabels" : false,
			"width" : "auto",
			"height" : "auto",
			"minHeight" : "250",
			"start" : initialStart.toDate(),
			"end" : initialEnd.toDate(),
			"min" : visibleStart.toDate(),
			"max" : visibleEnd.toDate()
		};
		
		// Draw our timeline with the created data and options
		timeline.setOptions(options);
		timeline.draw(data);
	}
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
	$("body").append('<div id="imagePreloadArea">');
	$(arrayOfImages).each(function(index, imageLocation){
		$("#imagePreloadArea").append('<img class="preloadedImage" src="' + imageLocation + '"/>');
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
		spinner.find(".spinImage").css("background-image", 'url(' + imageURL + ')')
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
	
	this.setTimeZone = function(zone)
	{
		that.eventTime.tz(zone);
	}
	
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