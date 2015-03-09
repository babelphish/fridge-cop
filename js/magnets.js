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
	var xValue = this.X();
	var yValue = this.Y();
	var result = 
	{
		x : xValue,
		y : yValue
	}
	return result
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