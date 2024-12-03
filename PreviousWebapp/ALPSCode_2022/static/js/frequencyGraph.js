// Class that creates and maintains the energy frequency data information
function FrequencyGraph(){
	this.paddingTop = 40;
	this.paddingRight = 40;
	this.paddingBottom = 25;
	this.paddingLeft = 60;
	this.hoverPadding = 10;
	this.lineWidth = 1;
	this.graph = d3.select("#frequency-graph");
	this.zoomLevel = 0;

	this.init = function(){	
		this.calcFrequency();
		this.calcDimensions();
		this.initAxes();
		this.initLines();	
		this.addHoverEffects();
	}

	this.calcFrequency = function(){
		// Since we don't have frequency data provided by ISO New England, Charles gave us this 
		// function for generating frequency data from the LMP
		this.genFrequency = function(d){
			var lmp = parseFloat(d.lmp);
			if(!isNaN(lmp) && lmp > 0 && isFinite(lmp))
				return (60 - 0.2 * Math.log(lmp)) + 0.6;
			else if(lmp <= 0)
				return 60;
			else if(lmp < 0)
				return 60;
			else
				return 60;
		};
	}

	
	this.calcDimensions = function(){
		this.width = document.getElementById("frequency-graph-container").clientWidth
			- (this.paddingLeft + this.paddingRight);
		this.height = document.getElementById("frequency-graph-container").clientHeight
			- (this.paddingBottom + this.paddingTop);
	}

	this.initAxes = function(){
		// Scaling function for x values
		this.xScale = d3.time.scale()
			.domain([pricingData[0].date, pricingData[pricingData.length-1].date])
			.range([this.paddingLeft, this.width + this.paddingLeft]);

		// Scaling function for y values
		this.yScale = d3.scale.linear()
			.domain([d3.min(pricingData.map(this.genFrequency)),
				d3.max(pricingData.map(this.genFrequency))])
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
			.attr("class", "axis xaxis")
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
			.attr("id", "freqClip")
			.append("svg:rect")
			.attr("x", this.paddingLeft)
			.attr("y", this.paddingTop)
			.attr("width", this.width)
			.attr("height", this.height - this.paddingTop);

		// Function to convert price data to graph lines
		this.lineFreq = d3.svg.line()
			.x(function(d){
				return this.xScale(d.date);
			})
			.y(function(d){
				return this.yScale(this.genFrequency(d));
			});

		// Create the frequency data line
		this.graph.append("svg:path")
			.attr("id", "frequencyDataLine")
			.attr("d", this.lineFreq(pricingData))
			.attr("stroke", "#679451")
			.attr("stroke-width", this.lineWidth)
			.attr("fill", "none")
			.attr("clip-path", "url(#freqClip)");

		// Create the animation rectangle
		// Acts as a "curtain" to reveal the lines underneath
		this.graph.append("svg:rect")
			.attr("x", -1-(this.width + this.paddingLeft))
			.attr("y", 1-(this.height))
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("id", "freqAnimationCurtain")
			.attr("transform", "rotate(180)")
			.attr("shape-rendering", "optimizeSpeed")
			.attr("fill", "#f6f4ee");

		// Specifies the animation that moves the aforementioned rectangle
		this.animation = d3.select("svg#frequency-graph").transition()
			.delay(0)
			.duration(1500);
		this.animation.select("svg rect#freqAnimationCurtain")
			.attr("width", 0);
	}

	this.addHoverEffects = function(){
		this.graph.append("svg:text")
			.attr("id", "freqMouseLabel")
			.attr("x", this.width + this.paddingLeft - 50)
			.attr("y", 25);
		
		// Add the mouse line
		this.graph.append("svg:line")
			.attr("id", "freqMouseLine")
			.attr("y1", this.paddingTop)
			.attr("y2", this.height)
			.attr("stroke", "#4f4f4f")
			.attr("stroke-width", 1)
			.attr("opacity", 0);
		this.graph.append("svg:circle")
			.attr("id", "freqMouseCircle")
			.attr("fill", "#679451")
			.attr("opacity", 0)
			.attr("r", 3.5);

		// Add a rectangle to detect mouse move events
		this.graph.append("svg:rect")
			.attr("id", "freqMouseListener")
			.attr("width", this.width)
			.attr("height", this.height)
			.attr("x", this.paddingLeft)
			.attr("y", this.paddingTop)
			.attr("fill", "none")
			.attr("pointer-events", "all")

			// Show the frequency markers on hover
			.on("mouseover", function(){
				d3.select("#freqMouseLine")
					.attr("opacity", 1);
				d3.select("#freqMouseLabel")
					.attr("opacity", 1);
				d3.select("#freqMouseCircle")
					.attr("opacity", 1);
			})

			// Hide the frequency markers when the user stops hovering
			.on("mouseout", function(){
				d3.select("#freqMouseLine")
					.attr("opacity", 0);
				d3.select("#freqMouseLabel")
					.attr("opacity", 0);
				d3.select("#freqMouseCircle")
					.attr("opacity", 0);
			})

			// Move the mouse line to match the mouse X position
			.on("mousemove", this.mouseMoveCallback);
	}

	this.mouseMoveCallback = function(){
		// Get the data point closest to the mouse's x-value
		var xVal = frequencyGraph.xScale.invert(d3.mouse(this)[0]);
		var i = frequencyGraph.bisectDate(pricingData, xVal, 1);
		var d;
		if(xVal - pricingData[i - 1].date > pricingData[i].date - xVal)
			d = pricingData[i];
		else
			d = pricingData[i-1];

		// Move the elements into position
		d3.select("#freqMouseLabel")
			.text(d3.time.format("%m/%d/%Y %H:%M - ")(d.date) + frequencyGraph.genFrequency(d).toFixed(2) + " Hz")
			.attr("x", frequencyGraph.width + frequencyGraph.paddingLeft - 175);
		d3.select("#freqMouseLine")
			.attr("x1", frequencyGraph.xScale(d.date))
			.attr("x2", frequencyGraph.xScale(d.date));
		d3.select("#freqMouseCircle")
			.attr("cx", frequencyGraph.xScale(d.date))
			.attr("cy", frequencyGraph.yScale(frequencyGraph.genFrequency(d)));
	}

	this.mouseMoveCallback2 = function(){
		// Get the data point closest to the mouse's x-value
		var xVal = frequencyGraph.xScale.invert(d3.mouse(this)[0]);
		var i = frequencyGraph.bisectDate(pricingData, xVal, 1);
		var d;
		if(xVal - pricingData[i - 1].date > pricingData[i].date - xVal)
			d = pricingData[i];
		else
			d = pricingData[i-1];
		
		// Move the elements into position
		d3.select("#freqMouseLabel")
			.attr("transform", "translate(" + frequencyGraph.xScale(d.date) + "," + frequencyGraph.yScale(frequencyGraph.genFrequency(d)) + ")");
		d3.select("#freqMouseLabel").select("text").select("tspan#f1")
			.text(frequencyGraph.genFrequency(d).toFixed(2) + " Hz");
		d3.select("#freqMouseLabel").select("text").select("tspan#f2")
			.text(d3.time.format("%m/%d/%Y %H:%M")(d.date));
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
		
		// Redraw the data line
		this.graph.select("svg path#frequencyDataLine")
			.transition().duration(300)
			.attr("d", this.lineFreq(pricingData));

		// Reposition the mouse listener
		this.graph.select("svg rect#freqMouseListener")
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

		// Redraw the data line
		this.graph.select("svg path#frequencyDataLine")
			.transition().duration(300)
			.attr("d", this.lineFreq(pricingData));

		// Reposition the mouse listener
		this.graph.select("svg rect#freqMouseListener")
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

		// Redraw the data line
		this.graph.select("svg path#frequencyDataLine")
			.transition().duration(300)
			.attr("d", this.lineFreq(pricingData));

		// Reposition the mouse listener
		this.graph.select("svg rect#freqMouseListener")
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
				this.xAxis.ticks(d3.time.minute, 15);	// 4 labels on the axis
			}
			else if(this.width < 625){	
				this.xAxis.ticks(d3.time.minute, 10);	// 6 labels on the axis
			}
			else{	
				this.xAxis.ticks(d3.time.minute, 5);	// 12 labels on the axis
			}
		}

		this.graph.select("svg g.xaxis").call(this.xAxis);
	}

	this.resize = function(){
		// Recalculate the width of the plot
		this.width = document.getElementById("frequency-graph-container").clientWidth
			- (this.paddingLeft + this.paddingRight);

		if(this.width < 0){
			return false;
		}

		this.rescaleXAxis();

		// Resize and redraw the data lines
		this.graph.select("svg path#frequencyDataLine")
			.attr("d", this.lineFreq(pricingData));
		
		// Resize and reposition the svg rectangle mouse listener
		this.graph.select("svg rect#freqMouseListener")
			.attr("width", this.width)
			.attr("height", this.height);
		
		// Resize and reposition the clip path
		this.graph.select("svg clipPath rect")
			.attr("width", this.width)
			.attr("height", this.height - this.paddingTop);
	}
}

