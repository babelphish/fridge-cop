<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=365, initial-scale=1" >
		{{!style_tags}}
		<title>Fridge Cop</title>
	</head>

	<body>
		<div id="fridgeStateContainer" class="unselectable {{fridge_state}}">
			<div id="lastOpenedTime" class="lastOpenedClockPosition digitalFont"><span id="lastOpenedText">00:00</span></div>
			<div id="lastOpenedOverlay" class="lastOpenedClockPosition"></div><div id="lastOpenedToolTipText" class="hidden"></div>

			<div id="fridgeClickOverlay"></div>
			<div id="fridgeWhiteboard" class="whiteboardText"><a href="{{user_url}}" id="whiteboardLink" ></a></div>
			<div id="statPopupButton"></div>
			<div id="fridgeClickVerifying" class="hidden">

			</div>
		</div>
		{{!script_tags}}
	</body>
</html>