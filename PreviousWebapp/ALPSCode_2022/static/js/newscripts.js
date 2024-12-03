

function drawChart() {
	var data = google.visualization.arrayToDataTable([
	  ['Time', 'Frequency'],
	  ['2004',  1000],
	  ['2005',  1170],
	  ['2006',  660],
	  ['2007',  1030]
	]);

	var options = {
	  title: 'Frequency',
	  //curveType: 'function',
	  legend: { position: 'bottom' }
	};

	var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));

	chart.draw(data, options);
}


