"""
Seed script: genera datos sintéticos realistas y los carga en la DB.

    python seed.py          → seed normal
    python seed.py --reset  → borra todo y re-seedea
"""

import random
import sys

from database import SessionLocal, engine
from models import Base, Country

random.seed(42)

# --- Datos base por región (rangos realistas) ---
REGIONS = {
    "Europa": {
        "countries": [
            "Alemania", "Francia", "España", "Italia", "Reino Unido",
            "Países Bajos", "Suecia", "Polonia", "Noruega", "Suiza",
            "Portugal", "Bélgica", "Austria", "Grecia", "Dinamarca",
        ],
        "life_exp": (76, 84), "gdp": (20000, 65000), "pop": (4_000_000, 83_000_000),
        "unemployment": (3, 15), "education": (0.75, 0.95), "health": (6, 12),
        "co2": (4, 12), "internet": (60, 98),
    },
    "América": {
        "countries": [
            "Estados Unidos", "Brasil", "México", "Argentina", "Colombia",
            "Canadá", "Chile", "Perú", "Venezuela", "Uruguay",
            "Ecuador", "Cuba", "Paraguay", "Bolivia", "Costa Rica",
        ],
        "life_exp": (65, 82), "gdp": (3000, 62000), "pop": (3_000_000, 330_000_000),
        "unemployment": (3, 18), "education": (0.55, 0.92), "health": (3, 17),
        "co2": (1, 16), "internet": (30, 95),
    },
    "Asia": {
        "countries": [
            "China", "Japón", "India", "Corea del Sur", "Indonesia",
            "Tailandia", "Vietnam", "Filipinas", "Malasia", "Turquía",
            "Arabia Saudita", "Israel", "Singapur", "Taiwán", "Pakistán",
        ],
        "life_exp": (62, 85), "gdp": (1500, 60000), "pop": (5_000_000, 1_400_000_000),
        "unemployment": (2, 12), "education": (0.40, 0.93), "health": (2, 11),
        "co2": (1, 18), "internet": (15, 96),
    },
    "África": {
        "countries": [
            "Nigeria", "Egipto", "Sudáfrica", "Kenia", "Etiopía",
            "Ghana", "Tanzania", "Marruecos", "Senegal", "Uganda",
            "Túnez", "Costa de Marfil", "Mozambique", "Camerún", "Angola",
        ],
        "life_exp": (50, 75), "gdp": (500, 12000), "pop": (2_000_000, 220_000_000),
        "unemployment": (5, 30), "education": (0.25, 0.72), "health": (2, 8),
        "co2": (0.2, 8), "internet": (5, 70),
    },
    "Oceanía": {
        "countries": [
            "Australia", "Nueva Zelanda", "Papúa Nueva Guinea", "Fiyi", "Samoa",
        ],
        "life_exp": (60, 84), "gdp": (2000, 55000), "pop": (200_000, 26_000_000),
        "unemployment": (3, 12), "education": (0.45, 0.94), "health": (3, 10),
        "co2": (1, 17), "internet": (20, 95),
    },
}

YEARS = list(range(2000, 2025))


def _trend(base: float, year: int, growth: float, noise: float) -> float:
    """Aplica tendencia temporal + ruido."""
    years_from_start = year - 2000
    return base + (growth * years_from_start) + random.uniform(-noise, noise)


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def generate_records() -> list[Country]:
    records = []

    for continent, cfg in REGIONS.items():
        for country in cfg["countries"]:
            # Valores base para este país (consistentes entre años)
            base_life = random.uniform(*cfg["life_exp"])
            base_gdp = random.uniform(*cfg["gdp"])
            base_pop = random.uniform(*cfg["pop"])
            base_unemp = random.uniform(*cfg["unemployment"])
            base_edu = random.uniform(*cfg["education"])
            base_health = random.uniform(*cfg["health"])
            base_co2 = random.uniform(*cfg["co2"])
            base_internet = random.uniform(*cfg["internet"])

            # Tasas de crecimiento anuales por país
            pop_growth = random.uniform(0.005, 0.025)
            gdp_growth = random.uniform(0.01, 0.04)

            for year in YEARS:
                y = year - 2000

                life_exp = _clamp(_trend(base_life, year, 0.15, 0.3), 45, 90)
                gdp = _clamp(base_gdp * ((1 + gdp_growth) ** y) + random.uniform(-500, 500), 300, 120000)
                pop = int(base_pop * ((1 + pop_growth) ** y))
                unemployment = _clamp(_trend(base_unemp, year, -0.1, 0.8), 0.5, 35)
                education = _clamp(_trend(base_edu, year, 0.005, 0.01), 0.15, 0.99)
                health = _clamp(_trend(base_health, year, 0.08, 0.3), 1, 20)
                co2 = _clamp(_trend(base_co2, year, 0.05, 0.3), 0.1, 25)
                internet = _clamp(_trend(base_internet, year, 2.5, 2.0), 0.5, 99.9)

                records.append(
                    Country(
                        country=country,
                        continent=continent,
                        year=year,
                        life_exp=round(life_exp, 1),
                        pop=pop,
                        gdp_per_cap=round(gdp, 1),
                        unemployment=round(unemployment, 1),
                        education_index=round(education, 3),
                        health_exp_pct=round(health, 1),
                        co2_per_cap=round(co2, 2),
                        internet_pct=round(internet, 1),
                    )
                )

    return records


def seed(reset: bool = False):
    if reset:
        Base.metadata.drop_all(bind=engine)
        print("Tablas eliminadas.")

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    if not reset and session.query(Country).first():
        print("La base ya tiene datos. Usá --reset para recrear.")
        session.close()
        return

    records = generate_records()
    session.add_all(records)
    session.commit()

    n_countries = len({r.country for r in records})
    n_years = len(YEARS)
    print(f"Seed completado: {len(records)} registros ({n_countries} países × {n_years} años).")
    session.close()


if __name__ == "__main__":
    reset = "--reset" in sys.argv
    seed(reset=reset)
