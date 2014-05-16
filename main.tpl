<!DOCTYPE html>
<html>
	<head>
		<meta name="viewport" content="width=device-width, initial-scale=1" >
		<link rel="stylesheet" type="text/css" href="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.css"></link>
		<link rel="stylesheet" type="text/css" href="/css/timeline.css">		
		<link rel="stylesheet" type="text/css" href="./css/main.css?version=5"></link>
		<title>Fridge Cop</title>
	</head>

	<body>
		<div id="fridgeStateContainer" class="unselectable">
			<div id="lastOpenedTime" class="lastOpenedClockPosition digitalFont"><span id="lastOpenedText"></span></div>
			<div id="lastOpenedOverlay" class="lastOpenedClockPosition"></div><div id="lastOpenedToolTipText" style="display:none"></div>
			
			<div id="fridgeClickOverlay"></div>
			<div id="fridgeWhiteboard"><a href="{{user_url}}" id="whiteboardLink"></a></div>
			<div id="fridgeClickVerifying" class="startHidden">
			
			</div>
			<div id="statPopup"></div>
		</div>
		
		<div id="mytimeline"></div>

		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
		<script src="/js/moment.min.js"></script>
		<script src="/js/main.js"></script>
		<script src="//cdn.jsdelivr.net/qtip2/2.2.0/jquery.qtip.min.js"></script>
		<script type="text/javascript" src="http://www.google.com/jsapi"></script>
		<script type="text/javascript" src="/js/timeline.js"></script>
		<script src="//node.fridge-cop.com/socket.io/socket.io.js?version=5"></script>

		<script>
			var serverDateFormat = 'YYYY-MM-DD HH:mm:ss.SSS Z'
			var loggedIn = '{{logged_in}}' == 'True';
			var fridgePoints = {{fridge_points}}
			var currentState =({{!serialized_state}});

			function drawVisualization() 
			{
				// Create and populate a data table.
				var data = new google.visualization.DataTable();
				data.addColumn('datetime', 'start');
				data.addColumn('datetime', 'end');
				data.addColumn('string', 'content');

				data.addRows([
					[new Date(2010,7,23), , 'Conversation<br>' +
							'<img src="img/comments-icon.png" style="width:32px; height:32px;">'],
					[new Date(2010,7,23,23,0,0), , 'Mail from boss<br>' +
							'<img src="img/mail-icon.png" style="width:32px; height:32px;">'],
					[new Date(2010,7,24,16,0,0), , 'Report'],
					[new Date(2010,7,26), new Date(2010,8,2), 'Traject A'],
					[new Date(2010,7,28), , 'Memo<br>' +
							'<img src="img/notes-edit-icon.png" style="width:48px; height:48px;">'],
					[new Date(2010,7,29), , 'Phone call<br>' +
							'<img src="img/Hardware-Mobile-Phone-icon.png" style="width:32px; height:32px;">'],
					[new Date(2010,7,31), new Date(2010,8,3), 'Traject B'],
					[new Date(2010,8,4,12,0,0), , 'Report<br>' +
							'<img src="img/attachment-icon.png" style="width:32px; height:32px;">']
				]);

				// specify options
				var options = {
					"width":  "100%",
					"height": "200px",
					"style": "box"
				};

				// Instantiate our timeline object.
				timeline = new links.Timeline(document.getElementById('mytimeline'));

				// Draw our timeline with the created data and options
				timeline.draw(data, options);
			}
			
			 //google.load("visualization", "1");

			// Set callback to run when API is loaded
			google.setOnLoadCallback(drawVisualization);
			
		</script>

	</body>
</html>