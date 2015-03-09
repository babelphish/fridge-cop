function Container(config)
{
	var that = this;
	that.zones = {};
	that.magnets = {};
	that.state = "hidden";
}

Container.STATES = {
	HIDDEN: 1
}

Container.prototype.render = function()
{
	$(this.zones).each(function()
	{
		this.render();
	});


	$(this.magnets).each(function()
	{
	
	})
}

Container.prototype.configure = function(element, options)
{
	var that = this;
	$.each(option.zones, function(index, zoneConfig)
	{
		that.zones.push(new Zone(zoneConfig))
	});
}

Container.prototype.getZoneById = function(id)
{
	return this.zones[id];
}

Container.prototype.addMagnet = function(magnet, zoneId)
{
	if (zone >= this.zones.length)
	{
		throw("Can't add a magnet to a zone that doesn't exist!");
	}
	
	this.zones[zone].add(magnet, x, y);
}

function Zone(config)
{
	this.zoneMagnets = [];
}

Zone.prototype.placedMagnets = function()
{
//	return this.
}

Zone.prototype.add = function(magnet)
{
	
	this.zoneMagnets
}

Zone.prototype.firstOpenSpace = function()
{

}