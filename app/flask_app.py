# app.py
# Created by William Winslade on 28 Jan 2025

# This file contains the main flask code for the web app

from flask import Flask, render_template

from services import *
from routes import bp

# Create the flask app
app = Flask(__name__)

# Register routes
app.register_blueprint(bp)


if __name__ == "__main__":
  app.run(debug=True)
