"""Regional analytics chatbot — RAG over 14 Uzbekistan viloyat documents.

Public API:
  answer_question(question)          → async iterator of SSE-style events
  answer_question_blocking(question) → dict with full answer
  VILOYATS                           → 14-region registry
"""
from .orchestrator import answer_question, answer_question_blocking
from .registry import VILOYATS

__all__ = ["answer_question", "answer_question_blocking", "VILOYATS"]
