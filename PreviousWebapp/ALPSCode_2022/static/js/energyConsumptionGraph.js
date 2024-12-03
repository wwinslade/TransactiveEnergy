var totalEnergyConsumption = 0;
var savedEnergyConsumption = 0;
var totalCost = 0;
var totalMoneySaved = 0;

function EnergyConsumptionGraph(){
	this.paddingTop = 40;
	this.paddingRight = 40;
	this.paddingBottom = 25;
	this.paddingLeft = 60;
	this.hoverPadding = 10;
	this.lineWidth = 1;
	this.graph = d3.select("#energy-usage-graph");
	this.zoomLevel = 0;

	this.init = function(){
		this.parseDates();
		this.calcEnergyConsumption();
		this.calcDimensions();
		this.initAxes();
		this.initLines();
		this.addHoverEffects();
	}

	this.parseDates = function(){
		// Take the date strings from the database and convert them to JavaScript date objects
		var dateParser = d3.time.format("%Y-%m-%dT%H:%M");
		for(var i = 0; i < energyData.length; i++){
			energyData[i].date = dateParser.parse(energyData[i].datestr);
		}

		// Sort array based on date
		energyData.sort(function(d1, d2){
			return d1.date - d2.date;
		});

		// Initialize the array to hold the power consumption at every time interval
		this.data = [{
			date: energyData[0].date,
			powerConsumption: 0
		}];

		// Since we only care about the past month, discard any data older than 31 days old
		// (12 five minute intervals per hour) * (24 hours per day) * (31 days) = 8928
		// This assumes that there are no gaps in the data
		if(energyData.length > 8928){
			energyData = energyData.slice(energyData.length - 8928, energyData.length);
		}
	}

	this.calcEnergyConsumption = function(){
		var datestr = energyData[0].datestr;
		var counting = true;
		var numAppliances = -1;

		energyUsageTotals = [];
		for(var i = 0; i < energyData.length; i++){
			// If we're still counting the number of appliances...
			if(counting){

				// ...and we encounter a new date, we've encountered all appliances
				if(energyData[i].datestr != datestr){
					counting = false;
					numAppliances = i;

					// Check if the appliance is on or off
					if(energyData[i].state == "1"){

						// If it is on, update that appliance's total consumption
						for(var j = 0; j < numAppliances; j++){
							if(energyUsageTotals[j].id == energyData[i].applianceID){
								energyUsageTotals[j].consumed += (energyData[i].power * (1.0 / 12.0));
								break;
							}
						}

						// Add another object for the new date
						this.data.push({
							date: energyData[i].date,
							powerConsumption: this.data[0].powerConsumption + (energyData[i].power * (1.0 / 12.0))
						});
					}

					// If the appliance is off, add a new object for the new date with no power consumed
					else{
						this.data.push({
							date: energyData[i].date,
							powerConsumption: 0
						});
					}
				}

				// If we haven't encountered all appliances yet...
				else{

					// Check if the appliance is on
					if(energyData[i].state == "1"){

						// If so, update this date's power consumption
						this.data[0].powerConsumption += energyData[i].power * (1.0 / 12.0);

						// Add another object to keep track of the new appliance's individual power consumption
						energyUsageTotals.push({
							id: energyData[i].applianceID,
							name: energyData[i].name,
							consumed: energyData[i].power * (1.0 / 12.0)
						});
					}
					else{

						// Add another object to keep track of the new appliance's individual power consumption
						energyUsageTotals.push({
							id: energyData[i].applianceID,
							name: energyData[i].name,
							consumed: 0
						});
					}
				}
			}

			// If we've stopped counting the number of appliances...
			else{

				// If we've hit a new date, add another object for the total consumption per date
				if(i % numAppliances == 0){
					if(energyData[i].state == "1"){
						this.data.push({
							date: energyData[i].date,
							powerConsumption: energyData[i].power * (1.0 / 12.0)
							//	powerConsumption: this.data[Math.floor(i/numAppliances)-1].powerConsumption + (energyData[i].power * (1.0 / 12.0))
						});

						// If it is on, update that appliance's total consumption
						for(var j = 0; j < numAppliances; j++){
							if(energyUsageTotals[j].id == energyData[i].applianceID){
								energyUsageTotals[j].consumed += (energyData[i].power * (1.0 / 12.0));
								break;
							}
						}
					}
					else{
						this.data.push({
							date: energyData[i].date,
							powerConsumption: 0
							//	powerConsumption: this.data[Math.floor(i/numAppliances)-1].powerConsumption
						});
					}
				}

				// If this is the same date, update that object
				else{
					if(energyData[i].state == "1"){
						this.data[Math.floor(i/numAppliances)].powerConsumption += (energyData[i].power * (1.0 / 12.0));

						for(var j = 0; j < numAppliances; j++){
							if(energyUsageTotals[j].id == energyData[i].applianceID){
								energyUsageTotals[j].consumed += (energyData[i].power * (1.0 / 12.0));
								break;
							}
						}
					}
				}
			}

			// Calculate summary information
			var wattHours = (energyData[i].power * (1.0 / 12.0));
			if(energyData[i].state == "1"){
				totalEnergyConsumption += wattHours;
				totalCost += (parseFloat(energyData[i].LMP) * (wattHours / 1000000.0));
			}
			else{
				savedEnergyConsumption += wattHours;
				totalMoneySaved += (parseFloat(energyData[i].LMP) * (wattHours / 1000000.0));
			}
		}

		var data = [];
		var offset = -1;
		var temp = 0;
		for(var i = 0; i < this.data.length; i++){
			if(offset == -1){
				if(this.data[i].date.getMinutes() == 0){
					offset = 1;
					temp += this.data[i].powerConsumption;
					data.push({
						date: this.data[i].date,
						powerConsumption: temp
					});
				}
				else{
					temp += this.data[i].powerConsumption;
				}
			}
			else if(this.data[i].date.getMinutes() == 0){
				data.push({
					date: this.data[i].date,
					powerConsumption: this.data[i].powerConsumption
				});
			}
			else{
				//console.log(i + " " + offset);
				data[data.length-1].powerConsumption += this.data[i].powerConsumption;
			}
		}

		this.data = data;
		//console.log(this.data);
	}

	this.calcDimensions = function(){
		this.width = document.getElementById("energy-usage-container").clientWidth
		- (this.paddingLeft + this.paddingRight);
		this.height = document.getElementById("energy-usage-container").clientHeight
		- (this.paddingBottom + this.paddingTop);
		if(this.height > 300)
		this.height = 300 - (this.paddingBottom + this.paddingTop);
	}

	this.initAxes = function(){
		// Scaling function for x values
		this.xScale = d3.time.scale()
		.domain([this.data[0].date, this.data[this.data.length-1].date])
		.range([this.paddingLeft, this.width + this.paddingLeft]);

		// Scaling function for y values
		this.yScale = d3.scale.linear()
		.domain([0, d3.max(this.data.map(function(d){
			return d.powerConsumption / 1000.0;
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
		.attr("id", "energyClip")
		.append("svg:rect")
		.attr("x", this.paddingLeft)
		.attr("y", this.paddingTop)
		.attr("width", this.width)
		.attr("height", this.height - this.paddingTop);

		// Function to convert price data to graph lines
		this.lineEnergy = d3.svg.line()
		.x(function(d){
			return this.xScale(d.date);
		})
		.y(function(d){
			return this.yScale(d.powerConsumption / 1000.0);
		});

		// Create the frequency data line
		this.graph.append("svg:path")
		.attr("id", "energyDataLine")
		.attr("d", this.lineEnergy(this.data))
		.attr("stroke", "#679451")
		.attr("stroke-width", this.lineWidth)
		.attr("fill", "none")
		.attr("clip-path", "url(#energyClip)");

		// Create the animation rectangle
		// Acts as a "curtain" to reveal the lines underneath
		this.graph.append("svg:rect")
		.attr("x", -1-(this.width + this.paddingLeft))
		.attr("y", 1-(this.height))
		.attr("width", this.width)
		.attr("height", this.height)
		.attr("id", "energyAnimationCurtain")
		.attr("transform", "rotate(180)")
		.attr("shape-rendering", "optimizeSpeed")
		.attr("fill", "#f6f4ee");

		// Specifies the animation that moves the aforementioned rectangle
		this.animation = d3.select("svg#energy-usage-graph").transition()
		.delay(0)
		.duration(1500);
		this.animation.select("svg rect#energyAnimationCurtain")
		.attr("width", 0);
	}

	this.addHoverEffects = function(){
		this.graph.append("svg:text")
		.attr("id", "energyMouseLabel")
		.attr("x", this.width + this.paddingLeft - 50)
		.attr("y", 25);

		// Add the mouse line
		this.graph.append("svg:line")
		.attr("id", "energyMouseLine")
		.attr("y1", this.paddingTop)
		.attr("y2", this.height)
		.attr("stroke", "#4f4f4f")
		.attr("stroke-width", 1)
		.attr("shape-rendering", "crispEdges")
		.attr("opacity", 0);
		this.graph.append("svg:circle")
		.attr("id", "energyMouseCircle")
		.attr("fill", "#679451")
		.attr("opacity", 0)
		.attr("r", 3.5);

		// Add a rectangle to detect mouse move events
		this.graph.append("svg:rect")
		.attr("id", "energyMouseListener")
		.attr("width", this.width)
		.attr("height", this.height)
		.attr("x", this.paddingLeft)
		.attr("y", this.paddingTop)
		.attr("fill", "none")
		.attr("pointer-events", "all")

		// Show the frequency markers on hover
		.on("mouseover", function(){
			d3.select("#energyMouseLine")
			.attr("opacity", 1);
			d3.select("#energyMouseLabel")
			.attr("opacity", 1);
			d3.select("#energyMouseCircle")
			.attr("opacity", 1);
		})

		// Hide the frequency markers when the user stops hovering
		.on("mouseout", function(){
			d3.select("#energyMouseLine")
			.attr("opacity", 0);
			d3.select("#energyMouseLabel")
			.attr("opacity", 0);
			d3.select("#energyMouseCircle")
			.attr("opacity", 0);
		})

		// Move the mouse line to match the mouse X position
		.on("mousemove", this.mouseMoveCallback);
	}

	this.mouseMoveCallback = function(){
		// Get the data point closest to the mouse's x-value
		var xVal = energyConsumptionGraph.xScale.invert(d3.mouse(this)[0]);
		var i = energyConsumptionGraph.bisectDate(energyConsumptionGraph.data, xVal, 1);
		var d;
		if(xVal - energyConsumptionGraph.data[i - 1].date > energyConsumptionGraph.data[i].date - xVal)
		d = energyConsumptionGraph.data[i];
		else
		d = energyConsumptionGraph.data[i-1];

		// Move the elements into position
		d3.select("#energyMouseLabel")
		.text(d3.time.format("%m/%d/%Y %H:%M - ")(d.date) + (d.powerConsumption / 1000.0).toFixed(2) + " kWh")
		.attr("x", energyConsumptionGraph.width + energyConsumptionGraph.paddingLeft - 175);
		d3.select("#energyMouseLine")
		.attr("x1", energyConsumptionGraph.xScale(d.date))
		.attr("x2", energyConsumptionGraph.xScale(d.date));
		d3.select("#energyMouseCircle")
		.attr("cx", energyConsumptionGraph.xScale(d.date))
		.attr("cy", energyConsumptionGraph.yScale(d.powerConsumption / 1000.0));
	}

	this.setScaleHour = function(){
		this.zoomLevel = 2;

		// Update the axis scale
		if(this.data.length <= 12)
		this.setScaleFull();
		else
		this.xScale.domain([this.data[this.data.length-1-12].date, this.data[this.data.length-1].date]);
		this.xAxis.tickFormat(d3.time.format("%I:%M"));
		this.graph.select("svg g#xaxis")
		.transition().duration(300)
		.call(this.xAxis);

		// Redraw the data line
		this.graph.select("svg path#energyDataLine")
		.transition().duration(300)
		.attr("d", this.lineEnergy(this.data));

		// Reposition the mouse listener
		this.graph.select("svg rect#energyMouseListener")
		.on("mousemove", this.mouseMoveCallback);

		this.rescaleXAxis();
	}

	this.setScaleDay = function(){
		this.zoomLevel = 1;

		// Update the axis scale
		if(this.data.length <= 288)
		this.setScaleFull();
		else
		this.xScale.domain([this.data[this.data.length-1-288].date, this.data[this.data.length-1].date]);

		this.xAxis.tickFormat(d3.time.format("%I:%M"));
		this.graph.select("svg g#xaxis")
		.transition().duration(300)
		.call(this.xAxis);

		// Redraw the data line
		this.graph.select("svg path#energyDataLine")
		.transition().duration(300)
		.attr("d", this.lineFreq(this.data));

		// Reposition the mouse listener
		this.graph.select("svg rect#energyMouseListener")
		.on("mousemove", this.mouseMoveCallback);

		this.rescaleXAxis();
	}

	this.setScaleFull = function(){
		this.zoomLevel = 0;

		// Update the axis scale
		this.xScale.domain([this.data[0].date, this.data[this.data.length-1].date]);
		this.xAxis.tickFormat(d3.time.format("%b %d"));
		this.graph.select("svg g#xaxis")
		.transition().duration(300)
		.call(this.xAxis);

		// Redraw the data line
		this.graph.select("svg path#energyDataLine")
		.transition().duration(300)
		.attr("d", this.lineFreq(this.data));

		// Reposition the mouse listener
		this.graph.select("svg rect#energyMouseListener")
		.on("mousemove", this.mouseMoveCallback);

		this.rescaleXAxis();
	}

	// Since D3 is stupid and we have to manually specify tick mark intervals,
	// this function sets them based on how much of the graph is shown and how
	// wide the graph is
	this.rescaleXAxis = function(){
		this.xScale.range([this.paddingLeft, this.width + this.paddingLeft]);
		this.xAxis.scale(this.xScale);

		if(this.width < 768){
			this.xAxis.ticks(3);
			if(this.data.length < 48){
				this.xAxis.tickFormat(d3.time.format("%I:%M"));
			}
			else{
				this.xAxis.tickFormat(d3.time.format("%b %d"));
			}
		}
		else{
			this.xAxis.ticks(7);
			if(this.data.length < 48){
				this.xAxis.tickFormat(d3.time.format("%I:%M"));
			}
			else{
				this.xAxis.tickFormat(d3.time.format("%b %d"));
			}
		}

		this.graph.select("svg g.xaxis").call(this.xAxis);
	}

	this.resize = function(){
		this.calcDimensions();

		if(this.width < 0){
			return false;
		}

		this.rescaleXAxis();

		// Resize and redraw the data lines
		this.graph.select("svg path#energyDataLine")
		.attr("d", this.lineEnergy(this.data));

		// Resize and reposition the svg rectangle mouse listener
		this.graph.select("svg rect#energyMouseListener")
		.attr("width", this.width)
		.attr("height", this.height);

		// Resize and reposition the clip path
		this.graph.select("svg clipPath rect")
		.attr("width", this.width)
		.attr("height", this.height - this.paddingTop);
	}
}
