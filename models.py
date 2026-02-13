from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    continent: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    life_exp: Mapped[float] = mapped_column(Float, nullable=False)
    pop: Mapped[int] = mapped_column(Integer, nullable=False)
    gdp_per_cap: Mapped[float] = mapped_column(Float, nullable=False)
    unemployment: Mapped[float] = mapped_column(Float, nullable=False)
    education_index: Mapped[float] = mapped_column(Float, nullable=False)
    health_exp_pct: Mapped[float] = mapped_column(Float, nullable=False)
    co2_per_cap: Mapped[float] = mapped_column(Float, nullable=False)
    internet_pct: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        return f"<Country {self.country} ({self.year})>"
