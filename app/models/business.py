from sqlalchemy import DateTime, Integer, String, ForeignKey, Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from ..core.database import Base


class Business(Base):
    __tablename__ = "businesses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    slug: Mapped[str] = mapped_column(String(255), nullable = False, unique = True)
    description: Mapped[str] = mapped_column(String(255), nullable = True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)
    is_active: Mapped[bool] = mapped_column(Boolean, default = True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone = True), server_default = func.now())
    
    owner: Mapped["User"] = relationship("User", back_populates = "businesses")
    ingredients: Mapped[list["Ingredient"]] = relationship("Ingredient", back_populates = "business", cascade = "all, delete-orphan")
    ingredient_price_history: Mapped[list["IngredientPriceHistory"]] = relationship("IngredientPriceHistory", back_populates="business", cascade="all, delete-orphan")
    packagings: Mapped[list["Packaging"]] = relationship("Packaging", back_populates="business", cascade="all, delete-orphan")
    products: Mapped[list["Product"]] = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Business(id={self.id}, name={self.name})>"
    