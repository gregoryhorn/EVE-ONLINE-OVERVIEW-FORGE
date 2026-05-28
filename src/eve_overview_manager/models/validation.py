"""Structured validation result models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ValidationResult(BaseModel):
    code: str
    severity: Literal["info", "warning", "error"]
    message: str
    path: str
    suggestedFix: str | None = None
