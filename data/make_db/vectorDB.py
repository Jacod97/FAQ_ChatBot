from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm
import pandas as pd
import openai
import chromadb

load_dotenv()

df = pd.read_csv("../faq.csv", encoding='utf-8')

questions = df["question"].fillna("").tolist()
answers = df["answer"].fillna("").tolist()
q_types = df["q_type"].fillna("").tolist()
keywords = df["keyword"].fillna("").tolist()

def text_embedding(texts, model="text-embedding-3-small"):
    embeddings = []
    for text in tqdm(texts):
        response = openai.embeddings.create(input=text, model=model)
        embeddings.append(response.data[0].embedding)
    return embeddings

embeddings = text_embedding(questions)

persist_path = "../chroma"  

client = chromadb.PersistentClient(path=persist_path)

collection = client.get_or_create_collection(name="try1")

ids = [f"faq-{i}" for i in range(len(questions))]

collection.add(
    documents=questions,
    embeddings=embeddings,
    metadatas=[
        {"answer": a, "q_type": t}
        for a, t in zip(answers, q_types)
    ],
    ids=ids  
)

print(f"저장 완료: {len(questions)}건")