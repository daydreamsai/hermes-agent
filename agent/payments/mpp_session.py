from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from agent.payments.types import PaymentSessionHandle


@dataclass
class PaymentSessionStore:
    _sessions: Dict[str, PaymentSessionHandle] = field(default_factory=dict)

    def get(self, key: str) -> Optional[PaymentSessionHandle]:
        return self._sessions.get(key)

    def set(self, key: str, session: PaymentSessionHandle) -> None:
        self._sessions[key] = session

    def invalidate(self, key: str) -> None:
        self._sessions.pop(key, None)

