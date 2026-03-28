from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class PaymentChallenge:
    adapter: str
    intent: str
    endpoint: str
    method: str
    raw: Dict[str, Any]
    retryable: bool = True


@dataclass
class PaymentCredential:
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PaymentReceipt:
    receipt_id: Optional[str]
    session_id: Optional[str]
    raw: Dict[str, Any]
    verified: bool = False


@dataclass
class PaymentSessionHandle:
    adapter: str
    endpoint_key: str
    session_id: Optional[str]
    method: str
    expires_at: Optional[float]
    state: Dict[str, Any] = field(default_factory=dict)

