
$(function()
{
	var containerManager = new ContainerManager();
	
	$(window).on("resize", function()
	{
		containerManager.resize();
	});

});