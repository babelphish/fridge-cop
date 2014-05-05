<html>
<body>
		<script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/json2/20130526/json2.min.js"></script>
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>

		<script>
			$(function() 
			{
				var getList = [];
				var highPoints = 0;
				var processed = 0;
				
				for( var i = 0; i < 100; i++)
				{
					var getResult = $.get("/fridge_point_click?i=" + i);
					getList.push(getResult)
					getResult.done(function(result)
					{
						var points = JSON.parse(result).points;
						if (points > highPoints)
							highPoints = points;
							
						processed++;
					})
				}
				
				$.when.apply($, getList).then(function(result, test) {
					console.log('High Points: ' + highPoints + ' Processed: ' + processed);
				})
				
			})
		</script>
</body>
</html>