"""Office assistant tools."""

from .calendar import calendar_list, calendar_schedule
from .document_rag import document_rag_search
from .email_tool import email_draft, email_send
from .task_list import task_list_add, task_list_list
from .web_search import web_search

TOOL_REGISTRY = {
    "calendar_list": calendar_list,
    "calendar_schedule": calendar_schedule,
    "email_draft": email_draft,
    "email_send": email_send,
    "web_search": web_search,
    "document_rag_search": document_rag_search,
    "task_list_add": task_list_add,
    "task_list_list": task_list_list,
}

__all__ = [
    "TOOL_REGISTRY",
    "calendar_list",
    "calendar_schedule",
    "document_rag_search",
    "email_draft",
    "email_send",
    "task_list_add",
    "task_list_list",
    "web_search",
]
