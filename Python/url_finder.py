import requests
import pickle

def urls_list():
    url_list = []
    base_string = 'https://www.ah.nl/allerhande/recept/R-R119'

    for i in range(9000, 9999):
        url = base_string + str(i)
        print(i)
        print(requests.head(url).status_code)
        print(url)
        if requests.head(url).status_code == 301 or requests.head(url).status_code == 200:      # If valid
            url_list.append(url)

    file_path = 'urls.pkl'
    with open(file_path, 'wb') as file:
        pickle.dump(url_list, file)
    return url_list


test = urls_list()
print(len(test))