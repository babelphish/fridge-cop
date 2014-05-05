<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" >
		<link rel="stylesheet" type="text/css" href="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.css"></link>
		<link rel="stylesheet" type="text/css" href="./css/main.css"></link>
		<title>Fridge Cop</title>
	</head>

	<body>
		<div id="fridgeStateContainer" class="fridgeStateUnknown unselectable">
			<div id="lastOpenedTime" class="lastOpenedClockPosition digitalFont"><span id="lastOpenedText"></span></div>
			<div id="lastOpenedOverlay" class="lastOpenedClockPosition"></div>
			<div id="fridgeClickOverlay"></div>
			<div id="fridgeClickToolTip" style="display:none"></div>

			<a id="pollingSpeed" href="{{user_url}}"  class="{{polling_state}}"></a>
			<div id="fridgeWhiteboard" class="startHidden">{{points}}</div>
			<div id="fridgeClickVerifying" class="startHidden">

			</div>
		</div>

		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<script src="/js/main.js"></script>
		<script src="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.js"></script>

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