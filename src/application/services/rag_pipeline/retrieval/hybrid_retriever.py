"""混合召回策略（稠密分数 + 关键词分数融合）。"""
import re

from .dense_retriever import DenseRetriever


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"\w+", (text or "").lower()) if len(t) > 1}


class HybridRetriever(DenseRetriever):
    strategy_name = "hybrid"

    def __init__(self, collection_name: str, store, alpha: float = 0.7):
        super().__init__(collection_name, store)
        self.alpha = alpha

    async def retrieve(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int,
        filters: dict,
    ):
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

        max_dense = max((c.score for c in dense_candidates), default=1.0) or 1.0
        scored = []
        for c in dense_candidates:
            content_terms = _tokenize(c.chunk.content)
            sparse_score = len(query_terms & content_terms) / max(len(query_terms), 1)
            dense_score = c.score / max_dense
            hybrid_score = self.alpha * dense_score + (1 - self.alpha) * sparse_score
            scored.append((hybrid_score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]
