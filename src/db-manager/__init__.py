"""DB Manager for the Entity Resolution Engine (ERE)."""

from db_manager import (
    save_entitymention,
    get_entitymention,
    list_entitymentions,
    delete_entitymention,
)

__all__ = [
    "save_entitymention",
    "get_entitymention",
    "list_entitymentions",
    "delete_entitymention",
]
