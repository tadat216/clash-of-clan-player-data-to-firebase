import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import os
import json
import coc
import asyncio

try:
    email = os.environ["SECRET_EMAIL"]
except KeyError:
    email = None

try:
    password = os.environ["SECRET_PASS"]
except KeyError:
    password = None

async def login_async():
    await client.login(email=email, password=password)

async def get_player_data(tag):
    player_data = await client.get_player(tag)
    return player_data

try:
    json_private_key = os.environ["JSON_PRIVATE_KEY"]
except KeyError:
    json_private_key = None

json_private_key = json.loads(json_private_key.strip())

cred = credentials.Certificate(json_private_key)
firebase_admin.initialize_app(cred)

db = firestore.client()

client = coc.Client()

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

async def add_player_data_to_firebase(tag:str, ref):
    p =  await get_player_data(tag)
    player_data = ref.get().to_dict()
    trophies_ref_last = player_data['trophies_ref_last']
    doc_last = trophies_ref_last.get().to_dict()
    if doc_last['trophies'] != p.trophies:
        new_data = {
            'trophies' : p.trophies,
            'player_ref' : ref, 
            'next_ref' : None,
            'prev_ref' : trophies_ref_last,
            'time_stamp' : datetime.now().isoformat()
        }
        trophies_col = db.collection('trophies_data')
        time_stamp, new_ref = trophies_col.add(new_data)
        trophies_ref_last.update({'next_ref' : new_ref})

async def update_database():
    await login_async()
    colection = db.collection('player_tag')
    tags = [doc.id for doc in colection.stream()]
    for tag in tags:
        await add_player_data_to_firebase(tag, colection.document(tag))
    await client.close()

if __name__ == "__main__":
    asyncio.run(update_database())