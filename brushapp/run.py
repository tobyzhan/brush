from brushapp import create_app
from flask import request

app = create_app()

#For logging:
@app.before_request
def log_request():
    # Log the full request headers
    print(f"Incoming request method: {request.method}")
    print(f"Request URL: {request.url}")
    print("Request Headers:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")

if __name__ == "__main__":
    app.run(debug=True)