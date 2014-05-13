<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" >
		<link rel="stylesheet" type="text/css" href="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.css"></link>
		<link rel="stylesheet" type="text/css" href="./css/main.css"></link>
		<title>Fridge Cop</title>
	</head>

	<body>
		<div id="fridgeStateContainer" class="unselectable">
			<div id="lastOpenedTime" class="lastOpenedClockPosition digitalFont"><span id="lastOpenedText"></span></div>
			<div id="lastOpenedOverlay" class="lastOpenedClockPosition"></div><div id="lastOpenedToolTipText" style="display:none"></div>
			
			<div id="fridgeClickOverlay"></div>
			<a href="{{user_url}}" id="whiteboardLink"><div id="fridgeWhiteboard"></div></a>
			<div id="fridgeClickVerifying" class="startHidden">

			</div>
		</div>

		<script type="text/javascript" src="/_ah/channel/jsapi"></script>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<script src="/js/main.js"></script>
		<script src="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.js"></script>
		<script src="http://node.fridge-cop.com/socket.io/socket.io.js"></script>

		<script>
			var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
			var loggedIn = '{{logged_in}}' == 'True';
			var fridgePoints = {{fridge_points}}
			var currentState =({{!serialized_state}});
		</script>

	</body>
</html>