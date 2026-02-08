import hashlib
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Protocol

import numpy as np
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# 得到项目所在绝对路径
basic_dir = Path(__file__).resolve().parent.parent

# 读取 FAQ 文本文件
with open(f"{basic_dir}/order_faq.md", encoding="utf8") as f:
    faq_text = f.read()

# 将 FAQ 文本按标题分割成多个文档
docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]


class EmbeddingsModel(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        ...

    def embed_query(self, text: str) -> list[float]:
        ...


class HashEmbeddings:
    """No-network deterministic embedding fallback for local development."""

    dim = 256

    @staticmethod
    def _vectorize(text: str) -> list[float]:
        base = [0.0] * HashEmbeddings.dim
        if not text:
            return base
        encoded = text.encode("utf-8", errors="ignore")
        digest = hashlib.sha256(encoded).digest()
        for idx, value in enumerate(digest):
            base[idx % HashEmbeddings.dim] += (value / 255.0) - 0.5
        return base

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vectorize(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vectorize(text)


def _build_embeddings_model() -> EmbeddingsModel:
    api_key = os.getenv("EMBEDDINGS_API_KEY") or os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("EMBEDDINGS_API_BASE") or os.getenv("OPENAI_API_BASE")

    if api_key and api_base:
        return OpenAIEmbeddings(openai_api_key=api_key, openai_api_base=api_base)
    return HashEmbeddings()


# 定义向量存储检索器类
class VectorStoreRetriever:
    def __init__(self, docs: list, vectors: list):
        # 存储文档和对应的向量
        self._arr = np.array(vectors)
        self._docs = docs
        self._embeddings_model = _build_embeddings_model()

    @classmethod
    def from_docs(cls, docs):
        # 从文档生成嵌入向量
        embeddings_model = _build_embeddings_model()
        vectors = embeddings_model.embed_documents([doc["page_content"] for doc in docs])
        instance = cls(docs, vectors)
        instance._embeddings_model = embeddings_model
        return instance

    def query(self, query: str, k: int = 5) -> list[dict]:
        # 对查询生成嵌入向量
        embed = self._embeddings_model.embed_query(query)
        # 计算查询向量与文档向量的相似度
        scores = np.array(embed) @ self._arr.T
        # 获取相似度最高的 k 个文档的索引
        top_k = min(k, len(self._docs))
        top_k_idx = np.argpartition(scores, -top_k)[-top_k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        # 返回相似度最高的 k 个文档及其相似度
        return [
            {**self._docs[idx], "similarity": float(scores[idx])} for idx in top_k_idx_sorted
        ]


@lru_cache(maxsize=1)
def _get_retriever() -> VectorStoreRetriever:
    return VectorStoreRetriever.from_docs(docs)


# 定义工具函数，用于查询航空公司的政策
@tool
def lookup_policy(query: str) -> str:
    """查询公司政策，检查某些选项是否允许。
    在进行航班变更或其他'写'操作之前使用此函数。"""
    # 查询相似度最高的 k 个文档
    matched_docs = _get_retriever().query(query, k=2)
    # 返回这些文档的内容
    return "\n\n".join([doc["page_content"] for doc in matched_docs])


if __name__ == '__main__':  # 测试代码
    print(lookup_policy('怎么才能退票呢？'))
