import requests


def fetch_patient_info():
    response = requests.get('http://localhost:5000/data')
    if response.status_code == 200:
        return response.json()
    return None
