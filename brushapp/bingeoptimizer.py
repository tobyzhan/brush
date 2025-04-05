#THIS IS FROM CHATGPT, IT DOESN'T DO ANYTHING YET!!!!:

import requests

def search_movie(title):
    query = f"""
    {{
      movies(search: "{title}") {{
        name
        year
        rating
        genres
      }}
    }}
    """
    url = "https://graph.imdbapi.dev/v1"
    response = requests.post(url, json={'query': query})
    return response.json()