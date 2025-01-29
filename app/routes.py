# routes.py
# Created by William Winslade on 28 Jan 2025

'''
This file will define all the routes for the Flask application
'''

from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
  return render_template("index.html")



