import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import os
import json


try:
    json_private_key = os.environ["JSON_PRIVATE_KEY"]
except KeyError:
    json_private_key = None

print("ok")
print(json_private_key)
json_private_key = json.loads(json_private_key)

cred = credentials.Certificate(json_private_key)

db = firestore.client()

class Player:
    def __init__(self, tag:str, name:str, trophies:int, league:str, time_stamp:datetime):
        self.tag = tag
        self.name = name
        self.trophies = trophies
        self.league = league
        self.time_stamp = time_stamp

    def to_dict(self):
        return {
            'tag' : self.tag,
            'name' : self.name,
            'trophies' : self.trophies,
            'league' : self.league,
            'time_stamp' : self.time_stamp.isoformat()
        }

    def to_data_tuple(self):
        return (
            self.trophies,
            self.league,
            self.time_stamp
        )
try:
    token = os.environ["TOKEN"]
except:
    token = None

headers = {
    "Accept" : "application/json",
    "authorization" : f"Bearer {token}"
}

def get_player_data(tag):
    url = f"https://api.clashofclans.com/v1/players/%23{tag}"
    response = requests.get(url, headers=headers) 
    return response.json()

def add_player_data_to_firebase(tag:str):

    p = get_player_data(tag)
    player = Player(p["tag"], p["name"], p["trophies"], p["league"]["name"], datetime.now())
    doc_ref = db.collection('players').document(player.tag)
    doc = doc_ref.get()
   
    if doc.exists:
        data = doc.to_dict()
        trophies = data.get('trophies', [])
        
        if trophies[-1] != player.trophies:
            leagues = data.get('leagues', [])
            leagues.append(player.league)
            time_stamps = data.get('time_stamps', [])
            trophies.append(player.trophies)
            time_stamps.append(player.time_stamp)
            doc_ref.update({
                'trophies' : trophies,
                'leagues' : leagues,
                'time_stamps' : time_stamps
            })
    else:
        doc_ref.set({
            'name':player.name,
            'trophies' : [player.trophies],
            'leagues' : [player.league],
            'time_stamps' : [player.time_stamp]
        })

def update_database():
    doc_ref = db.collection('player_tag').document('data')
    doc = doc_ref.get()
    data = doc.to_dict()
    tags = data.get('tags', [])
    for tag in tags:
        add_player_data_to_firebase(tag)
    print("Đã cập nhật thành công!")

if __name__ == "__main__":
    update_database()