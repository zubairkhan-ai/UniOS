from langchain_huggingface import HuggingFaceEmbeddings


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME
    )

    return embeddings