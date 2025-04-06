from flask import Blueprint, render_template, request
from brushapp.recommender import recommend_daily_binge, recommend_full_completion
from brushapp.apikeys import GOOGLE_API_KEY
import requests

homepagebp = Blueprint("homepage", __name__)

@homepagebp.route("/", methods=["GET", "POST"])
def homepage():
    daily_recommendations = []
    full_recommendations = []
    daily_image_urls = []
    full_image_urls = []
    
    if request.method == "POST":
        form_type = request.form.get("form_type")
        genre = request.form.get("genre", "").strip() or None
        
        global GOOGLE_API_KEY
        API_KEY = GOOGLE_API_KEY
        url = f"https://www.googleapis.com/customsearch/v1"


        if form_type == "daily":
            time_limit = int(request.form.get("time_limit", 0))
            if time_limit > 0:
                daily_recommendations = recommend_daily_binge(time_limit, genre)
            for rec in daily_recommendations:
                params = {
                    'q': f"{rec['title']} tv series",                # Search query
                    'key': API_KEY,            # API Key
                    'cx': "56ba96eb07f3442bf",                  # Custom Search Engine ID
                    'searchType': 'image',     # Specify we want image results
                    'num': 1                   # Return only the first image result
                }
                response = requests.get(url, params=params)
                data = response.json()
                daily_image_urls.append(data['items'][0]['link'])
                
        elif form_type == "full":
            days = int(request.form.get("days", 0))
            daily_minutes = int(request.form.get("daily_minutes", 0))
            if days > 0 and daily_minutes > 0:
                full_recommendations = recommend_full_completion(days, daily_minutes, genre)
            for rec in full_recommendations:
                params = {
                    'q': f"{rec['seriesTitle']} tv series",                # Search query
                    'key': API_KEY,            # API Key
                    'cx': "56ba96eb07f3442bf",                  # Custom Search Engine ID
                    'searchType': 'image',     # Specify we want image results
                    'num': 1                   # Return only the first image result
                }
                response = requests.get(url, params=params)
                data = response.json()
                full_image_urls.append(data['items'][0]['link'])
    
    return render_template(
        "homepage.html",
        daily_recommendations=daily_recommendations,
        full_recommendations=full_recommendations,
        daily_recommendation_data=list(zip(daily_recommendations, daily_image_urls)),
        full_recommendation_data=list(zip(full_recommendations, full_image_urls))
    )
