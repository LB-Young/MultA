"""会话存储（JSON 持久化）"""
import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.domain.entities.query import ConversationSession, ConversationMessage
from src.infrastructure.logging.setup import get_logger

logger = get_logger(__name__)


class SessionRepository:
    """会话仓储"""

    def __init__(self, storage_path: str = "data/sessions.json"):
        configured_path = os.getenv("SESSION_STORAGE_PATH", storage_path)
        self._storage_path = self._resolve_storage_path(configured_path)
        self._sessions: dict[str, dict] = {}
        logger.info(f"会话存储路径: {self._storage_path}")
        self._load()

    @staticmethod
    def _resolve_storage_path(storage_path: str) -> Path:
        path = Path(storage_path)
        if path.is_absolute():
            return path
        project_root = Path(__file__).resolve().parents[3]
        return project_root / path

    def _load(self) -> None:
        if self._storage_path.exists():
            try:
                with open(self._storage_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self._sessions = {
                        sid: self._deserialize_session_dict(sess)
                        for sid, sess in raw.items()
                    }
            except Exception as e:
                logger.warning(f"加载会话数据失败: {e}，将重新创建")
                self._sessions = {}

    def _save(self) -> None:
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            raw = {}
            for sid, sess in self._sessions.items():
                raw[sid] = self._serialize_session_dict(sess)
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败: {e}")

    @staticmethod
    def _ensure_datetime(value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise TypeError(f"invalid datetime value type: {type(value)!r}")

    def _deserialize_session_dict(self, session: dict) -> dict:
        data = deepcopy(session)
        data["created_at"] = self._ensure_datetime(data["created_at"])
        data["updated_at"] = self._ensure_datetime(data["updated_at"])
        for msg in data.get("messages", []):
            msg["created_at"] = self._ensure_datetime(msg["created_at"])
        return data

    def _serialize_session_dict(self, session: dict) -> dict:
        data = deepcopy(session)
        data["created_at"] = self._ensure_datetime(data["created_at"]).isoformat()
        data["updated_at"] = self._ensure_datetime(data["updated_at"]).isoformat()
        for msg in data.get("messages", []):
            msg["created_at"] = self._ensure_datetime(msg["created_at"]).isoformat()
        return data

    # ── 会话 CRUD ──────────────────────────────────────

    def create_session(self, session: ConversationSession) -> ConversationSession:
        self._sessions[session.id] = session.model_dump()
        self._save()
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        raw = self._sessions.get(session_id)
        if raw is None:
            return None
        data = self._deserialize_session_dict(raw)
        return ConversationSession(**data)

    def list_sessions(self, skip: int = 0, limit: int = 50) -> list[ConversationSession]:
        all_sessions = sorted(
            self._sessions.values(),
            key=lambda s: s["updated_at"],
            reverse=True,
        )
        page = all_sessions[skip : skip + limit]
        return [
            ConversationSession(**self._deserialize_session_dict(sess))
            for sess in page
        ]

    def update_session(self, session: ConversationSession) -> ConversationSession:
        self._sessions[session.id] = session.model_dump()
        self._save()
        return session

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save()
            return True
        return False

    def add_message(self, session_id: str, message: ConversationMessage) -> bool:
        session = self.get_session(session_id)
        if session is None:
            return False
        session.messages.append(message)
        session.updated_at = datetime.now()
        self.update_session(session)
        return True


# 全局单例
_session_repo: Optional[SessionRepository] = None
_agent_session_repo: Optional[SessionRepository] = None


def get_session_repository() -> SessionRepository:
    global _session_repo
    if _session_repo is None:
        _session_repo = SessionRepository()
    return _session_repo


def get_agent_session_repository() -> SessionRepository:
    """获取 Agent 会话仓储（与知识问答会话分开存储）。"""
    global _agent_session_repo
    if _agent_session_repo is None:
        _agent_session_repo = SessionRepository(storage_path="data/agent_sessions.json")
    return _agent_session_repo
