from flask import Blueprint, render_template, request
from brushapp.recommender import recommend_daily_binge, recommend_full_completion

homepagebp = Blueprint("homepage", __name__)

@homepagebp.route("/", methods=["GET", "POST"])
def homepage():
    daily_recommendations = []
    full_recommendations = []
    
    if request.method == "POST":
        form_type = request.form.get("form_type")
        genre = request.form.get("genre", "").strip() or None
        
        if form_type == "daily":
            time_limit = int(request.form.get("time_limit", 0))
            if time_limit > 0:
                daily_recommendations = recommend_daily_binge(time_limit, genre)
        
        elif form_type == "full":
            days = int(request.form.get("days", 0))
            daily_minutes = int(request.form.get("daily_minutes", 0))
            if days > 0 and daily_minutes > 0:
                full_recommendations = recommend_full_completion(days, daily_minutes, genre)
    
    return render_template(
        "homepage.html",
        daily_recommendations=daily_recommendations,
        full_recommendations=full_recommendations
    )