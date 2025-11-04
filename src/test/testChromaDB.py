import chromadb
client = chromadb.Client() 
collection = client.create_collection("test")
collection.add(ids=["1"], documents=["This is a test document."])
print(collection.query(query_texts=["test"], n_results=1))
