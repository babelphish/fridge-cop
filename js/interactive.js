
$(function()
{
	var grabbing = false;
	var timeGrabbed = null;
	
	var ticker = null;
		
	var objects = [];
	var currentVector = 10;
	var frictionAmount = .9;
	var minimumSpeed = 0.01;

	var stage = new Stage($("body"));

	stage.addObject(new Refrigerator(), 0);
	
	$(window).on("resize", function()
	{
		stage.setWidth($(this).width());
		stage.updateAllPositions();
	}).trigger("resize");
	
	ticker = setInterval(function()
	{
		//stage.update();
	}, 25);

});

function Stage(element)
{
	var that = this; 
	that.mainElement = element;
	that.objects = {};
	that.setOffset(0);
	
	element.css("overflow", "hidden");
	element.addClass("stage");
	element.append( $("<div/>", {
		"class" : "stage-cover"
	}))
	
	$(element).on("resize", function()
	{
		that.width = $(element.width);
	});

	var grabbing = false;
	var originalX = null;
	
	that.mainElement.find(".stage-cover").on("mousedown", function(e)
	{
		grabbing = true;
		originalX = e.pageX;
	}).on("mousemove", function(e)
	{
		if (grabbing)
		{
			var offsetX = e.pageX;			
			if (offsetX != stage.getOffset())
			{
				stage.setOffset(offsetX);
				stage.updateAllPositions();
			}
		}
	}).on("mouseup", function()
	{
		grabbing = false;
	}).on("mouseout", function()
	{
		grabbing = false;
	});
}

Stage.prototype.update = function()
{
	var frictionAmount = 0.95;
	
	$.each(this.objects, function(index, object)
	{
		var currentVector = applyFriction(currentVector, frictionAmount);
		object.applyVector(currentVector);
		object.render();
	});
}

Stage.prototype.getWidth = function()
{
	return this.width;
}

Stage.prototype.addObject = function(object, offset)
{
	object.setStage(this);
	object.setOffset(offset);
	
	this.mainElement.append(object.element);
	object.init();
	object.element.css("width", object.getWidth());
	object.element.css("height", object.getHeight());
	
	if (!this.nextObjectId)
	{
		this.nextObjectId = 1;
	}

	var id = this.nextObjectId;
	this.objects[id] = object;

	this.nextObjectId++;
	return id;
}

Stage.prototype.centerX = function()
{
	return this.getWidth() / 2;
}

Stage.prototype.setWidth = function(width)
{
	this.width = width;
	this.halfWidth = width / 2; //don't want to calculate 
	this.updateAllPositions();
}

Stage.prototype.objectTop = function(object)
{
//	return this.height() 
}

Stage.prototype.getHalfWidth = function()
{
	return this.halfWidth;
}

Stage.prototype.updateAllPositions = function()
{
	$.each(this.objects, function(index, object) {
		object.updatePosition();
	});
}

Stage.prototype.setOffset = function(offset)
{
	this.offset = offset;
}

Stage.prototype.getOffset = function()
{
	return this.offset;
}

function applyFriction(vector, frictionAmount)
{
	return vector * frictionAmount;
}

function calcVelocity(oldPos, newPos, oldTime, newTime)
{
	return (newX - oldX) / (newTime - oldtime)
}

function StageObject()
{
	this.element = $("<div></div>",
	{
		"class" : "stage-object"
	});
}

StageObject.prototype.setOffset = function(offset)
{
	this.offset = offset;
}

StageObject.prototype.updatePosition = function()
{
	var left = (this.stage.getHalfWidth() - this.getHalfWidth()) + this.stage.getOffset() + this.offset;
	this.element.css("left", left);
}

StageObject.prototype.getHalfWidth = function()
{
	return this.getWidth() / 2;
}

StageObject.prototype.setStage = function(stage)
{
	this.stage = stage;
}

function Refrigerator()
{

}

Refrigerator.prototype = new StageObject();
Refrigerator.prototype.constructor = Refrigerator;

Refrigerator.prototype.getHeight = function()
{
	return 300;
}

Refrigerator.prototype.getWidth = function()
{
	return 120;
}

Refrigerator.prototype.init = function()
{
	this.element.css("border", "1px solid black");
}