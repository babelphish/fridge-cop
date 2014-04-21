<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" >
		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<script src="/js/main.js"></script>
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
			var serializedStates = "{{ serialized_states }}";
			var userURL = '{{ user_url }}'
			var serverTime = moment('{{ server_time }}', serverDateFormat) //
			var delaySeconds = {{ delay_seconds }};
			var token = '{{channel_token}}'
			var offsetMilliseconds = moment().diff(serverTime)
		</script>
	</body>
</html>