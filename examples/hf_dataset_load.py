# examples/hf_dataset_load.py
from datasets import load_dataset

ds = load_dataset("ilyastas/katalog-ai")
print(f"Количество компаний: {len(ds['train'])}")
print(ds['train'][0])  # первая запись
