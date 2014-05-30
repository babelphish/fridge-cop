function StateClient(global)
{
	var that = this;	
	var reconnect = false;
	var socket = null;

	that.init = function(socketURL, onConnect, onReconnect, onStateChange, onDisconnect)
	{
		socketURL += "state_changes";
		
		if (global.io && io) //otherwise we can't connect to our node :(
		{
			socket = io.connect(socketURL);

			socket.on('connect', function()
			{
				onConnect();
				if (reconnect) //then we disconnected, get the latest state again and it's party time
				{
					onReconnect();
					reconnect = false;
				}
			});
			
			socket.on('new_states', function (data)
			{
				onStateChange(data);
			});

			socket.on('disconnect', function()
			{
				onDisconnect();
				reconnect = true;
			});
		}
	}
}