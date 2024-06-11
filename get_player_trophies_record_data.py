import requests
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import os

# for key, value in os.environ.items():
#     print(f'{key}: {value}')
#
try:
    json_private_key = os.environ["JSON_PRIVATE_KEY"]
except KeyError:
    json_private_key = None
print(json_private_key)