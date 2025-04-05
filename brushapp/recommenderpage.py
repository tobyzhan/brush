from flask import Blueprint, render_template

recommenderbp = Blueprint("recommender", __name__)

@recommenderbp.route("/")
def recommenderpage():
    return render_template('recommender.html')