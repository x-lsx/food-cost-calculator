from decimal import Decimal

from sqlalchemy import  Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..core.database import Base
from ..utils.mixins import TimestampMixin

class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    type: Mapped[str] = mapped_column(String(255), nullable = False)
    coefficient: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)

    ingredients: Mapped[list["Ingredient"]] = relationship("Ingredient", back_populates = "base_unit")
    ingredient_price_history: Mapped[list["IngredientPriceHistory"]] = relationship("IngredientPriceHistory", back_populates="purchase_unit")
    yield_product: Mapped[list["Product"]] = relationship("Product", back_populates="yield_unit")
    ingredients_unit: Mapped[list["ProductIngredients"]] = relationship("ProductIngredients", back_populates="unit")
    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, name={self.name})>"
