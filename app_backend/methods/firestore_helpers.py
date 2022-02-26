import json

import firebase_admin
from firebase_admin import auth
from google.cloud import firestore

db = firestore.Client()

def delete_document_and_sub_collections(docRef):
        for collectionRef in docRef.collections():
            for doc in collectionRef.stream():
                delete_document_and_sub_collections(doc.reference)

        docRef.delete()