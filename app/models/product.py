from decimal import Decimal

from sqlalchemy import Integer, String, ForeignKey, Float, Numeric, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from ..utils.mixins import TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable = False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cost_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    yield_quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    yield_unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)
    
    business: Mapped["Business"] = relationship("Business", back_populates="products")
    yield_unit: Mapped["Unit"] = relationship("Unit", back_populates="yield_product")
    ingredients: Mapped[list["ProductIngredients"]] = relationship("ProductIngredients",
                                                                   back_populates="product",
                                                                   cascade="all, delete-orphan")
    packagings_products: Mapped[list["ProductPackagings"]] = relationship("ProductPackagings",
                                                                          back_populates="products",
                                                                          cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name})>"
    
class ProductIngredients(Base, TimestampMixin):
    __tablename__ = "product_ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id"), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # Сколько нужно
    # unit_id: Mapped[int] = mapped_column(ForeignKey("units.id"), nullable=False)  # В чём измеряется количество

    
    product: Mapped["Product"] = relationship("Product", back_populates="ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="products")
    # unit: Mapped["Unit"] = relationship("Unit", back_populates="ingredients_unit")
   
   
class ProductPackagings(Base, TimestampMixin):
    __tablename__ = "product_packagings"

    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable = False)
    packaging_id: Mapped[int] = mapped_column(ForeignKey("packagings.id"), nullable = False)

    products: Mapped["Product"] = relationship("Product", back_populates="packagings_products")
    packaging: Mapped["Packaging"] = relationship("Packaging", back_populates="products")

    __table_args__ = (UniqueConstraint('product_id', 'packaging_id', name='uix_product_packaging'),) 