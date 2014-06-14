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
		function onConnect() {},
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
	
	var statsPopupContent = 
		'<ul class="nav nav-tabs">' +
			'<li class="active"><a href="#leaderboard-tab" data-toggle="tab">Top 10 Leaderboard</a></li>' +
			'<li id="timeline-button"><a href="#timeline-tab" data-toggle="tab">Timeline</a></li>' +
		'</ul>' +
		'<div class="tab-content">' +
			'<div class="tab-pane active" id="leaderboard-tab"><div id="leaderboard"></div></div>' +
			'<div class="tab-pane" id="timeline-tab"><div id="timeline"></div></div>' +
		'</div>'
	
	$("#statPopupButton").on("click", function()
	{
		vex.dialog.open({
			message: statsPopupContent,
		  showCloseButton : true,
		  buttons : [],
		  callback: function(data) {},
		  contentCSS :
		  {
			"width" : 700
		  },
		  css :{}
		});

		redrawTimeline();
		redrawLeaderboard();
	});
	
	$("body").on("click", "#timeline-button", function()
	{
		setTimeout(function() 
		{
			resizeTimeline();
		}, 100)
	});

	$("body").on("click", "#leaderboard tr.editable", function()
	{
		$(this).addClass("entry-mode");
		$(this).find("input").focus();
	});

	$("body").on("click", ".save-username-button", function()
	{
		var row = $(this).parents("tr.entry-mode");
		var newName = row.find(".name-entry input").val();
		updateVisibleUsername(newName);
	});
	
	$("body")
	.on("keyup", "input.username-input", function(e)
	{
		var currentString = $(this).val();
		var parent = $(this).parent();
		
		if (!currentString.match(visibleUserNamePattern))
		{
			parent.removeClass("has-success")
			parent.addClass("has-error")
		}
		else
		{			
			parent.removeClass("has-error")
			parent.addClass("has-success")
		}
	})
	.on("keypress", "input.username-input", function(e)
	{
        if (e.keyCode == 13) 
        {
        	var newName = $(this).val();
    		updateVisibleUsername(newName);        	
        	return false;
        }
	});
	
	$(window).resize(function() 
	{
		resizeTimeline();
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

function updateVisibleUsername(newName)
{
	$.post("/set_name", 
		  { "name" : newName })
	.done(function(data) 
	{ 
		if (data.error == false)
		{
			row.find(".name-text").text(newName);
			row.removeClass("entry-mode");
		}
	})	
}

function resizeTimeline()
{	
	if (timeline)
	{
		timeline.checkResize();
		timeline.checkResize();
	}
	
}

var timelineRequests = {};
var requestIndex = 0;

var leaderboardRequests = {};
var leaderboardRequestIndex = 0;


function redrawLeaderboard()
{
	$.each(leaderboardRequests, function(index, request) 
	{
		request.abort();
	});
	leaderboardRequestIndex++;

	makeRequest(leaderboardRequestIndex);
	
	function makeRequest(leaderboardRequestIndex)
	{
	
		leaderboardRequests[leaderboardRequestIndex] = 
		$.get("/point_ranks")
		.done(
			function(data)
			{
				data = JSON.parse(data);
				if (data.error == false)
				{
				
				}
				renderLeaderboard(data.ranks, data.startRank);
				
			})
		.always(
			function()
			{
				delete leaderboardRequests[leaderboardRequestIndex]
			})
	}
	
	function renderLeaderboard(ranks, startRank)
	{		
		var table = $('<table class="table table-striped table-hover"><thead><tr>' +
					  '<th class="rank-column">Rank</th>' +
					  '<th class="star-column">&nbsp;</th>' +
					  '<th>Name</th>' +
					  '<th class="points-column">Points</th>' +
					  '</tr></thead><tbody></tbody></table>')
		var interior = table.find("tbody")

		$(ranks).each(function(index, rank)
		{
			var glyph = "";
			var editButton = "";
			var noNameEntered = (rank.n == 'Anonymous FridgeClicker');
			var name = '<span class="name-text">' + rank.n + '</span>';

			var nameEntry =
			'<div class="name-entry">' +
				'<div class="input-group">' +
					'<input type="text" class="form-control username-input" placeholder="Enter your username" maxlength="' + maxVisibleUserNameLength + '">' +
					'<span class="input-group-btn">' +
						'<button class="btn btn-default save-username-button" type="button">Save!</button>' +
					'</span>' +
				'</div>' +
			'</div>';

			if (rank.s)
			{
				name += nameEntry; //add the possibility to set a username
				glyph = '<span class="glyphicon glyphicon-star"></span>';
			}
			row = $('<tr><td>' + (index + startRank) + '</td>' +
				'<td>' + glyph + '</td>' + 
				'<td>' + name + '</td>' +
				'<td>' + rank.p  + '</td></tr>').appendTo(interior);
			if (rank.s && noNameEntered)
				row.addClass('entry-mode');
				
			if (rank.s)
				row.addClass('editable');
		});

		table.appendTo("#leaderboard");
	}
}

function redrawTimeline() 
{
	// Instantiate our timeline object.
	timeline = new links.Timeline(document.getElementById('timeline'));

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
			"minHeight" : 250,
			"groupMinHeight" : 20,
			"start" : initialStart.toDate(),
			"end" : initialEnd.toDate(),
			"min" : visibleStart.toDate(),
			"max" : visibleEnd.toDate()
		};
		
		// Draw our timeline with the created data and options
		timeline.setOptions(options);
//		links.events.addListener(timeline, 'rangechange', fitToWindow);
		timeline.draw(data);
		resizeTimeline();
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