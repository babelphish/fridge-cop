var unit = 10;

function Magnet(config)
{
	if (!config)
		throw("Magnet needs a config!");

	if (!config.location)
		throw("Magnet needs a location!");
	
	if (config.location.x)
	{
		this.x = 0;
	}
	
	if (config.location.y)
	{
		this.y = 0;
	}
}

Magnet.prototype.getLocation = function()
{
	return
	{
		'x' : this.X(),
		'y' : this.Y()
	}
}

Magnet.prototype.render = function()
{


}

Magnet.prototype.X = function()
{
	return this.x;
}

Magnet.prototype.Y = function()
{
	return this.y;
}



Magnet.prototype.overlaps = function(magnet)
{
	this.getY()
	
	magnet.getY()
}