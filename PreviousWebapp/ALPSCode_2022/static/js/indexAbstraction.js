function drawIndexChart(){

  var nyData = [];
  var chart;
  $(document).ready(function() {
  	$.extend({
  	getUrlVars: function(){
  		var vars = [], hash;
  		var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
  		for(var i = 0; i < hashes.length; i++)     {
  			hash = hashes[i].split('=');
  			vars.push(hash[0]);
  			vars[hash[0]] = hash[1];
  		}
  		return vars;
  		},
  		getUrlVar: function(name){
  			return $.getUrlVars()[name];
  		}
  	});

  	var zone = '';
  	var counter = 0;
  	var FINAL_COUNT;
  	var globalDate = new Date();
  	var rnd;
  	rnd = globalDate.getFullYear() + '' + globalDate.getMonth() + '' + globalDate.getDate() + '' + globalDate.getHours() + '' + (Math.round(globalDate.getMinutes()/5)*5);


  	var zoneObj = new Object;
		//zoneObj['ZoneA']={zone:'a',name:'Zone A - West',ptid:'61752', yestData:[], data:[], yestLoad:[], load:[],color:'#0066cc', visible:false};
  		zoneObj['ZoneB']={zone:'b',name:'Zone B - Genesee',ptid:'61753', yestData:[], data:[], yestLoad:[],load:[],color:'#6600cc', visible:false};
  		zoneObj['ZoneC']={zone:'c',name:'Zone C - Central',ptid:'61754', yestData:[], data:[], yestLoad:[],load:[],color:'#cc00cc', visible:false};
  		zoneObj['ZoneD']={zone:'d',name:'Zone D - North',ptid:'61755',yestData:[], data:[], yestLoad:[],load:[],color:'#00cccc', visible:false};
  		zoneObj['ZoneE']={zone:'e',name:'Zone E - Mohawk Valley',ptid:'61756', yestData:[],data:[],yestLoad:[],load:[],color:'#47a3ff', visible:false};
  		zoneObj['ZoneF']={zone:'f',name:'Zone F - Capital',ptid:'61757',yestData:[],data:[], yestLoad:[],load:[],color:'#cc0066', visible:false};
  		zoneObj['ZoneG']={zone:'g',name:'Zone G - Hudson Valley',ptid:'61758',yestData:[],data:[], yestLoad:[],load:[],color:'#ff850a', visible:false};
  		zoneObj['ZoneH']={zone:'h',name:'Zone H - Millwood',ptid:'61759',yestData:[],data:[],yestLoad:[],load:[],color:'#cc6600', visible:false};
  		zoneObj['ZoneI']={zone:'i',name:'Zone I - Dunwoodie',ptid:'61760',yestData:[],data:[],yestLoad:[],load:[],color:'#cccc00', visible:false};
		zoneObj['ZoneJ']={zone:'j',name:'Zone J - New York City',ptid:'61761',yestData:[],data:[],yestLoad:[],load:[],color:'#cc0000', visible:false};
		zoneObj['ZoneK']={zone:'k',name:'Zone K - Long Island',ptid:'61762',yestData:[],data:[],yestLoad:[],load:[],color:'#00cc00', visible:false};

  	if($.getUrlVar('zone')){
  	 	zone = $.getUrlVar('zone');
  	 	var thisZone = 'Zone' + zone.toUpperCase();
  	 	zoneObj[thisZone].visible = true;
  	}

  	var globalDate = new Date();
  	var tomorrowDate = new Date();
  	tomorrowDate.setDate(globalDate.getDate() + 1);
  	var yesterdayDate = new Date();
  	yesterdayDate.setDate(globalDate.getDate() - 1);
  	var timeStamp = globalDate.getMonth() + '' + globalDate.getDate() + '' + globalDate.getFullYear() + '' + globalDate.getHours() + '' + globalDate.getMinutes() + '' + globalDate.getSeconds();
  	getData();

  function getDateFormatted(date){
  	var thisMonth = date.getMonth()+1;
  	if (thisMonth<10){
  		thisMonth = '0' +  thisMonth;
  	}
  	var dateFormatted = date.getFullYear() + '' + thisMonth;
  	if (date.getDate()<10){
  		dateFormatted = dateFormatted + '0' + date.getDate();
  	}else{
  		dateFormatted = dateFormatted + '' + date.getDate();
  	}
  	return dateFormatted;
  }

  function dateToUTC(date){
  	var thisMonth = date.getMonth();
  	var thisDay = date.getDate();
  	var thisYear = date.getFullYear();
  	var thisHour = date.getHours();
  	var thisMin = date.getMinutes();
  	return Date.UTC(thisYear, thisMonth, thisDay, thisHour, thisMin);
  }

  function getData(){
  	$("#loading").show();

  	var dateFormatted = getDateFormatted(globalDate);
  	var yesterdateFormatted = getDateFormatted(yesterdayDate);
  	var tomdateFormatted = getDateFormatted(tomorrowDate);

  	var yestNYMIS = "http://mis.nyiso.com/public/csv/realtime/" + yesterdateFormatted + "realtime_zone.csv";
  	var yestNYUrl = "select * from csv where url = '" + yestNYMIS + "'";
  	var nyMIS = "http://mis.nyiso.com/public/csv/realtime/" + dateFormatted + "realtime_zone.csv";
  	var nyUrl = "select * from csv where url = '" + nyMIS + "'";

  	var yestLoadMIS = "http://mis.nyiso.com/public/csv/pal/" + yesterdateFormatted + "pal.csv";
  	var yestLoadUrl = "select * from csv where url = '" + yestLoadMIS + "'";
  	var loadMIS = "http://mis.nyiso.com/public/csv/pal/" + dateFormatted + "pal.csv";
  	var loadUrl = "select * from csv where url = '" + loadMIS + "'";

  	FINAL_COUNT = 4;
  	getNYData(nyUrl);
  	getNYData(yestNYUrl);
  	getLoadData(loadUrl);
  	getLoadData(yestLoadUrl);
    //console.log(loadUrl);
  }
  var tempNum = 0;
  function setNYData(data){
    // console.log(data.query.results.row[0]);
    // console.log("2: " + data.query.results.row[1].col1 + ":  " + data.query.results.row[1].col3);
    // console.log("3: " + data.query.results.row[2].col1 + ":  " + data.query.results.row[2].col3);
    // console.log("4: " + data.query.results.row[3].col1 + ":  " + data.query.results.row[3].col3);
    // console.log("5: " + data.query.results.row[4].col1 + ":  " + data.query.results.row[4].col3);
    // console.log("6: " + data.query.results.row[5].col1 + ":  " + data.query.results.row[5].col3);
    // console.log("7: " + data.query.results.row[6].col1 + ":  " + data.query.results.row[6].col3);
    // console.log("8: " + data.query.results.row[7].col1 + ":  " + data.query.results.row[7].col3);
    // console.log("9: " + data.query.results.row[8].col1 + ":  " + data.query.results.row[8].col3);
    // console.log("10: " + data.query.results.row[9].col1 + ":  " + data.query.results.row[9].col3);
    // console.log("11: " + data.query.results.row[10].col1 + ":  " + data.query.results.row[10].col3);
    // console.log("12: " + data.query.results.row[11].col1 + ":  " + data.query.results.row[11].col3);
    // console.log("13: " + data.query.results.row[12].col1 + ":  " + data.query.results.row[12].col3);
    // console.log("14: " + data.query.results.row[13].col1 + ":  " + data.query.results.row[13].col3);

  	if(data.query.count > 0){
		//var q = 0;//Changes
  		$.each(data.query.results.row, function(i, v) {
			//console.log(v.col0 + ": " + v.col1 + ": " + v.col2 + ": " + v.col3 + ": " + v.col4);
			//var w = 0;//Changes
			var i = 0;
  			$.each(zoneObj, function(k,z) {
				//console.log(q + " : " + w);//Changes
				if (v.col2 == z.ptid) {
					var thisData = [];
					var dateStr = v.col0;
					var thisDate = new Date(dateStr);
					var dateUTC = dateToUTC(thisDate);
			  // console.log("Global: " + globalDate.getDate());
			  // console.log("This:   " + thisDate.getDate());

	          if (data.query.results.row[i].col1 == "N.Y.C." && thisDate.getFullYear() == globalDate.getFullYear() && thisDate.getMonth() == globalDate.getMonth() && thisDate.getDate() == globalDate.getDate() && thisDate.getHours() == globalDate.getHours() && globalDate.getMinutes() <= thisDate.getMinutes()){
				tempNum += 1;
				
				console.log(tempNum + ": " + data.query.results.row[i].col0 + ": " + data.query.results.row[i].col1 + ":  " + data.query.results.row[i].col3);
				console.log("globalDate: " + globalDate);
				console.log("dateStr: " + dateStr);
				console.log("v.col0: " + v.col0);
				console.log("v.col2: " + v.col2);
				console.log("z.ptid: " + z.ptid);
			  }
	
					thisData.push(dateUTC);
					thisData.push(parseFloat(v.col3));

					if(thisDate.getDate() == globalDate.getDate()){
						if(thisDate <= globalDate){
							zoneObj[k].data.push(thisData);
				  // console.log(thisDate);
						}
					}else if(thisDate.getDate() == yesterdayDate.getDate()){
						zoneObj[k].yestData.push(thisData);
					}
				 }
				 //w++;
				 i++;
  			 });
			//q++;
  		});
  	}
  	drawChart();
    // console.log(globalDate);
  }

  function getNYData(url){
  	$.ajax({
  		url: 'http://query.yahooapis.com/v1/public/yql',
  		data: {
  			q: url,
  			format: 'json',
  			_maxage: 120,
  			rnd: rnd
  		},
  		cache:true,
  		dataType: 'jsonp',
  		success:function(data,status,rsp){
      		setNYData(data);
    		}
  	});
  }

  function setLoadData(data){
    //console.log(data.query.results.row[1]);
  	if(data.query.count > 0){
  		$.each(data.query.results.row, function(i, v) {
  			$.each(zoneObj, function(k,z) {
  			if (v.col3 == z.ptid) {
  				if(parseFloat(v.col4)){
					//console.log(v.col4);
  					var thisData = [];
  					var dateStr = v.col0;
  					var thisDate = new Date(dateStr);
  					var dateUTC = dateToUTC(thisDate);

  					thisData.push(dateUTC);
  					thisData.push(parseFloat(v.col4));

  					if(thisDate.getDate() == globalDate.getDate()){
  						zoneObj[k].load.push(thisData);
  					}else if(thisDate.getDate() == yesterdayDate.getDate()){
  						zoneObj[k].yestLoad.push(thisData);
  					}
  				}
  			 }
  			 });
  		});
  	}
  	drawChart();
  }

  function getLoadData(url){
  	$.ajax({
  		url: 'http://query.yahooapis.com/v1/public/yql',
  		data: {
  			q: url,
  			format: 'json',
  			_maxage: 120,
  			rnd: rnd
  		},
  		cache:true,
  		dataType: 'jsonp',
  		success:function(data,status,rsp){
      		setLoadData(data);
          //console.log(data);
    		}
  	});
  }

function drawChart(){
  counter = counter + 1;
  if (counter == FINAL_COUNT){

  var dMth = globalDate.getMonth() + 1;
  if(dMth < 10){//Changes
    dMth = "0" + dMth;
  }
  var dDay = globalDate.getDate();
  if(dDay < 10){//Changes
    dDay = "0" + dDay;
  }
  var dYr = globalDate.getFullYear();
  var dStr = dMth + '/' + dDay + '/' + dYr;
  title = dStr + ' - Real-Time LBMP';//Changes

  Highcharts.theme = { colors: ['#4572A7'] };// prevent errors in default theme

  var seriesData= [];

  if (zone == ''){ 
  $.each(zoneObj, function(k,z) {
  	var thisData = [];

  	thisData.type = 'line';
  	thisData.name = z.name;
  	thisData.data = zoneObj[k].data;
  	thisData.data.sort();
  	seriesData.push(thisData);
  	for (i = 0;i < thisData.data.length; i++){
		console.log(k + ": " + thisData.type + ": " + thisData.name + ": " + thisData.data[i]);
  	}
  	//console.log(thisData.data.length);
  });
  }else{
  $.each(zoneObj, function(k,z) { console.log("Alternate");
  	var visi;
  	var lbmpData = [];
  	var loadData = [];
  	if (z.zone == zone){
  		visi = true;
  	}else{
  		visi = false;
  	}

  	lbmpData.type = 'line';
  	lbmpData.id = z.zone;
  	lbmpData.name = z.name;
  	lbmpData.data = zoneObj[k].data;
  	lbmpData.visible = visi;
  	lbmpData.color = z.color;
  	lbmpData.step = true;
  	lbmpData.events = {
  		legendItemClick: function(event) {
  			var loadId = this.options.id + 'load';
  			if (this.visible == true){
  				var series = chart.get(loadId);
  				series.hide();
  			}else{
  				var series = chart.get(loadId);
  				series.show();
  			}
  		},
  		click: function(event) {
  			this.hide();
  		}
  	};
  	seriesData.push(lbmpData);

  });
  }
     chart = new Highcharts.Chart({
        chart: {
           renderTo: 'chartContainer',
           zoomType: 'xy'

        },
         title: {
           text: title
        },
         subtitle: {
           text: document.ontouchstart === undefined ?
              'Click and drag in the plot area to zoom in' :
              'Drag your finger over the plot to zoom in'
        },
  	  xAxis: [{
  			 type: 'datetime'
  		  },{
  			type: 'datetime',
  			linkedTo: 0,
  			opposite: false,
  			tickInterval: 24 * 3600 * 1000,
  			labels: {
                  formatter: function() {
                      return Highcharts.dateFormat('%m/%d/%Y', this.value);
                  }
              }
  		  }
  	  ],
        yAxis: [
        {
           title: {
              text: 'Dollars ($/MWh)'
           },
          startOnTick: true,
           showFirstLabel: true
        },{         title: {
              text: 'Y'
           },
          startOnTick: true,
           showFirstLabel: true}
        ],
        tooltip: {
           crosshairs: true,
           borderColor: '#909090',
           formatter: function() {
           	var s = '<b>' + Highcharts.dateFormat('%m/%d/%Y %H:%M', this.x) +'</b><br/>';
              $.each(this.points, function(i, p) {
              	if (p.series.name.indexOf('Flow')>0 || p.series.name.indexOf('Load')>0){
              		s = s + '<span style="color:' + p.point.series.color + '">' + p.series.name + '</span> : ' + Highcharts.numberFormat(p.y, 2) + ' MW<br/>';
              	}else{
                  	s = s + '<span style="color:' + p.point.series.color + '">' + p.series.name + ' LBMP</span> : $' + Highcharts.numberFormat(p.y, 2) + '<br/>';
                  }
              });
              return s;

           },
           shared:true
        },
        legend: {
        	 enabled: false,
           layout: 'vertical',
           align: 'right',
           verticalAlign: 'top',
           x: -10,
           y: 50,
           borderWidth: 0
        },
        plotOptions: {
           line: {
              lineWidth: 2,
              marker: {
                 enabled: false,
                 states: {
                    hover: {
                       enabled: true,
                       radius: 4
                    }
                 }
              },
              states: {
              	hover: {
                  	enabled: true,
                      lineWidth: 2
                  }
              },
              shadow: false
           }
        },
        series: seriesData
     });
     $("#loading").hide();
  }
}

  $.each(zoneObj, function(k,z) {
    //console.log(zoneObj);//temp changes .ZoneA.data["0"][1]
  	var $legend = $('#legend');
  	var linkClass = (z.visible == true) ? '' : 'hidden';

  	$('<li id="legend' + z.zone + '">')
  		.css('color', z.color)
  		.text(z.name)
  		.click(function(){
      		toggleSeries(z.zone);
  		})
  		.addClass(linkClass)
          .hover(function () {
          	$(this).addClass("highlight");
           },
           function () {
           	$(this).removeClass("highlight");
           })
  		.appendTo($legend);
  });

  function toggleSeries(zone){
  	$.each(zoneObj, function(k,z) {
  		var legendId = '#legend' + z.zone;
  		if(z.zone == zone){
  			if (z.visible == true){
  				z.visible = false;
  				$(legendId).addClass('hidden');
  			}else{
  				z.visible = true;
  				$(legendId).removeClass('hidden');
  			}
  			return;
  		}
  	});
  	paintChart();
  }

  function paintChart(){
  	var lbmpEnabled = $('#showLbmps').is(':checked');
  	var loadEnabled = false;
  	var tomorrowEnabled = false;

  	var yesterdayEnabled = true;

  	if (lbmpEnabled == true){
  		chart.yAxis[0].axisTitle.show();
  	}else{
  		chart.yAxis[0].axisTitle.hide();
  	}

  	$.each(chart.series, function(i,s) {
  		thisZone = 'Zone' + s.name.charAt(5);
  		if (s.name.indexOf('Load')==-1){
  			var allData = zoneObj[thisZone].data;
  			if(yesterdayEnabled){
  				allData = allData.concat(zoneObj[thisZone].yestData);
  			}
  			s.setData(allData);
  			if(zoneObj[thisZone].visible==true){
  				if (lbmpEnabled ==true){
  					if (s.visible == false){
  						s.show();
  					}
  				} else {
  					if (s.visible == true){
  						s.hide();
  					}
  				}
  			}else{
  				if (s.visible == true){
  					s.hide();
  				}
  			}
  		}else{
  			var allLoadData = zoneObj[thisZone].load;
  			if(yesterdayEnabled){
  				allLoadData = allLoadData.concat(zoneObj[thisZone].yestLoad);
  			}
  			s.setData(allLoadData);
  			if(zoneObj[thisZone].visible==true){
  				if (loadEnabled ==true){
  					if (s.visible == false){
  						s.show();
  					}
  				}else{
  					if (s.visible == true){
  						s.hide();
  					}
  				}
  			}else{
  				if (s.visible == true){
  					s.hide();
  				}
  			}
  		}
  	});
  }

  $("#showLbmps").click(function() {
  	paintChart();
  });

  $("#showLoads").click(function() {
  	paintChart();
  });

  $("#showYesterday").click(function() {
  	paintChart();
  });
  });
}
