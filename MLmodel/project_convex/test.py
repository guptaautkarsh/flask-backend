import requests

# URL of the stream route
url = 'http://127.0.0.1:5000/stream'  # Adjust this to match your Flask app URL if needed

# Make a GET request to the Flask stream route
response = requests.get(url, stream=True)

# Process the streamed response in chunks
if response.status_code == 200:
    for chunk in response.iter_content(chunk_size=1024):
        if chunk:  # Filter out keep-alive new lines
            print(chunk.decode('utf-8'), end='')
else:
    print(f"Error: {response.status_code}")