<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" >
		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<link rel="stylesheet" type="text/css" href="./css/main.css"></link>
	</head>

	<body>
		<div id="fridgeStateContainer" class="{{fridge_state}}">
			<div id="lastOpenedTime" class="digitalFont {{fridge_state}}"><span id="lastOpenedText"></span></div>
			<a id="pollingSpeed" href="{{user_url}}"  class="{{polling_state}} {{fridge_state}}"></a>
			<div id="fridgeWhiteboard" style="{{'display:none' if (not logged_in) or (fridge_state != 'fridgeStateClosed') else '' }}"></div>
		</div>
		
		<script>
			var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
			var fridgeStates = ["", "fridgeStateOpen", "fridgeStateClosed", "fridgeStateUnknown", "fridgeStateTransition"]
			var currentState = "{{ fridge_state }}";
			var lastOpenedDate = moment('{{ last_opened_time }}', serverDateFormat)
			var userURL = '{{ user_url }}'
			var serverTime = moment('{{ server_time }}', serverDateFormat) //
			var delay_seconds = {{ delay_seconds }}
			var milliseconds_offset = moment().diff(serverTime)
						
			function updateFridgeState(stateNumber)
			{
				newState = "";
				if (stateNumber > 0 && stateNumber < fridgeStates.length)
				{
					newState = fridgeStates[stateNumber]
				}
				
				if (newState != currentState)
				{
					if (newState != 'fridgeStateClosed')
						$("#fridgeWhiteboard").hide()
					else
						$("#fridgeWhiteboard").show()
					
					$("#fridgeStateContainer, #pollingSpeed, #lastOpenedTime").removeClass(currentState).addClass(newState);
					currentState = newState;
				
					updateLastOpenedTime(moment())
				}
			}
		 
			var timer = null;
			var token = '{{channel_token}}'
			
			$(function()
			{
				preload([
					'/images/fridge_closed2.png',
					'/images/fridge_open2.png',
					'/images/rabbit.png',
					'/images/snail.png'
				]);

				updateLastOpenedTime(lastOpenedDate);
				
				if (token && token != '') //then it's channel time baby
				{
					startListeningChannel(token);
				}
				else //start polling
				{
					timer = setInterval(updateFridgeStatus, 1000);
				}
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
			
			function startListeningChannel(token)
			{
				var channel = new goog.appengine.Channel(token);
				var socket = channel.open();
				socket.onopen = function() {  };
				socket.onmessage = function(e) 
				{
					var data = JSON.parse(e.data);
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
		</script>
	</body>
</html>