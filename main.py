from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
import math
import re
import requests

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def read_root():
    return {"message": "The Fruit-Tree Brain is Online! Use /search to find trees."}
    
class SearchEngine:
    def __init__(self, k1=1.5, b=0.75):
        self.index = defaultdict(lambda: defaultdict(int))
        self.doc_lengths = {}
        self.k1 = k1
        self.b = b
        self.documents = {}

    def _normalize(self, text):
        return re.findall(r'[a-z0-9]+', text.lower())
    def add_document(self, doc_id, text): 
        terms = self._normalize(text)
        self.documents[doc_id] = text
        self.doc_lengths[doc_id] = len(terms)
        for term in terms:
            self.index[term][doc_id] += 1 
    
    def search(self, query):
        query_terms = self._normalize(query)
        if not query_terms or not self.doc_lengths:
            return []

        scores = defaultdict(float)
        N = len(self.doc_lengths)
        avgdl  = sum(self.doc_lengths.values()) / N
        
        for term in query_terms:
            n_t = len(self.index[term])
            if n_t == 0: continue

            idf = math.log(1 + (N - n_t + 0.5) / (n_t + 0.5))

            for doc_id, tf in self.index[term].items():
                numerator = tf * (self.k1 + 1)
                normalization = (1 - self.b) + self.b * (self.doc_lengths[doc_id] / avgdl)
                denominator = tf + self.k1 * normalization

                scores[doc_id] += idf * (numerator / denominator)
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:20]


engine = SearchEngine()

import json

def load_data():
    try:
        with open('smartview-map-data.geojson', 'r') as f:
            data = json.load(f)
            for feature in data['features']:
                prop = feature['properties']
                engine.add_document(prop.get('id'), prop.get('group', ''))
            print(f"Success! Indexed {len(data['features'])} fruit trees.")
    except Exception as e:
        print(f"Error loading local data: {e}")

load_data()
@app.get("/search")
def search_trees(query: str):
    results = engine.search(query)
    return {"results": results}

