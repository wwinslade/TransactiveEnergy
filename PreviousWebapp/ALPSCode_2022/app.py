from flask import Flask, render_template, redirect, url_for, request, jsonify
from matplotlib.font_manager import json_dump
import requests
from simplejson import dump
from databases import FridgeData, AppData
from ApplianceClass import Fridge
from plot_price import plot_price
import subprocess
import json
from databases import Data

# from rpi_rf import RFDevice
from transmitterPrimetest import send_code

app = Flask(__name__)

#These are the websote address for the different urls 
#ex 0.0.0.0:5000/powergeneratopn The render template is the name of the
#corresponding html files in the template folder. A couple were left
#intentionally blank

@app.route("/")
def main():
	return render_template("FrontPanel.html")


@app.route("/FrontPanel")
def Frontpanel():
	return render_template("FrontPanel.html")

@app.route("/Frontpanel_ReVvabout")
def Frontpanel_ReVvabout():
	return render_template("FrontPanel_ReVvabout.html")

@app.route("/Frontpanel_SHEMSabout")
def Frontpanel_SHEMSabout():
	return render_template("FrontPanel_SHEMSabout.html")

@app.route("/Frontpanel_CombinedTechabout")
def Frontpanel_CombinedTechabout():
	return render_template("FrontPanel_CombinedTechsabout.html")

@app.route("/SHEMS_home")
def home():
	return render_template("SHEMS_index.html")
	
@app.route("/SHEMS_powergeneration")
def powergeneration():
	return render_template("SHEMS_powergeneration.html")

@app.route("/SHEMS_conditions")
def conditions():
	return render_template("SHEMS_conditions.html")
	
	
@app.route("/SHEMS_livecamera")
def camera():
	return render_template("SHEMS_livecamera.html")
	
@app.route("/ReVv_home")
def R_home():
	return render_template("ReVv_index.html")
	
@app.route("/ReVv_powergeneration")
def R_powergeneration():
	return render_template("ReVv_powergeneration.html")

@app.route("/ReVv_conditions")
def R_conditions():
	return render_template("ReVv_setting.html")
	
	
@app.route("/ReVv_livecamera")
def R_camera():
	return render_template("ReVv_livecamera.html")
	
	
@app.route("/ALPS_home")
def ALPS_home():
	return render_template("ALPS_index.html")
	
# This is Where we wanna put the power price graph
@app.route("/ALPS_powergeneration")
def ALPS_powergeneration():
	#this is the funtion that will generate the graph on the HTML page
	#plot_price()    #Was commented out for redundancy and to correct a bug
	                 #Was generating an extra plot which caused the graph link on the website to crash after accessing
					 #more than once
	return render_template("ALPS_powergeneration.html")

@app.route("/ALPS_conditions", methods = ['GET', 'POST'])
def ALPS_conditions():
	fridge = FridgeData.getFridge("sewellnoah@gmail.com")
	appliances = AppData.getAppliances("sewellnoah@gmail.com")
	fridge_object = json.dumps(fridge.__dict__, indent = 4)
	 
	return render_template("ALPS_conditions.html",fridge=fridge_object, applianceArray=json.dumps([app.__dict__ for app in appliances]))

#background process happening without any refreshing
@app.route('/update_db')
def update_db():
	appName = request.args.get('appName')
	adr = request.args.get('adr')
	adrApp = request.args.get('adrApp')
	currState = request.args.get('currState')
	if adr:
		FridgeData.updateFridgeADR(appName, adr)
	if currState:
		print("updated currState")
		AppData.updateAppState(appName, currState)
	if adrApp:
		if adrApp == "true":
			print("updated app's ADR")
			AppData.updateAppADR(appName, 1)
		else:
			print("updated app's ADR")
			AppData.updateAppADR(appName, 0)
	else:
		print("no params")
	return ("nothing")

@app.route("/ALPS_livecamera")
def ALPS_camera():
	return render_template("ALPS_livecamera.html")


@app.route("/channel1on")
def channel1on():
	send_code(2761756)
	#flash("Channel Signal Sent")
	#return redirect(url_for(home))
	return render_template("ALPS_conditions.html")
	
@app.route("/channel1off")
def channel1off():
	send_code(2761748)
	#flash("Channel Signal Sent")
	#return redirect(url_for(home))
	return render_template("ALPS_conditions.html")
	
@app.route("/channel2on")
def channel2on():
	send_code(2761754)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel2off")
def channel2off():
	send_code(2761746)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel3on")
def channel3on():
	send_code(2761753)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel3off")
def channel3off():
	send_code(2761745)
	return render_template("ALPS_conditions.html")

@app.route("/channel4on")
def channel4on():
	send_code(2761757)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel4off")
def channel4off():
	send_code(2761749)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel5on")
def channel5on():
	send_code(2761755)
	return render_template("ALPS_conditions.html")
	
@app.route("/channel5off")
def channel5off():
	send_code(2761747)
	return render_template("ALPS_conditions.html")
	
#Codes for the on and off signals for each of the rf plugs MK 530 page 
	
@app.route("/MK_channel1on")
def MK_channel1on():
	send_code(349491)
	#flash("Channel Signal Sent")
	#return redirect(url_for(home))
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel1off")
def MK_channel1off():
	send_code(349500)
	#flash("Channel Signal Sent")
	#return redirect(url_for(home))
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel2on")
def MK_channel2on():
	send_code(349635)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel2off")
def MK_channel2off():
	send_code(349644)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel3on")
def MK_channel3on():
	send_code(349955)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel3off")
def MK_channel3off():
	send_code(349964)
	return render_template("FrontPanel_SHEMSabout.html")

@app.route("/MK_channel4on")
def MK_channel4on():
	send_code(351491)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel4off")
def MK_channel4off():
	send_code(351500)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel5on")
def MK_channel5on():
	send_code(357635)
	return render_template("FrontPanel_SHEMSabout.html")
	
@app.route("/MK_channel5off")
def MK_channel5off():
	send_code(357644)
	return render_template("FrontPanel_SHEMSabout.html")

if __name__ == "__main__":
		app.run(debug=True)
