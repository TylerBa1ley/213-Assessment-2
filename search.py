from collections import defaultdict


index = defaultdict(lambda: defaultdict(int))

for doc_id, text in documents.items():
    for word in text.lower().split():
        index[word][doc_id] += 1
for word in text.lower().strip().split(): 
    index[word].add(doc_id)    


search_term = "apple"
print(f"'{search_term}' appears in: {index[search_term]}")

