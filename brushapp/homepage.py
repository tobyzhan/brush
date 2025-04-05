from flask import Blueprint, render_template, request

homepagebp = Blueprint("homepage", __name__)

@homepagebp.route("/", methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        feeling = request.form['feeling']
        hrs = request.form['hrs']
        mins = request.form['mins']
        error = None

        if not feeling:
            error = 'Genre is required.'
        elif not hrs:
            error = 'hrs is required.'
        elif not mins:
            error = 'mins is required.'
    
    print(f"Feeling: {feeling}, Hours: {hrs}, Minutes: {mins}")
    return render_template('homepage.html')