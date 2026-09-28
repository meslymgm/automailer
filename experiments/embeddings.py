from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

sentences = [
    "India launches a new national AI mission",
    "Government announces a new artificial intelligence initiative",
    "Indian technology companies increase AI investments",
    "England wins the cricket match"
]

embeddings = model.encode(sentences)

print(embeddings.shape)

similarities = model.similarity(embeddings, embeddings)

print(similarities)