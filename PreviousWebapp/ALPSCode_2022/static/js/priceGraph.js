// Class that holds the price graph information
function PriceGraph(){
	this.paddingTop = 40;
	this.paddingRight = 40;
	this.paddingBottom = 20;
	this.paddingLeft = 60;
	this.lineWidth = 1;
	this.legendWidth = 250;
	this.graph = d3.select("#graph");
	this.zoomLevel = 0;

	this.init = function(){
		this.parseDates();	
		this.calcDimensions();
		this.initAxes();
		this.initLines();
	//	this.initLegend();
		this.addHoverEffects();
	}

	// Convert each date string to a date object
	this.parseDates = function(){

		// Convert the date strings to Javascript date objects
		var dateParser = d3.time.format("%Y-%m-%dT%H:%M");
		for(var i = 0; i < pricingData.length; i++){
			pricingData[i].date = dateParser.parse(pricingData[i].datestr);		
		}

		// Sort the data by date
		pricingData.sort(function(d1, d2){
			return d1.date - d2.date;
		});
	}

	// Calculate the plot width and height of the plot
	this.calcDimensions = function(){	
		this.width = document.getElementById("price-graph").clientWidth 
			- (this.paddingLeft + this.paddingRight);
		this.height = document.getElementById("price-graph").clientHeight 
			- (this.paddingBottom + this.paddingTop);
	}

	this.initAxes = function(){
		// Scaling function for x values
		this.xScale = d3.time.scale()
			.domain([pricingData[0].date, pricingData[pricingData.length-1].date])
			.range([this.paddingLeft, this.width + this.paddingLeft]);

		// Scaling function for y values
		this.yScale = d3.scale.linear()
			.domain([0, d3.max(pricingData.map(function(d){
				return parseFloat(d.lmp);
			}))])
			.range([this.height, this.paddingTop]);

		// Set up the axis objects
		this.xAxis = d3.svg.axis()
			.scale(this.xScale)
			.tickFormat(d3.time.format("%b %d"));
		this.yAxis = d3.svg.axis()
			.scale(this.yScale)
			.orient("left");

		// Move the axes to their proper positions and graph them
		this.graph.append("svg:g")
			.attr("id", "xaxis")
			.attr("class", "axis")
			.attr("transform", "translate(0, " + this.height + ")")
			.call(this.xAxis);
		this.graph.append("svg:g")
			.attr("id", "yaxis")
			.attr("class", "axis")
			.attr("transform", "translate(" + this.paddingLeft + ", 0)")
			.call(this.yAxis);
	
		this.bisectDate = d3.bisector(function(d){
			return d.date;
		}).left;

		this.rescaleXAxis();
	}

	this.initLines = function(){
		// Define a clipping path to cut off overflow while zooming
		this.graph.append("svg:clipPath")
			.attr("id", "priceClip")
			.append("svg:rect")
			.attr("x", this.paddingLeft)
			.attr("y", this.paddingTop)
			.attr("width", this.width)
			.attr("height", this.height - this.paddingTop);

		// Function to convert price data to graph lines
		this.lineLMP = d3.svg.line()
			.x(function(d){ return this.xScale(d.date); })
			.y(function(d){ return this.yScale(d.lmp); });

		// Create the price data line
		this.graph.append("svg:path")
			.attr("id", "priceDataLine")
			.attr("d", this.lineLMP(pricingData))
			.attr("stroke", "#679451")
			.attr("stroke-width", this.lineWidth)
			.attr("fill", "none")
			.attr("clip-path", "url(#priceClip)");

		// Create the animation rectangle
		// Acts as a "curtain" to reveal the lines underneath
		this.graph.append("svg:rect")
			.attr("x", -1-(this.width + this.paddingLeft))
			.attr("y", 1-(this.height))
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("id", "animationCurtain")
			.attr("transform", "rotate(180)")
			.attr("shape-rendering", "optimizeSpeed")	
			.attr("fill", "#f6f4ee");

		// Specifies the animation that moves the aforementioned rectangle
		this.animation = d3.select("svg#graph").transition()
			.delay(0)
			.duration(1500);
		this.animation.select("svg rect#animationCurtain")
			.attr("width", 0);
	}

	this.initLegend = function(){
		// Add the legend container element
		this.legend = this.graph.append("svg:g")
			.attr("transform", "translate(" + (this.paddingLeft + (this.width / 2) - (this.legendWidth / 2)) + ", " 
					+ (this.height + this.paddingTop + 5) + ")")
			.attr("id", "priceGraphLegend");

		// Add the legend LMP line
		this.legend.append("svg:line")
			.attr("x1", 0)
			.attr("y1", 10)
			.attr("x2", 20)
			.attr("y2", 10)	
			.attr("stroke", "#679451")
			.attr("stroke-width", this.lineWidth)
			.attr("fill", "none");
		this.legend.append("svg:text")
			.text("LMP Price")
			.attr("x", 25)
			.attr("y", 15);

		// Add the legend forecasted line
		this.legend.append("svg:line")
			.attr("x1", 110)
			.attr("y1", 10)
			.attr("x2", 130)
			.attr("y2", 10)	
			.attr("stroke", "#81ae6c")
			.attr("stroke-width", this.lineWidth)
			.attr("fill", "none")
			.attr("stroke-dasharray", ("2, 2"));	
		this.legend.append("svg:text")
			.text("Forecasted Price")
			.attr("x", 135)
			.attr("y", 15);
	}

	this.addHoverEffects = function(){
		this.graph.append("svg:text")
			.attr("id", "mouseLabel")
			.attr("x", this.width + this.paddingLeft - 60)
			.attr("y", 25);

		// Add the mouse line
		this.graph.append("svg:line")
			.attr("id", "mouseLine")
			.attr("y1", this.paddingTop)
			.attr("y2", this.height)
			.attr("stroke", "#4f4f4f")
			.attr("stroke-width", 1)
			.attr("opacity", 0);
		this.graph.append("svg:circle")
			.attr("id", "mouseCircle")
			.attr("fill", "#679451")
			.attr("opacity", 0)
			.attr("r", 3.5);

		// Add a rectangle to detect mouse move events
		this.graph.append("svg:rect")
			.attr("id", "mouseListener")
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("x", this.paddingLeft)
			.attr("y", this.paddingTop)
			.attr("fill", "none")
			.attr("pointer-events", "all")

			// Show the frequency markers on hover
			.on("mouseover", function(){
				d3.select("#mouseLine")
					.attr("opacity", 1);
				d3.select("#mouseLabel")
					.attr("opacity", 1);
				d3.select("#mouseCircle")
					.attr("opacity", 1);
			})

			.on("mouseout", function(){
				d3.select("#mouseLine")
					.attr("opacity", 0);
				d3.select("#mouseLabel")
					.attr("opacity", 0);
				d3.select("#mouseCircle")
					.attr("opacity", 0);
			})

			// Move the mouse line to match the mouse X position
	        .on("mousemove", this.mouseMoveCallback);
	}
	
	this.mouseMoveCallback = function(){
		// Get the data point closest to the mouse's x-value
		var xVal = priceGraph.xScale.invert(d3.mouse(this)[0]);
		var i = priceGraph.bisectDate(pricingData, xVal, 1);
		var d;
		if(xVal - pricingData[i - 1].date > pricingData[i].date - xVal)
			d = pricingData[i];
		else
			d = pricingData[i-1];

		// Move the elements into position
		d3.select("#mouseLabel")
			.text(d3.time.format("%m/%d/%Y %H:%M - ")(d.date) + parseFloat(d.lmp).toFixed(2) + " $/MWh")
			.attr("x", priceGraph.width + priceGraph.paddingLeft - 200);
		d3.select("#mouseLine")
			.attr("x1", priceGraph.xScale(d.date))
			.attr("x2", priceGraph.xScale(d.date));
		d3.select("#mouseCircle")
			.attr("cx", priceGraph.xScale(d.date))
			.attr("cy", priceGraph.yScale(d.lmp));
	}

	
	this.setScaleHour = function(){
		this.zoomLevel = 2;
		
		// Update the axis scale
		if(pricingData.length <= 12)
			this.setScaleFull();
		else
			this.xScale.domain([pricingData[pricingData.length-1-12].date, pricingData[pricingData.length-1].date]);	
		
		this.xAxis.tickFormat(d3.time.format("%I:%M"));
		this.graph.select("svg g#xaxis")
			.transition().duration(300)
			.call(this.xAxis);
		
		// Redraw the lines
		this.graph.select("svg path#priceDataLine")
			.transition().duration(300)
			.attr("d", this.lineLMP(pricingData));
		
		// Reposition the mouse listener
		this.graph.select("svg rect#priceMouseListener")
			.on("mousemove", this.mouseMoveCallback);

		this.rescaleXAxis();
	}

	this.setScaleDay = function(){
		this.zoomLevel = 1;
		
		// Update the axis scale
		if(pricingData.length <= 288)
			this.setScaleFull();
		else
			this.xScale.domain([pricingData[pricingData.length-1-288].date, pricingData[pricingData.length-1].date]);

		this.xAxis.tickFormat(d3.time.format("%I:%M"));
		this.graph.select("svg g#xaxis")
			.transition().duration(300)
			.call(this.xAxis);

		// Redraw the lines
		this.graph.select("svg path#priceDataLine")
			.transition().duration(300)	
			.attr("d", this.lineLMP(pricingData));

		// Reposition the mouse listener
		this.graph.select("svg rect#priceMouseListener")
			.on("mousemove", this.mouseMoveCallback);
		
		this.rescaleXAxis();
	}

	this.setScaleFull = function(){
		this.zoomLevel = 0;
		
		// Update the axis scale
		this.xScale.domain([pricingData[0].date, pricingData[pricingData.length-1].date]);
		this.xAxis.tickFormat(d3.time.format("%b %d"));
		this.graph.select("svg g#xaxis")
			.transition().duration(300)
			.call(this.xAxis);

		// Redraw the lines
		this.graph.select("svg path#priceDataLine")
			.transition().duration(300)	
			.attr("d", this.lineLMP(pricingData));

		// Reposition the mouse listener
		this.graph.select("svg rect#priceMouseListener")
			.on("mousemove", this.mouseMoveCallback);

		this.rescaleXAxis();	
	}

	// Since D3 is stupid and we have to manually specify tick mark intervals,
	// this function sets them based on how much of the graph is shown and how
	// wide the graph is
	this.rescaleXAxis = function(){
		this.xScale.range([this.paddingLeft, this.width + this.paddingLeft]);
		this.xAxis.scale(this.xScale);

		if(this.zoomLevel == 0){
			if(pricingData.length > 210240){
				this.xAxis.ticks(d3.time.year, 1);
			}
			// More than 1 year's worth of information
			if(pricingData.length > 105120){
				this.xAxis.ticks(d3.time.month, 6);
			}
			else if(pricingData.length > 52560){
				this.xAxis.ticks(d3.time.month, 3);
			}
			// More than 1 month
			else if(pricingData.length > 8928){
				this.xAxis.ticks(d3.time.month, 1);
			}
			else{
				if(this.width < 300)
					this.xAxis.ticks(d3.time.day, 15);
				else if(this.width < 625)
					this.xAxis.ticks(d3.time.day, 5);
				else
					this.xAxis.ticks(d3.time.day, 2);
			}
		}
		else if(this.zoomLevel == 1){
			if(this.width < 300)
				this.xAxis.ticks(d3.time.hour, 8);
			else if(this.width < 625)
				this.xAxis.ticks(d3.time.hour, 6);
			else
				this.xAxis.ticks(d3.time.hour, 2);
		}
		else if(this.zoomLevel == 2){
			if(this.width < 300){	
				this.xAxis.ticks(d3.time.minute, 15);   // 4 labels on the axis
			}
			else if(this.width < 625){	
				this.xAxis.ticks(d3.time.minute, 10);   // 6 labels on the axis
			}
			else{	
				this.xAxis.ticks(d3.time.minute, 5);    // 12 labels on the axis
			}
		}

		this.graph.select("svg g#xaxis").call(this.xAxis);
	}

	// Resize the graph based on the window size
	this.resize = function(){
		// Recalculate the width of the plot
		this.width = document.getElementById("price-graph").clientWidth 
			- (this.paddingLeft + this.paddingRight);
	
		if(this.width < 0){
			return false;
		}

		this.rescaleXAxis();

		// Resize and redraw the data lines
		this.graph.select("svg path#priceDataLine")
			.attr("d", this.lineLMP(pricingData));

		// Reposition the legend
		this.graph.select("svg g#priceGraphLegend")
			.attr("transform", "translate(" + (this.paddingLeft + (this.width / 2) - (this.legendWidth / 2)) + ", " 
					+ (this.height + this.paddingTop + 5) + ")");

		// Rescale the rectangle that listens for events
		this.graph.select("svg rect#mouseListener")
			.attr("width", this.width)
			.attr("height", this.height);
		
		// Resize and reposition the clip path	
		this.graph.select("svg clipPath rect")
			.attr("width", this.width)
			.attr("height", this.height - this.paddingTop);
	}
}
