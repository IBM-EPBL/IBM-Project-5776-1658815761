import requests

BASE = "http://127.0.0.1:5000/"

data = [{"name" : "test123", "email" : "test123@gmail.com", "password" : "test123"},
        {"name" : "test156", "email" : "test156@gmail.com", "password" : "test156"},
        {"name" : "test699", "email" : "test699@gmail.com", "password" : "test699"}]


for i in range(len(data)):
    response = requests.put(BASE + "account/" + str(i), data[i])
    print(response.json())

input()
response = requests.delete(BASE + "account/0")
print(response)
input()
response = requests.get(BASE + "account/2")
print(response.json())