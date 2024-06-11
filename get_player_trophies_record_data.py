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

json_private_key = json.loads(json_private_key.strip())
cred = credentials.Certificate(json_private_key)
firebase_admin.initialize_app(cred)
db = firestore.client()
for doc in db.collection('player_tag').stream():
    player = doc.reference.get().to_dict()
    print(f"Chuỗi cúp của player {doc.id} {player['name']}")
    trophies = player['trophies_ref_first'].get().to_dict()
    while 1:
        print(trophies['trophies'], end=' ')
        if trophies['next_ref'] == None:
            break
        trophies = trophies['next_ref'].get().to_dict()
    print()