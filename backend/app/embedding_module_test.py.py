from embeddings import get_embeddings


print("Loading embedding model...")

embeddings = get_embeddings()

print("Embedding model loaded successfully!")


text = "What is time complexity?"

vector = embeddings.embed_query(text)


print("\n===================================")
print("EMBEDDING TEST")
print("===================================")

print("Text:")
print(text)

print("\nVector dimensions:")
print(len(vector))

print("\nFirst 10 values:")
print(vector[:10])