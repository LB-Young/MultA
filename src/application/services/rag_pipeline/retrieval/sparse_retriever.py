"""稀疏召回策略（关键词匹配重排序）。"""
import re

from .dense_retriever import DenseRetriever


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"\w+", (text or "").lower()) if len(t) > 1}


class SparseRetriever(DenseRetriever):
    strategy_name = "sparse"

    async def retrieve(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int,
        filters: dict,
    ):
        # 先做更宽的候选召回，再按关键词重排模拟稀疏策略。
        dense_candidates = await self.store.search(
            self.collection_name,
            query_vector,
            top_k=max(top_k * 4, 10),
            filters=filters,
        )
        if not dense_candidates:
            return []

        query_terms = _tokenize(query_text)
        if not query_terms:
            return dense_candidates[:top_k]

        scored = []
        for c in dense_candidates:
            content_terms = _tokenize(c.chunk.content)
            overlap = len(query_terms & content_terms)
            score = overlap / max(len(query_terms), 1)
            scored.append((score, c))

        scored.sort(key=lambda x: (x[0], x[1].score), reverse=True)
        return [item[1] for item in scored[:top_k]]
