import requests
from main import create_session

current = create_session("shruti", 400)
# current.username = "shruti"

def create(name):
    response = requests.post(f"http://127.0.0.1:8000/create_session/{name}")
    print(response.json())

def who():
    response = requests.get(f"http://127.0.0.1:8000/whoami")
    print(response.json())
    return response.json()

def delete():
    response = requests.post(f"http://127.0.0.1:8000/delete_session")
    print(response.json())
    return response.json()

# create("hello")
who()
delete()
