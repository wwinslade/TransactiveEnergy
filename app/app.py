from flask import Flask, render_template

from services import *


app = Flask(__name__)

# Default (root) route
@app.route("/")
def root():
  return render_template("index.html")




if __name__ == "__main__":
  app.run(debug=True)
