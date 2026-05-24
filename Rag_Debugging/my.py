from dotenv import load_dotenv
import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("OpenAI API Key not found.")
    exit()

if not os.path.exists("company_docs.txt"):
    print("company_docs.txt file not found.")
    exit()

print("\nLoading document...\n")

loader = TextLoader("company_docs.txt")

documents = loader.load()

text_splitter = CharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = text_splitter.split_documents(documents)

print(f"Total chunks created: {len(docs)}")

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

print("\nRAG System Ready!")
print("Type 'exit' to quit.\n")

while True:

    question = input("Ask a question: ")

    if question.lower() == "exit":
        print("\nGoodbye.\n")
        break

    try:

        result = qa_chain.invoke({
            "query": question
        })

        print("\nAnswer:\n")

        print(result["result"])

        print("\nSources:\n")

        for i, doc in enumerate(result["source_documents"]):

            print(f"Source {i + 1}:\n")

            print(doc.page_content[:300])

            print("\n----------------------\n")

    except Exception as e:

        print(f"\nError: {str(e)}\n")