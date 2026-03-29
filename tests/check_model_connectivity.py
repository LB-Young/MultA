"""
三合一客户端示例（在另一台电脑运行）
将 SERVER_IP 改为服务端 Tailscale IP
"""

import httpx
from openai import OpenAI

SERVER_IP = "100.117.128.23"   # ← 改为服务端 Tailscale IP

CHAT_URL      = f"http://{SERVER_IP}:8000"
EMBEDDING_URL = f"http://{SERVER_IP}:8001"
RERANKER_URL  = f"http://{SERVER_IP}:8002"


# ══════════════════════════════════════════════
# 1. Chat（复用 OpenAI SDK）
# ══════════════════════════════════════════════
def demo_chat():
    print("=" * 60)
    print("【Chat 示例】")
    client = OpenAI(base_url=f"{CHAT_URL}/v1", api_key="not-needed")
    stream = client.chat.completions.create(
        model="qwen3-5-4b",
        messages=[{"role": "user", "content": "用一句话解释向量数据库的原理。"}],
        stream=True,
    )
    print("Assistant: ", end="", flush=True)
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="", flush=True)
    print()


# ══════════════════════════════════════════════
# 2. Embedding
# ══════════════════════════════════════════════
def demo_embedding():
    print("=" * 60)
    print("【Embedding 示例】")
    with httpx.Client(timeout=60) as client:
        # Query 侧（自动加 instruction 前缀）
        resp = client.post(
            f"{EMBEDDING_URL}/v1/embeddings",
            json={
                "input": ["向量数据库怎么工作？", "什么是语义检索？"],
                "is_query": True,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"返回 {len(data['data'])} 条 embedding，维度: {len(data['data'][0]['embedding'])}")

        # 文档侧（不加 instruction）
        resp = client.post(
            f"{EMBEDDING_URL}/v1/embeddings",
            json={
                "input": "向量数据库将文本转成高维向量并通过近似最近邻索引实现快速检索。",
                "is_query": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        print(f"单条文档 embedding 维度: {len(data['data'][0]['embedding'])}")


# ══════════════════════════════════════════════
# 3. Rerank
# ══════════════════════════════════════════════
def demo_rerank():
    print("=" * 60)
    print("【Rerank 示例】")
    query = "向量数据库的工作原理"
    documents = [
        "向量数据库将文本转成高维向量并通过近似最近邻索引实现快速检索。",
        "今天天气晴朗，适合出门散步。",
        "FAISS 是 Meta 开源的高效向量相似度搜索库。",
        "Python 是一种广泛使用的编程语言。",
    ]
    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{RERANKER_URL}/v1/rerank",
            json={
                "query": query,
                "documents": documents,
                "top_n": 3,
                "return_documents": True,
            },
        )
        resp.raise_for_status()
        result = resp.json()

    print(f"Query: {query}")
    print("Top-3 结果（按相关性降序）:")
    for item in result["results"]:
        print(f"  [{item['index']}] score={item['relevance_score']:.4f}  {item['document'][:40]}...")


# ══════════════════════════════════════════════
if __name__ == "__main__":
    demo_chat()
    print()
    demo_embedding()
    print()
    demo_rerank()
