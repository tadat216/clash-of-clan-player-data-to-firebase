import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import os
import json

api_url = 'https://developer.clashofclans.com/api/'
api_token = None

try:
    email = os.environ["SECRET_EMAIL"]
except KeyError:
    email = None

try:
    password = os.environ["SECRET_PASS"]
except KeyError:
    password = None

login_payload = {
    "email": email,
    "password": password
}

session = requests.Session()
login_response = session.post(api_url+'login', json=login_payload)
api_token = login_response.json().get('temporaryAPIToken')
headers = {
        "authorization": f"Bearer {api_token}",
        "Accept": "application/json"
}

def get_player_data(tag:str):
    player_data = requests.get(f'https://api.clashofclans.com/v1/players/%23{tag}', headers=headers)
    return player_data.json()

try:
    json_private_key = os.environ["JSON_PRIVATE_KEY"]
except KeyError:
    json_private_key = None

json_private_key = json.loads(json_private_key.strip())

cred = credentials.Certificate(json_private_key)
firebase_admin.initialize_app(cred)

db = firestore.client()

def add_player_data_to_firebase(tag:str, ref):
    p =  get_player_data(tag)
    player_data = ref.get().to_dict()
    trophies_ref_last = player_data['trophies_ref_last']
    doc_last = trophies_ref_last.get().to_dict()
    if doc_last['trophies'] != p['trophies']:
        new_data = {
            'trophies' : p['trophies'],
            'player_ref' : ref, 
            'next_ref' : None,
            'prev_ref' : trophies_ref_last,
            'time_stamp' : datetime.now().isoformat()
        }
        trophies_col = db.collection('trophies_data')
        time_stamp, new_ref = trophies_col.add(new_data)
        trophies_ref_last.update({'next_ref' : new_ref})
        ref.update({'trophies_ref_last' : new_ref})

def update_database():
    colection = db.collection('player_tag')
    tags = [doc.id for doc in colection.stream()]
    for tag in tags:
        add_player_data_to_firebase(tag, colection.document(tag))

if __name__ == "__main__":
    update_database()