import requests
import json
import pytest


def test1():

    url = 'http://127.0.0.1:5000/api/weather'
    headers = {'Content-Type': 'application/json'}

    payload = {"location": "USC00110072", "date": "19850101"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    print(response)
    
    assert response.status_code == 200
        

def test2():
    url = 'http://127.0.0.1:5000/api/weather/stats'
    headers = {'Content-Type': 'application/json'}

    payload = {"location": "USC00110072", "date": "1985"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    assert response.status_code == 200
