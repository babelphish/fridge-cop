<!DOCTYPE html>
<html>
	<head>
		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<link rel="stylesheet" type="text/css" href="./css/main.css"></link>
	</head>

	<body>
		<div id="fridgeStateContainer" class="{{fridge_state}}">
			<div id="lastOpenedTime" class="digitalFont {{fridge_state}}"><span id="lastOpenedText"></span></div>
			<div id="pollingSpeed" class="slowPolling {{fridge_state}}"></div>
		</div>
		
		 <script>

			var fridgeStates = ["", "fridgeStateOpen", "fridgeStateClosed", "fridgeStateUnknown", "fridgeStateTransition"]
			var currentState = "{{ fridge_state }}";
			var lastOpenedDate = moment('{{ last_opened_time }}', 'YYYY-MM-DD HH:mm:ss.SSS Z')

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
					updateLastOpenedTime(moment())
				}
			}
		 
			var timer = null;
			
			$(function()
			{
				preload([
					'/images/fridge_closed.png',
					'/images/fridge_open.png',
					'/images/rabbit.png',
					'/images/snail.png'
				]);

				updateLastOpenedTime(lastOpenedDate);
				timer = setInterval(updateFridgeStatus, 1000);
			})

			function updateLastOpenedTime(lastOpenedDate)
			{
				$("#lastOpenedText").text(lastOpenedDate.format("hh:mm")).attr("title", lastOpenedDate.toString());
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
			
			function preload(arrayOfImages) {
				$(arrayOfImages).each(function(){
					$('<img/>')[0].src = this;
				});
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