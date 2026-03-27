from decimal import Decimal
from sqlalchemy import  Boolean, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..core.database import Base
from ..utils.mixins import TimestampMixin

class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable = False)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False)
    conversion_factor_to_base: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)

    ingredient_price_history: Mapped[list["IngredientPriceHistory"]] = relationship("IngredientPriceHistory", back_populates="purchase_unit")
    ingredients: Mapped[list["Ingredient"]] = relationship("Ingredient", back_populates = "base_unit")
    ingredients_unit: Mapped[list["ProductIngredients"]] = relationship("ProductIngredients", back_populates="unit")
    yield_product: Mapped[list["Product"]] = relationship("Product", back_populates="yield_unit")
    
    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, name={self.name})>"
    
    #qty_in_base = purchase_quantity * purchase_unit.conversion_factor_to_base   # 25 * 1000 = 25000
    #current_price = purchase_price / qty_in_base