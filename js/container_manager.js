function ContainerManager()
{
	this.init($("body"), {});
}

ContainerManager.prototype.init = function(element, options)
{
	this.element = element;
	this.loadedContainers = {};
	this.loading = true;
	this.loaded = false;
	this.visibleContainer = null;
	this.height = options.height ? options.height : $(window).height();
	this.width = options.width ? options.width : $(window).width();
	
	this.render();
}

ContainerManager.prototype.resize = function(width, height)
{
	this.width = width;
	this.height = height;

	this.render();	
}

ContainerManager.prototype.render = function()
{
	this.element.css("border", "1px solid black");
}

ContainerManager.prototype.addContainer = function(id, config)
{
	if (loadedContainers)
	{
	
	
	}
	
	new Container(
	{
	
	
	})
}

ContainerManager.prototype.hasContainer = function(id, config)
{


}

ContainerManager.prototype.show = function(containerId)
{
	if (visibleContainer)
	{
	
	}

}