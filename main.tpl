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
		<div id="fridgeStateContainer" class="fridgeStateUnknown">
			<div id="lastOpenedTime" class="digitalFont fridgeStateUnknown"><span id="lastOpenedText"></span></div>
			<a id="pollingSpeed" href="{{user_url}}"  class="{{polling_state}} fridgeStateUnknown"></a>
			<div id="fridgeWhiteboard" style="display:none"></div>
		</div>
		
		<script>
			var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
			var userURL = '{{user_url}}';
			var serverTime = moment('{{server_time}}', serverDateFormat);
			var delaySeconds = {{ delay_seconds }};
			var channelData = {{!channel_data}};
			var offsetMilliseconds = moment().diff(serverTime);
			appendStateData({{!serialized_states}});
			
		</script>
	</body>
</html>