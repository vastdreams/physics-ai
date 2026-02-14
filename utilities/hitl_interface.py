"""
Human-in-the-Loop (HITL) Interface.

Inspired by DREAM architecture - audit and oversight interfaces.

First Principle Analysis:
- HITL requests: Request human input for critical decisions
- Approval flows: Require human approval before execution
- Audit logging: Track all human interventions
- Mathematical foundation: Decision theory, approval workflows
- Architecture: Modular interface with async support
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from loggers.system_logger import SystemLogger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_TIMEOUT_SECONDS = 3600  # 1 hour


class ApprovalStatus(Enum):
    """Approval status for HITL requests."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class HITLRequest:
    """Represents a HITL request."""

    request_id: str
    action: str
    description: str
    context: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    response: Optional[Dict[str, Any]] = None
    timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS


class HITLInterface:
    """Human-in-the-Loop interface for audit and oversight.

    Features:
    - Request human input for critical decisions
    - Approval workflows
    - Audit logging
    - Timeout handling
    """

    def __init__(self) -> None:
        """Initialize HITL interface."""
        self._logger = SystemLogger()
        self.requests: Dict[str, HITLRequest] = {}
        self.request_counter = 0
        self.approval_callbacks: Dict[str, Callable[..., Any]] = {}

        self._logger.log("HITLInterface initialized", level="INFO")

    def request_approval(
        self,
        action: str,
        description: str,
        context: Dict[str, Any],
        timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS,
        callback: Optional[Callable[..., Any]] = None,
    ) -> str:
        """Request human approval for an action.

        Args:
            action: Action description.
            description: Detailed description.
            context: Action context.
            timeout_seconds: Timeout in seconds.
            callback: Optional callback when approved/rejected.

        Returns:
            Request ID.
        """
        self.request_counter += 1
        request_id = f"hitl_{self.request_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        request = HITLRequest(
            request_id=request_id,
            action=action,
            description=description,
            context=context,
            timeout_seconds=timeout_seconds,
        )

        self.requests[request_id] = request

        if callback:
            self.approval_callbacks[request_id] = callback

        self._logger.log(f"HITL approval requested: {request_id} - {action}", level="INFO")
        self._notify_human(request)
        return request_id

    def approve(
        self,
        request_id: str,
        approved_by: str,
        response: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Approve a request.

        Args:
            request_id: Request ID.
            approved_by: Approver identifier.
            response: Optional response data.

        Returns:
            True if approved successfully.
        """
        if request_id not in self.requests:
            self._logger.log(f"Request not found: {request_id}", level="WARNING")
            return False

        request = self.requests[request_id]

        if request.status != ApprovalStatus.PENDING:
            self._logger.log(f"Request already processed: {request_id}", level="WARNING")
            return False

        elapsed = (datetime.now() - request.requested_at).total_seconds()
        if elapsed > request.timeout_seconds:
            request.status = ApprovalStatus.EXPIRED
            self._logger.log(f"Request expired: {request_id}", level="WARNING")
            return False

        request.status = ApprovalStatus.APPROVED
        request.approved_at = datetime.now()
        request.approved_by = approved_by
        request.response = response or {}

        self._logger.log(f"Request approved: {request_id} by {approved_by}", level="INFO")
        self._invoke_callback(request_id, request)
        return True

    def reject(self, request_id: str, rejected_by: str, reason: str) -> bool:
        """Reject a request.

        Args:
            request_id: Request ID.
            rejected_by: Rejector identifier.
            reason: Rejection reason.

        Returns:
            True if rejected successfully.
        """
        if request_id not in self.requests:
            self._logger.log(f"Request not found: {request_id}", level="WARNING")
            return False

        request = self.requests[request_id]

        if request.status != ApprovalStatus.PENDING:
            self._logger.log(f"Request already processed: {request_id}", level="WARNING")
            return False

        request.status = ApprovalStatus.REJECTED
        request.approved_by = rejected_by
        request.response = {"reason": reason}

        self._logger.log(
            f"Request rejected: {request_id} by {rejected_by} - {reason}", level="INFO"
        )
        self._invoke_callback(request_id, request)
        return True

    def get_request(self, request_id: str) -> Optional[HITLRequest]:
        """Get a request by ID."""
        return self.requests.get(request_id)

    def get_pending_requests(self) -> List[HITLRequest]:
        """Get all pending requests."""
        return [req for req in self.requests.values() if req.status == ApprovalStatus.PENDING]

    def check_timeouts(self) -> List[str]:
        """Check for expired requests.

        Returns:
            List of expired request IDs.
        """
        expired: List[str] = []
        now = datetime.now()

        for request_id, request in self.requests.items():
            if request.status == ApprovalStatus.PENDING:
                elapsed = (now - request.requested_at).total_seconds()
                if elapsed > request.timeout_seconds:
                    request.status = ApprovalStatus.EXPIRED
                    expired.append(request_id)
                    self._logger.log(f"Request expired: {request_id}", level="WARNING")

        return expired

    def _notify_human(self, request: HITLRequest) -> None:
        """Notify human operator (placeholder for actual notification system)."""
        self._logger.log(
            f"HITL notification: {request.request_id} - {request.action}", level="INFO"
        )

    def _invoke_callback(self, request_id: str, request: HITLRequest) -> None:
        """Invoke the callback registered for a request, if any."""
        if request_id in self.approval_callbacks:
            try:
                self.approval_callbacks[request_id](request)
            except Exception as e:
                self._logger.log(f"Error in callback for {request_id}: {e}", level="ERROR")

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log of all requests."""
        return [
            {
                "request_id": req.request_id,
                "action": req.action,
                "status": req.status.value,
                "requested_at": req.requested_at.isoformat(),
                "approved_at": req.approved_at.isoformat() if req.approved_at else None,
                "approved_by": req.approved_by,
            }
            for req in self.requests.values()
        ]
