import requests

def check_recipe_url(url):
    response = requests.head(url)
    print(response)
    return response.status_code == 200

def generate_recipe_urls(start_id, end_id):
    base_url = "https://www.ah.nl/allerhande/recept/R-R119"
    urls = []
    for i in range(start_id, end_id + 1):
        url = f"{base_url}{i}"
        if check_recipe_url(url):
            urls.append(url)
    return urls

start_id = 9000  # Adjust start ID as needed
end_id = 9020    # Adjust end ID as needed
recipe_urls = generate_recipe_urls(start_id, end_id)
print(len(recipe_urls))

