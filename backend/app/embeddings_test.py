from langchain_huggingface import HuggingFaceEmbeddings


# --------------------------------
# 1. Load embedding model
# --------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# --------------------------------
# 2. Text to embed
# --------------------------------

text = """
Complexity is the number of steps required
to solve a problem.
"""


# --------------------------------
# 3. Create embedding
# --------------------------------

vector = embeddings.embed_query(text)


# --------------------------------
# 4. Display result
# --------------------------------

print("Vector type:", type(vector))
print("Vector dimensions:", len(vector))

print("\nFirst 10 values:")
print(vector[:10])