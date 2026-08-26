"""Transport-independent authoritative inventory posting service."""

from .models import PostConfirmedReceiptRequest
from .repository import InventoryPostingRepository


class InventoryPostingService:
    def __init__(self, repository: InventoryPostingRepository) -> None:
        self._repository = repository

    async def post_confirmed_receipt(self, receipt_id, expected_version,
                                     actor_reference):
        request = PostConfirmedReceiptRequest(
            receipt_id, expected_version, actor_reference
        )
        return await self._repository.post_confirmed_receipt(
            request.receipt_id, request.expected_version, request.actor_reference
        )
