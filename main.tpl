<!DOCTYPE html>
<html>
	<head>
		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<link rel="stylesheet" type="text/css" href="./css/main.css"></link>
	</head>

	<body>
		<div id="fridgeStateContainer" class="{{fridge_state}}">
			<div id="lastOpenedTime" class="digitalFont {{fridge_state}}"><span id="lastOpenedText"></span></div>
		</div>
		
		 <script>

			var fridgeStates = ["", "fridgeStateOpen", "fridgeStateClosed", "fridgeStateUnknown", "fridgeStateTransition"]
			var currentState = "{{ fridge_state }}";
			var lastOpenedDate = new Date('{{ last_opened_time }} UTC')

			function updateFridgeState(stateNumber)
			{
				newState = "";
				if (stateNumber > 0 && stateNumber < fridgeStates.length)
				{
					newState = fridgeStates[stateNumber]
				}
				
				if (newState != currentState)
				{
					currentState = newState;
					$("#fridgeStateContainer").removeClass().addClass(newState);
					$("#lastOpenedTime").removeClass().addClass("digitalFont").addClass(newState);
					updateLastOpenedTime(new Date())
				}
			}
		 
			var timer = null;
			
			$(function()
			{
				updateLastOpenedTime(lastOpenedDate);
				timer = setInterval(updateFridgeStatus, 1000);
			})

			function updateLastOpenedTime(lastOpenedDate)
			{
				var hours = lastOpenedDate.getHours();
				if (hours > 12)
				{
					hours -= 12;
				}
				if ((hours + "").length == 1)
				{
					hours = "0" + hours;
				}
				var minutes = lastOpenedDate.getMinutes() + "";
				if (minutes.length == 1)
				{
					minutes = "0" + minutes;
				}
				
				$("#lastOpenedText").text(hours + ":" + minutes).attr("title", lastOpenedDate.toString());
			}
			
			var updateInProgress = false;
			function updateFridgeStatus()
			{
				if (!updateInProgress)
				{
					updateInProgress = true;
					$.get("/fridge_state").done(function(e) 
					{
						updateFridgeState(e)
					}).always(function() {
						updateInProgress = false;
					})
				}
			}
		 
			/*
			socket = channel.open();
			socket.onopen = function() { alert('open') };
			socket.onmessage = function(e) 
			{
				
			};
			socket.onerror = function() { alert('error') };
			socket.onclose = function() { alert('close!') };
			*/
		</script>
	</body>
</html>