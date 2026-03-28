from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from agent.payments.types import (
    PaymentChallenge,
    PaymentCredential,
    PaymentReceipt,
    PaymentSessionHandle,
)


class PaymentAdapter(Protocol):
    adapter_name: str

    def supports_response(self, response: Any) -> bool: ...

    def parse_challenge(self, response: Any, request: Dict[str, Any]) -> PaymentChallenge: ...

    def build_credential(
        self,
        challenge: PaymentChallenge,
        request: Dict[str, Any],
        session: Optional[PaymentSessionHandle],
        runtime_config: Dict[str, Any],
    ) -> PaymentCredential: ...

    def extract_receipt(self, response: Any) -> Optional[PaymentReceipt]: ...

    def update_session(
        self,
        challenge: PaymentChallenge,
        receipt: Optional[PaymentReceipt],
        prior_session: Optional[PaymentSessionHandle],
    ) -> Optional[PaymentSessionHandle]: ...


@dataclass
class MPPAdapter:
    adapter_name: str = "mpp"

    @staticmethod
    def _response_headers(response: Any) -> Dict[str, Any]:
        source = getattr(response, "response", None) or response
        headers = getattr(source, "headers", None)
        if isinstance(headers, dict):
            return headers
        return {}

    @staticmethod
    def _response_body(response: Any) -> Dict[str, Any]:
        source = getattr(response, "response", None) or response
        payload = getattr(source, "json", None)
        if not callable(payload):
            return {}
        try:
            data = payload()
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    def supports_response(self, response: Any) -> bool:
        status_code = getattr(response, "status_code", None)
        if status_code == 402:
            return True
        nested_response = getattr(response, "response", None)
        return getattr(nested_response, "status_code", None) == 402

    def parse_challenge(self, response: Any, request: Dict[str, Any]) -> PaymentChallenge:
        endpoint = str(request.get("base_url") or "")
        payment_config = request.get("payment_config") or {}
        headers = self._response_headers(response)
        body = self._response_body(response)
        intent = (
            headers.get("X-MPP-Intent")
            or body.get("intent")
            or payment_config.get("intent")
            or "session"
        )
        method = (
            headers.get("X-MPP-Method")
            or body.get("method")
            or payment_config.get("method")
            or "unknown"
        )
        return PaymentChallenge(
            adapter=self.adapter_name,
            intent=str(intent),
            endpoint=endpoint,
            method=str(method),
            raw={"response": response, "headers": headers, "body": body},
        )

    def build_credential(
        self,
        challenge: PaymentChallenge,
        request: Dict[str, Any],
        session: Optional[PaymentSessionHandle],
        runtime_config: Dict[str, Any],
    ) -> PaymentCredential:
        payment_config = runtime_config.get("payment_config") or {}
        headers: Dict[str, str] = {}
        if session and isinstance(session.state.get("headers"), dict):
            headers = {
                str(k): str(v)
                for k, v in session.state["headers"].items()
                if isinstance(k, str) and v is not None and str(v).strip()
            }
            if headers:
                return PaymentCredential(headers=headers)
        credential_factory = runtime_config.get("payment_credential_factory")
        if callable(credential_factory):
            headers = credential_factory(
                challenge=challenge,
                request=request,
                session=session,
                runtime_config=runtime_config,
            ) or {}
        elif isinstance(payment_config.get("credential_headers"), dict):
            headers = {
                str(k): str(v)
                for k, v in payment_config["credential_headers"].items()
                if isinstance(k, str) and v is not None and str(v).strip()
            }
        return PaymentCredential(headers=headers)

    def extract_receipt(self, response: Any) -> Optional[PaymentReceipt]:
        headers = self._response_headers(response)
        body = self._response_body(response)
        receipt_id = headers.get("X-MPP-Receipt-Id") or body.get("receipt_id")
        session_id = headers.get("X-MPP-Session-Id") or body.get("session_id")
        verified_raw = headers.get("X-MPP-Receipt-Verified")
        if verified_raw is None:
            verified_raw = body.get("verified")
        if receipt_id is None and session_id is None:
            return None
        verified = str(verified_raw).strip().lower() in {"1", "true", "yes", "on"}
        return PaymentReceipt(
            receipt_id=str(receipt_id) if receipt_id is not None else None,
            session_id=str(session_id) if session_id is not None else None,
            raw={"headers": headers, "body": body},
            verified=verified,
        )

    def update_session(
        self,
        challenge: PaymentChallenge,
        receipt: Optional[PaymentReceipt],
        prior_session: Optional[PaymentSessionHandle],
    ) -> Optional[PaymentSessionHandle]:
        if challenge.intent != "session":
            return prior_session

        raw_headers = challenge.raw.get("headers") or {}
        raw_body = challenge.raw.get("body") or {}
        session_id = (
            (receipt.session_id if receipt else None)
            or raw_headers.get("X-MPP-Session-Id")
            or raw_body.get("session_id")
            or (prior_session.session_id if prior_session else None)
        )
        state = dict(prior_session.state) if prior_session else {}
        if receipt and receipt.receipt_id:
            state["receipt_id"] = receipt.receipt_id
        if not state.get("headers"):
            state["headers"] = {}
        return PaymentSessionHandle(
            adapter=self.adapter_name,
            endpoint_key=str(challenge.endpoint),
            session_id=str(session_id) if session_id is not None else None,
            method=challenge.method,
            expires_at=prior_session.expires_at if prior_session else None,
            state=state,
        )


def build_payment_adapter(name: Optional[str]) -> Optional[PaymentAdapter]:
    if name == "mpp":
        return MPPAdapter()
    return None


def build_payment_session_key(runtime: Dict[str, Any], model: str) -> str:
    provider = str(runtime.get("provider") or "")
    base_url = str(runtime.get("base_url") or "")
    payment_config = runtime.get("payment_config") or {}
    method = str(payment_config.get("method") or "")
    return f"{provider}|{base_url}|{model}|{method}"
