"""SQLAlchemy database models for DealScout."""

from .company import Company
from .investment_target import InvestmentTarget

__all__ = ["Company", "InvestmentTarget"]
