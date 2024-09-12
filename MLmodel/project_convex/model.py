from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.llama_cpp import LlamaCPP

# Load your documents and build the index
def load_documents_and_create_index(folder_path):
    documents = SimpleDirectoryReader(folder_path).load_data()
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")  # Your embedding model
    return VectorStoreIndex.from_documents(documents, embed_model=embed_model)

llm = LlamaCPP(
    # you can set the path to a pre-downloaded model instead of model_url
    model_path="./MLmodel/project_convex/Main-Model-7.2B-Q5_K_M.gguf",
)

def predict(question):
    # Set up the query engine and run the query
    DOCUMENT_FOLDER = './MLmodel/project_convex/documents'
    index = load_documents_and_create_index(DOCUMENT_FOLDER)
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(question)

    # Return the model's response
    return response
