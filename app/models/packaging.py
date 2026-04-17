from decimal import Decimal

from sqlalchemy import Integer, String, ForeignKey, Float, Numeric, UniqueConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base
from ..utils.mixins import TimestampMixin

class Packaging(Base, TimestampMixin):
    __tablename__ = "packagings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key = True, autoincrement = True, index = True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable = False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    products: Mapped[list["ProductPackagings"]] = relationship("ProductPackagings",
                                                               back_populates="packaging",
                                                               cascade="all, delete-orphan")
    business: Mapped["Business"] = relationship("Business", back_populates="packagings")
    
