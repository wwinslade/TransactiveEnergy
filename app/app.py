# app.py
# Created by William Winslade on 28 Jan 2025

# This file contains the main flask code for the web app

from flask import Flask, render_template

from services import *

app = Flask(__name__)

# Default (root) route
@app.route("/")
def root():
  return render_template("index.html")


if __name__ == "__main__":
  app.run(debug=True)
