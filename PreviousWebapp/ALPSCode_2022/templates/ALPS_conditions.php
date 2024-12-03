<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>ALPS Web App</title>


		<script src="http://ajax.googleapis.com/ajax/libs/jquery/2.2.2/jquery.min.js"></script>
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
		<script src="//d3js.org/d3.v3.min.js" charset="utf-8"></script>
		<!--Added this for link -->
		<script type = "text/javascript" src="../static/js/links.js"></script>
		<link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel='stylesheet' type='text/css'>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
		<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
		<!-- The correct links to the css file are below -->
		<link rel="stylesheet" type="text/css" href="../static/css/style.css">
		<link rel="stylesheet" type="text/css" href="../static/css/index.css">
		<link rel="stylesheet" type="text/css" href="../static/css/foundation.css">
		<script src="https://kit.fontawesome.com/b852344663.js" crossorigin="anonymous"></script>

<!--This stuff up here is important and works, maybe we can do something about the useless graphs though -->
	</head>

	<body id="body">

		<!--This is the top header of the HTML Doc, Picture and ALPS-->
	    <nav class="top-bar" data-topbar>
			<div class="container">
				<a href="#" onClick="return showHome()">
					<img src="../static/img/curent.png" alt="current image" width="250px" height="63px" align="right">
					<h2 id="brand">ALPS<br>
					<span id="brand-small">Automated Load Planning System</span></h2>
				</a>
			</div>


		<!--Website Navigation with local and global Navigation-->
		<header class="navbar-inverse" id="navbar">
			<div class="container">
				
				<!--This is the Local Website Navigation tabs-->
				<ul class="nav navbar-nav">
					<li id="navHome" class="nav-link"><a href="{{ url_for('ALPS_home') }}" onclick="return showHome()" value="Display">Home</a></li>
					<li id="navPowergen" class="nav-link"><a href="{{ url_for('ALPS_powergeneration') }}" onclick="return showPowergeneration()" value= "Display">Hourly Prices</a></li>
					<li id="navConditionals" class="nav-link active"><a href="{{ url_for('ALPS_conditions') }}" onclick="return showConditions()" value="Display">Smart Home Manager</a></li>
					<li id="navCamera" class="nav-link"><a href="{{ url_for('ALPS_camera') }}" onclick="return showLivecamera()" value="Display">Live Camera</a></li>
				</ul>

				<!--This is the GLobal Website's Navigation dropdown-->
				<ul class="nav navbar-nav navbar-right" id="project-drop">
					<div class="dropdown">
						<button class="btn btn-warning dropdown-toggle dropdown-menu-right" type="button" data-toggle="dropdown" id="navButton">Project Websites
						<span class="caret"></span></button>
							<ul class="dropdown-menu">
								<li><a href="{{ url_for ('Frontpanel') }}">MK 530 website</a></li>
								<li><a href="{{ url_for ('R_home') }}">ReVv website</a></li>
								<li><a href="{{ url_for ('home') }}">SHEMS website</a></li>
							</ul>
					</div>
					<button class="btn" id ="navButton" action="ALPS_user.php"><i class="fa-solid fa-user"></i></button>
				</ul>
			</div>
		</header>
		</nav>
		

		<!--Daniel: Changed tabs to say user settings instead of policy
		& added what this tab is going to be in terms of ADR on/off + SHEMS on/off-->
		
		<!--Section That contains Header about User Stettings-->
		<div id="container" class ="container">
			<div id="content">
				<section id="home" class="page shown">
					<div class="section-title">
						<h4></h4>
					</div>
						</p>
					</div>
			</div>
		</div>
			
					
					
					<!--This is the chunk of code that implements the buttons
					<div class="row">
					  <div class="large-12 columns">
						  <dd>
							<a href="#panel3" align="middle"><b>Lights</b></a>
							<div id="panel3" class="content">
								  <div class="row">
									<div class="large-12 columns">
										<div class="large-8 medium-4 columns">
											<div class="callout panel">
												<p><b>Light	(Socket #1)</b></p>
											</div>
										</div>
										<a href="{{ url_for('channel1on') }}" class="medium success button">ON</a>
										<a href="{{ url_for('channel1off') }}" class="medium alert button" class="medium alert button">OFF</a>
									</div>
									<div class="large-12 columns">
										<div class="large-8 medium-4 columns">
											<div class="callout panel">
												<p><b>Light	(Socket #2)</b></p>
											</div>
										</div>
										<a href="{{ url_for('channel2on') }}" class="medium success button">ON</a>
										<a href="{{ url_for('channel2off') }}" class="medium alert button" class="medium alert button">OFF</a>
									</div>
											<div class="large-12 columns">
										<div class="large-8 medium-4 columns">
											<div class="callout panel">
												<p><b>Light	(Socket #3)</b></p>
											</div>
										</div>
										<!--<a href="{{ url_for('channel3on') }}" class="medium success button">ON</a>
										<a href="{{ url_for('channel3off') }}" class="medium alert button" class="medium alert button">OFF</a>
										<label class="switch">
										<input type="checkbox">
											<span class="slider"></span>
										</label>
									</div>
											<div class="large-12 columns">
										<div class="large-8 medium-4 columns">
											<div class="callout panel">
												<p><b>Fan	(Socket #4)</b></p>
											</div>
										</div>
										<a href="{{ url_for('channel4on') }}" class="medium success button">ON</a>
										<a href="{{ url_for('channel4off') }}" class="medium alert button" class="medium alert button">OFF</a>
									</div>
											<div class="large-12 columns">
										<div class="large-8 medium-4 columns">
											<div class="callout panel">
												<p><b>Lamp	(Socket #5)</b></p>
											</div>
										</div>
										<a href="{{ url_for('channel5on') }}" class="medium success button">ON</a>
										<a href="{{ url_for('channel5off') }}" class="medium alert button" class="medium alert button">OFF</a>
									</div>
								</div>
							</div>
						  </dd>
					  </div>
					</div>
				</section>
			</div>
		</div> -->
		
		<!-- Slider/Button Implementation-->
		<div id="container" class ="container">
			<div class="containerSwitch">
			
				<div>
					<label class="switch">
					<input type="checkbox">
						<span class="slider"></span>
					</label>
				</div>
				
				
				<div>
					<label class="switch">
					<input type="checkbox">
						<span class="slider"></span>
					</label>
				</div>
				
				<div>
					<label class="switch">
					<input type="checkbox">
						<span class="slider"></span>
					</label>
				</div>
				
				<div>
					<label class="switch">
					<input type="checkbox">
						<span class="slider"></span>
					</label>
				</div>
			
			</div>
		</div>
				
		<footer class="row">
		  <div class="large-12 columns">
			<hr></hr>

			<div class="row">
			  <div class="large-12 columns">
				<p>© Copyright by <i>Smart Home and Grid Laboratory (SHGL) at the University of Tennessee Knoxville </i></p>
			  </div>
			</div>
		  </div>
		</footer>
				<!-- Testing new button implementation and layout design -->
	</body>



</html>
				

