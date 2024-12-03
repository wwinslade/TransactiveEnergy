window.onload = showHome;

var x, counter;
var energyConsumptionGraph;
var priceGraph;
var frequencyGraph;
var pieGraph;

var pricingData;
var energyData;
var energyUsageTotals;

/* Switch between pages and run PHP scripts to get data from the database ************************/

function showPage(pageElement, navElement){
	// Set the active navigation link 
	var navlinks = document.getElementsByClassName("nav-link");
	for(var i = 0; i < navlinks.length; i++){
		navlinks[i].className = "nav-link";
	}
	document.getElementById(navElement).className = "active nav-link";

	// Show the selected page and hide the others
	var pages = document.getElementsByClassName("page");
	for(var i = 0; i < pages.length; i++){
		pages[i].className = "page hidden";
	}
	document.getElementById(pageElement).className = "page shown";
}

// Run the page's PHP script with an ajax request
function loadPHP(scriptName, readyStateChangeCallback){
	if(window.XMLHttpRequest) 
		xhr = new XMLHttpRequest();
	else
		xhr = new ActiveXObject("Microsoft.XMLHTTP");
	
	xhr.onreadystatechange = readyStateChangeCallback;
	xhr.open("GET", scriptName, true);
	xhr.setRequestHeader("Content-type", "text/plain");
	xhr.send();
}

// Functions for showing the home page, settings page, and price history pages, respectively
function showHome(){
	if(typeof energyConsumptionGraph == "undefined"){
		loadPHP("php/getEnergy.php", function(){
			if(xhr.readyState == 4 && xhr.status == 200){
				console.log(xhr.responseText);
				
				document.getElementById("load-energy-consumption-script").setAttribute('type', 'text/javascript');
				document.getElementById("load-energy-consumption-script").text = xhr.responseText;
				
				// Create the two visualizations for this page
				energyConsumptionGraph = new EnergyConsumptionGraph();
				energyConsumptionGraph.init();
			
				pieGraph = new PieGraph();
				pieGraph.init();
				
				// Update the table with summary information
				updateUsageInfo();
				
				d3.select(window).on("resize", function(){
					pieGraph.resize();
					energyConsumptionGraph.resize();
				});	
			}
		});
	}

	showPage("home", "navHome");
	return false;
}

function showSettings(){
	loadPHP("php/getSettings.php", function(){
		if(xhr.readyState == 4 && xhr.status == 200){	
			document.getElementById("appliance-list").innerHTML = xhr.responseText;
		}
	});

	showPage("settings", "navSettings");
	return false;
}

function showPricing(){	
	// Load LMP data via a PHP script if it has not been loaded already
	if(typeof priceGraph == "undefined"){
		loadPHP("php/getPricing.php", function(){
			if(xhr.readyState == 4 && xhr.status == 200){
				document.getElementById("loadPricingScript").innerHTML = xhr.responseText;
				priceGraph = new PriceGraph();
				priceGraph.init();

				
				d3.select(window).on("resize", function(){
					priceGraph.resize();
				});
			}
		});
		showPage("pricing", "navPricing");
	}
	else{
		showPage("pricing", "navPricing");
		priceGraph.resize();
	}

	return false;
}
function showFrequency(){
	if(typeof priceGraph == "undefined"){
		loadPHP("php/getPricing.php", function(){
			if(xhr.readyState == 4 && xhr.status == 200){
				document.getElementById("loadPricingScript").innerHTML = xhr.responseText;
				frequencyGraph = new FrequencyGraph();
				frequencyGraph.init();
				
				d3.select(window).on("resize", function(){
					frequencyGraph.resize();
				});
			}				
		});

	}
	else{

                
                frequencyGraph.resize();
                                                	
	}
	
	return false;
}
/* User Settings page: Menu navigation ***********************************************************/

function toggleEditSettingsMenu(menuId, applianceId){
	if(document.getElementById(menuId).className === "col-md-12 settings-menu settings-menu-shown")
		hideEditSettingsMenu(menuId, applianceId);
	else
		showEditSettingsMenu(menuId, applianceId);
	return false;
}

function showEditSettingsMenu(menuId, applianceId){
	document.getElementById(menuId).className = "col-md-12 settings-menu settings-menu-shown";
	document.getElementById(applianceId).className = "appliance container-fluid settings-menu-shown";
	return false;
}

function hideEditSettingsMenu(menuId, applianceId){
	document.getElementById(menuId).className = "col-md-12 settings-menu settings-menu-hidden";
	document.getElementById(applianceId).className = "appliance container-fluid";
	return false;
}

function setActiveIcon(icon, applianceNum){	
	var icons = document.getElementsByClassName("icon-" + applianceNum);
	for(var i = 0; i < icons.length; i++){
		icons[i].className = "settings-icon icon-" + applianceNum;
	}
	
	var iconId = "icon-" + icon + "-" + applianceNum;
	document.getElementById(iconId).className = "settings-icon icon-" + applianceNum + " active";

	// Update the hidden field for the form submission
	document.getElementById("hidden-field-icon-" + applianceNum).value = "assets/" + icon + ".svg";

	return false;
}

function updateUserSettings(formNo){
	var formName = "form-" + formNo;

	if(validateForm(formNo)){
		$.ajax({
			type: "POST",
			url: "php/updateSettings.php",
			data: {
				"form-name": document.forms[formName]["form-name"].value,
				"form-icon": document.forms[formName]["form-icon"].value,
				"form-power": document.forms[formName]["form-power"].value,
				"form-threshold": document.forms[formName]["form-threshold"].value,
				"form-policy": document.forms[formName]["form-policy"].value,
				"form-number": document.forms[formName]["form-number"].value
			},
			success: function(response){
				console.log(response);
				showSettings();
			},
			error: function(xhr, ajaxOptions, thrownError){
				alert(xhr.status + ": " + thrownError);
			}
		});
	}

	return false;
}

function validateForm(formNo){
	var formName = "form-" + formNo;
	console.log(formName);
	
	// Validate the appliance name
	var nameInput = document.forms[formName]["form-name"];
	var name = nameInput.value;	

	if(name === ""){
		nameInput.parentElement.className = "has-error";	
		return false;
	}
	if(escapeHtml(name).length > 30){
		nameInput.parentElement.className = "has-error";	
		return false;
	}
	else{
		nameInput.parentElement.className = "";
	}	

	// Validate the appliance icon
	var iconInput = document.forms[formName]["form-icon"];
	var icon = iconInput.value;
	var iconRegex = /assets\/.*\.svg/;
	if(!(icon.match(iconRegex))){
		return false;
	}

	var powerInput = document.forms[formName]["form-power"];
	var power = powerInput.value;
	if(power.length > 4){
		powerInput.parentElement.className = "has-error";	
		return false;
	}
	else{
		for(var i = 0; i < power.length; i++){
			if(isNaN(parseInt(power[i]))){
				powerInput.parentElement.className = "input-group has-error";	
				return false;
			}
		}
		powerInput.parentElement.className = "input-group";
	}

	var policy = document.forms[formName]["form-policy"].value;
	if(isNaN(parseInt(policy)) ||  parseInt(policy) < 0 || parseInt(policy) > 2){	
		return false;
	}

	var priceThresholdInput = document.forms[formName]["form-threshold"];
	var priceThreshold = priceThresholdInput.value;
	if(isNaN(parseInt(priceThreshold))){
		priceThresholdInput.parentElement.className = "input-group has-error";
		return false;
	}
	else{
		priceThresholdInput.parentElement.className = "input-group";	
	}

	return true;
}

// JavaScript equivalent of PHP's htmlspecialchars used for form validation
// http://stackoverflow.com/questions/1787322/htmlspecialchars-equivalent-in-javascript
function escapeHtml(text) {
	var map = {
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#039;'
	};

	return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

/* Edit Scheduled Off Periods Menu *******************************************************************************/

function showTimeMenu(applianceId, scheduleId, startTime, endTime, daysArray){
	// If there was no applianceId specified, that means we're adding a new off period
	if(scheduleId == null){

		// Set the start and end times to some arbitrary values
		document.getElementById("time-begin-h").value = "00"
		document.getElementById("time-begin-m").value = "00";
		document.getElementById("time-end-h").value = "23";
		document.getElementById("time-end-m").value = "59";
		
		// Edit the submit button action so that it adds a new off period
		document.getElementById("time-submit").onclick = function(){
			addNewOffPeriod(applianceId);
		}
		document.getElementById("time-delete").onclick = function(){
			hideTimeMenu();
		}
	}

	else{
		// Set the start and end times according to the queried settings
		document.getElementById("time-begin-h").value = startTime.substring(0, 2);
		document.getElementById("time-begin-m").value = startTime.substring(3, 5);
		document.getElementById("time-end-h").value = endTime.substring(0, 2);
		document.getElementById("time-end-m").value = endTime.substring(3, 5);

		// Set the selected days according to the queried settings
		for(var i = 0; i < daysArray.length; i++){	
			document.getElementById("day-" + daysArray[i]).className = "time-select-day selected";
			document.getElementById("day-" + daysArray[i] + "-hidden").value = "1";
		}
		document.getElementById("time-submit").onclick = function(){
			return saveOffPeriod(applianceId, scheduleId);
		}
		document.getElementById("time-delete").onclick = function(){
			return deleteOffPeriod(scheduleId);
		}
	}
	
	// Finally show the menu
	document.getElementById("time-menu-container").className = "shown";
	return false;
}

function hideTimeMenu(){
	document.getElementById("time-menu-container").className = "";
	
	// Unselect any day buttons that may have been selected earlier
	var dayLinks = document.getElementsByClassName("time-select-day");
	for(var i = 0; i < dayLinks.length; i++){
		dayLinks[i].className = "time-select-day";
		document.getElementById(dayLinks[i].getAttribute("id") + "-hidden").value = "0";
	}
	
	return false;
}

// Select or unselect a day 'button' as the user clicks
function toggleDay(dayLinkId){
	var dayLink = document.getElementById(dayLinkId);
	if(dayLink.className === "time-select-day"){
		document.getElementById(dayLinkId).className = "time-select-day selected";
		
		// Also select the hidden field that holds the value
		document.getElementById(dayLinkId + "-hidden").value = "1";
	}
	else{
		document.getElementById(dayLinkId).className = "time-select-day";

		// Also unselect the hidden field that holds the value
		document.getElementById(dayLinkId + "-hidden").value = "0";
	}

	return false;
}

function saveOffPeriod(applianceId, scheduleId){

	// If the form data was successfully validated
	if(validateOffPeriodForm()){
			
		// Get the start and end times
		var startH = document.getElementById("time-begin-h");
		var startM = document.getElementById("time-begin-m");
		var endH = document.getElementById("time-end-h");
		var endM = document.getElementById("time-end-m");
		
		var sh, sm, eh, em;
		if(startH.value.length === 2)
			sh = startH.value;
		else
			sh = "0" + startH.value;
		
		if(startM.value.length === 2)
			sm = startM.value;
		else
			sm = "0" + startM.value;
		
		if(endH.value.length === 2)
			eh = endH.value;
		else
			eh = "0" + endH.value;
		
		if(endM.value.length === 2)
			em = endM.value;
		else
			em = "0" + endM.value;
		
		var startTime = sh + ":" + sm;
		var endTime = eh + ":" + em;

		// Get the days
		var dayString = "";
		var dayArray = [];
		if(document.getElementById("day-sun-hidden").value == "1"){
			dayString += "sun,";
			dayArray.push("sun");
		}
		if(document.getElementById("day-mon-hidden").value == "1"){
			dayString += "mon,";
			dayArray.push("mon");
		}
		if(document.getElementById("day-tue-hidden").value == "1"){
			dayString += "tue,";
			dayArray.push("tue");
		}
		if(document.getElementById("day-wed-hidden").value == "1"){
			dayString += "wed,";
			dayArray.push("wed");
		}
		if(document.getElementById("day-thu-hidden").value == "1"){
			dayString += "thu,";
			dayArray.push("thu");
		}
		if(document.getElementById("day-fri-hidden").value == "1"){
			dayString += "fri,";
			dayArray.push("fri");
		}
		if(document.getElementById("day-sat-hidden").value == "1"){
			dayString += "sat,";
			dayArray.push("sat");
		}
		
		dayString = dayString.substring(0, dayString.length-1);

		$.ajax({
			type: "POST",
			url: "php/updatePeriods.php",
			data: {
				"form-begin": startTime,
				"form-end": endTime,
				"form-day": dayString,
				"form-schedule": scheduleId
			},
			success: function(response){
				console.log(response);
				showSettings();
				hideTimeMenu();
			},
			error: function(xhr, ajaxOptions, thrownError){
				alert(xhr.status + ": " + thrownError);
			}
		});
	}

	return false;
}

function addAppliance(){
	$.ajax({
		type: "POST",
		url: "php/addAppliance.php",
		data: {
			"form-name": "New Appliance",
			"form-icon": "assets/question-mark.svg",
			"form-power": 60,
			"form-threshold": 0,
			"form-policy": 0
		},
		success: function(response){
			console.log(response);
			showSettings();	
		},
		error: function(xhr, ajaxOptions, thrownError){
			alert(xhr.status + ": " + thrownError);
		}
	});
}

// Wrapper class for saveOffPeriod, adds a new DOM element for the new off period
function addNewOffPeriod(applianceId){
	if(validateOffPeriodForm()){
		
		// Get the start and end times
		var startH = document.getElementById("time-begin-h");
		var startM = document.getElementById("time-begin-m");
		var endH = document.getElementById("time-end-h");
		var endM = document.getElementById("time-end-m");
		
		var sh, sm, eh, em;
		if(startH.value.length === 2)
			sh = startH.value;
		else
			sh = "0" + startH.value;
		
		if(startM.value.length === 2)
			sm = startM.value;
		else
			sm = "0" + startM.value;
		
		if(endH.value.length === 2)
			eh = endH.value;
		else
			eh = "0" + endH.value;
		
		if(endM.value.length === 2)
			em = endM.value;
		else
			em = "0" + endM.value;
		
		var startTime = sh + ":" + sm;
		var endTime = eh + ":" + em;

		// Get the days
		var dayString = "";
		var dayArray = [];
		if(document.getElementById("day-sun-hidden").value == "1"){
			dayString += "sun,";
			dayArray.push("sun");
		}
		if(document.getElementById("day-mon-hidden").value == "1"){
			dayString += "mon,";
			dayArray.push("mon");
		}
		if(document.getElementById("day-tue-hidden").value == "1"){
			dayString += "tue,";
			dayArray.push("tue");
		}
		if(document.getElementById("day-wed-hidden").value == "1"){
			dayString += "wed,";
			dayArray.push("wed");
		}
		if(document.getElementById("day-thu-hidden").value == "1"){
			dayString += "thu,";
			dayArray.push("thu");
		}
		if(document.getElementById("day-fri-hidden").value == "1"){
			dayString += "fri,";
			dayArray.push("fri");
		}
		if(document.getElementById("day-sat-hidden").value == "1"){
			dayString += "sat,";
			dayArray.push("sat");
		}
		
		dayString = dayString.substring(0, dayString.length-1);

		$.ajax({
			type: "POST",
			url: "php/addPeriod.php",
			data: {
				"form-begin": startTime,
				"form-end": endTime,
				"form-day": dayString,
				"form-number": applianceId
			},
			success: function(response){
				console.log(response);
				showSettings();
				hideTimeMenu();
			},
			error: function(xhr, ajaxOptions, thrownError){
				alert(xhr.status + ": " + thrownError);
			}
		});
	}

	return false;
}

function validateOffPeriodForm(){
	var rv = true;
	
	// Make sure the inputs are numbers
	var startH = document.getElementById("time-begin-h");
	var val = parseInt(startH.value);
	if(startH.value.length > 2 || startH.value.length < 1 || isNaN(val) || val < 0 || val > 23){
		startH.parentElement.className = "has-error";
		rv = false;
	}
	else{
		startH.parentElement.className = "";
	}

	var startM = document.getElementById("time-begin-m");
	var val = parseInt(startM.value);
	if(startM.value.length > 2 || startM.value.length < 1 || isNaN(val) || val < 0 || val > 59){
		startM.parentElement.className = "has-error";
		rv = false;
	}
	else{
		if(startM.parentElement.className != "has-error")
			startM.parentElement.className = "";
	}

	var endH = document.getElementById("time-end-h");
	var val = parseInt(endH.value);	
	if(endH.value.length > 2 || endH.value.length < 1 || isNaN(val) || val < 0 || val > 23){
		endH.parentElement.className = "has-error";	
		rv = false;
	}
	else{
		endH.parentElement.className = "";	
	}

	var endM = document.getElementById("time-end-m");
	var val = parseInt(endM.value);	
	if(endM.value.length > 2 || endM.value.length < 1 || isNaN(val) || val < 0 || val > 59){
		endM.parentElement.className = "has-error";	
		rv = false;
	}
	else{
		if(endM.parentElement.className != "has-error")
			endM.parentElement.className = "";	
	}
	
	// Make sure the user selects at least one day
	if(document.getElementById("day-sun-hidden").value == "0" &&
			document.getElementById("day-mon-hidden").value == "0" &&
			document.getElementById("day-tue-hidden").value == "0" &&
			document.getElementById("day-wed-hidden").value == "0" &&
			document.getElementById("day-thu-hidden").value == "0" &&
			document.getElementById("day-fri-hidden").value == "0" &&
			document.getElementById("day-sat-hidden").value == "0"){
		document.getElementById("days-container").className = "error";
		rv = false;
	}
	else{
		document.getElementById("days-container").className = "";
	}
	
	return rv;
}

function showThreshold(applianceNum, show){
	if(show)
		document.getElementById("threshold-div-" + applianceNum).className = "threshold-div shown";
	else
		document.getElementById("threshold-div-" + applianceNum).className = "threshold-div hidden";
}

function timTest(){
	loadPHP("php/getEnergy.php", function(){
		if(xhr.readyState == 4 && xhr.status == 200){
			console.log(xhr.responseText);	
		}
	});
}

function showDeleteDialog(applianceId, applianceName){
	document.getElementById("confirm-delete-container").className = "shown";
	document.getElementById("confirm-delete-name").innerHTML = applianceName;
	document.getElementById("confirm-delete-button").onclick = function(){
		deleteAppliance(applianceId);
	}

	return false;
}

function hideDeleteDialog(){
	document.getElementById("confirm-delete-container").className = "";
	return false;
}

function deleteAppliance(applianceId){
	$.ajax({
		type: "POST",
		url: "php/deleteAppliance.php",
		data: {
			"form-number": applianceId
		},
		success: function(response){
			console.log(response);
			showSettings();
			hideDeleteDialog();
		},
		error: function(xhr, ajaxOptions, thrownError){
			alert(xhr.status + ": " + thrownError);
		}
	});	

	return false;
}

function deleteOffPeriod(scheduleId){
	$.ajax({
		type: "POST",
		url: "php/deletePeriod.php",
		data: {
			"form-number": scheduleId
		},
		success: function(response){
			console.log(response);
			showSettings();
			hideTimeMenu();
		},
		error: function(xhr, ajaxOptions, thrownError){
			alert(xhr.status + ": " + thrownError);
		}
	});	

	return false;	
}

function updateUsageInfo(){
	document.getElementById("energy-used").innerHTML = (totalEnergyConsumption/1000.0).toFixed(2) + " kWh";
	document.getElementById("energy-saved").innerHTML = (savedEnergyConsumption/1000.0).toFixed(2) + " kWh";
	document.getElementById("energy-cost").innerHTML = "$" + totalCost.toFixed(2);
	document.getElementById("energy-cost-saved").innerHTML = "$" + totalMoneySaved.toFixed(2);
	document.getElementById("co2-used").innerHTML = co2Consumed(totalEnergyConsumption).toFixed(2) + " lbs CO<sub>2</sub>";
	document.getElementById("co2-saved").innerHTML = co2Consumed(savedEnergyConsumption).toFixed(2) + " lbs CO<sub>2</sub>";
}

function co2Consumed(watts){
	return ((228.6 / 1000000.0 / 0.293071) * watts);
}
