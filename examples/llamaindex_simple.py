# examples/llamaindex_simple.py
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.readers.json import JSONReader

# Загрузка
documents = JSONReader().load_data("https://raw.githubusercontent.com/ilyastas/katalog-ai/main/data/ai-catalog.json")

# Индекс
index = VectorStoreIndex.from_documents(documents)

# Запрос
query_engine = index.as_query_engine()
response = query_engine.query("Какие есть проверенные бизнесы по ремонту в Астане?")
print(response)
