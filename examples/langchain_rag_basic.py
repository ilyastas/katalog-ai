# examples/langchain_rag_basic.py
# Простой RAG на katalog-ai (загружаем JSON → чанк → векторный store → retrieval)

from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # или HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# 1. Загрузка всего каталога (или используй HF версию)
loader = JSONLoader(
    file_path="https://raw.githubusercontent.com/ilyastas/katalog-ai/main/data/ai-catalog.json",
    jq_schema=".[]",  # каждый элемент массива — документ
    text_content=False
)
docs = loader.load()

# 2. Чанки + эмбеддинги
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()  # или бесплатные HuggingFaceEmbeddings
vectorstore = FAISS.from_documents(splits, embeddings)

# 3. Retrieval + LLM
llm = ChatOpenAI(model="gpt-4o-mini")
qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

# Тест
question = "Найди салоны красоты в Алматы"
result = qa_chain.invoke({"query": question})
print(result["result"])
