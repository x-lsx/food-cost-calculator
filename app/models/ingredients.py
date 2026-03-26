from decimal import Decimal

from sqlalchemy import Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship


from ..core.database import Base
from ..utils.mixins import TimestampMixin

class Ingredient(Base, TimestampMixin):
    __tablename__ = "ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    slug: Mapped[str] = mapped_column(String(255), nullable = False, unique=True)
    base_unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable = False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable = False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable = False)
    
    business: Mapped["Business"] = relationship("Business", back_populates = "ingredients", lazy = "joined")
    base_unit: Mapped["Unit"] = relationship("Unit", back_populates = "ingredients")
    price_history: Mapped[list["IngredientPriceHistory"]] = relationship("IngredientPriceHistory", back_populates="ingredient", cascade="all, delete-orphan")
    products: Mapped[list["ProductIngredients"]] = relationship("ProductIngredients",
                                                               back_populates="ingredient",
                                                               cascade="all, delete-orphan")
    
    
    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name={self.name})>"
    
    
class IngredientPriceHistory(Base, TimestampMixin):
    __tablename__ = "ingredient_price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), nullable=False)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable = False)
    purchase_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    purchase_unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable = False)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=True, default="Продавец")
    
    business: Mapped["Business"] = relationship("Business", back_populates="ingredient_price_history")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="price_history")
    purchase_unit: Mapped["Unit"] = relationship("Unit", back_populates="ingredient_price_history")
    
    