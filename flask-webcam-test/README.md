# Flask Webcam Test
## Instructions to Run
1. Ensure prerequisites are installed. Need at least Python3.12 and preferably manage your environment w/ Conda
2. Create an environment for the project. If you have done this already skip to step 3
    - Run `conda env create -f environment.yml` in your terminal
3. Activate the environment
    - Run `conda activate cs401-flask-webcam-test` in your terminal
4. Navigate to the *flask-webcam-test* directory
5. Run `sudo flask run` in your terminal
6. Go to a web browser and navigate to `localhost:5000`


## Notes
### 7 Nov 2024
Idea is to test out how to integrate a webcam into a Flask app. I suspect that the current frontend is using Flask currently.

Seems pretty easy to integrate a webcam with the OpenCV library. Not sure how the Pi's CPU will be able to handle this increase in compute demand.

