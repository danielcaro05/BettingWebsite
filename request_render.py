import requests

# Your Render website URL
RENDER_URL = "https://bettingwebsite-599p.onrender.com"

def make_request():
    try:
        # Make the GET request to the Render website
        response = requests.get(RENDER_URL)
        # Print the response status code and a snippet of the content
        print(f"Request successful: {response.status_code}")
        print(f"Response snippet: {response.text[:100]}...")  # First 100 characters
    except requests.exceptions.RequestException as e:
        # Handle errors
        print(f"Request failed: {e}")

if __name__ == "__main__":
    make_request()
