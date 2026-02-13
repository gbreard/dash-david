# Dashboard Analítico con Dash + PostgreSQL

Template para crear dashboards interactivos con Python, listos para deploy en Koyeb (gratis).

## Estructura del proyecto

```
├── app.py              ← Dashboard principal (layout + gráficos + callbacks)
├── database.py         ← Conexión a la DB (SQLite local / PostgreSQL en Koyeb)
├── models.py           ← Modelo de datos (tablas de la DB)
├── seed.py             ← Script para cargar datos en la DB
├── requirements.txt    ← Dependencias de Python
├── Procfile            ← Comando de inicio para Koyeb
├── runtime.txt         ← Versión de Python
└── .gitignore          ← Archivos ignorados por git
```

## Setup local (primera vez)

```bash
# 1. Clonar el repo
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar el entorno
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Cargar datos en la DB local (SQLite)
python seed.py

# 6. Levantar el dashboard
python app.py
# Abrir http://127.0.0.1:8050
```

## Cómo adaptarlo a tu propio proyecto

### Paso 1: Definí tu modelo de datos

Editá `models.py` con las columnas que necesites. Ejemplo para un dashboard de ventas:

```python
from sqlalchemy import Float, Integer, String, Date
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fecha: Mapped[str] = mapped_column(String(10), nullable=False)  # "2024-01-15"
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    ingreso_total: Mapped[float] = mapped_column(Float, nullable=False)
```

### Paso 2: Cargá tus datos

Editá `seed.py`. Podés cargar desde un CSV, Excel, o generar datos:

**Desde un CSV:**
```python
import pandas as pd
from database import SessionLocal, engine
from models import Base, Venta

def seed():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    if session.query(Venta).first():
        print("Ya hay datos.")
        session.close()
        return

    df = pd.read_csv("mis_datos.csv")
    records = [
        Venta(
            producto=row["producto"],
            categoria=row["categoria"],
            region=row["region"],
            fecha=row["fecha"],
            cantidad=row["cantidad"],
            precio_unitario=row["precio_unitario"],
            ingreso_total=row["ingreso_total"],
        )
        for _, row in df.iterrows()
    ]

    session.add_all(records)
    session.commit()
    print(f"Cargados {len(records)} registros.")
    session.close()

if __name__ == "__main__":
    seed()
```

**Desde un Excel:**
```python
df = pd.read_excel("mis_datos.xlsx", sheet_name="Hoja1")
```

### Paso 3: Armá tu dashboard

Editá `app.py`. Las piezas clave son:

**1. Función para leer de la DB:**
```python
def query_df():
    session = SessionLocal()
    rows = session.query(TuModelo).all()
    session.close()
    return pd.DataFrame([{...} for r in rows])
```

**2. Layout (lo que se ve):**
```python
app.layout = dbc.Container([
    dcc.Dropdown(...),      # Filtros
    dcc.Graph(id="..."),    # Gráficos
])
```

**3. Callbacks (interactividad):**
```python
@callback(
    Output("mi-grafico", "figure"),   # Qué se actualiza
    Input("mi-filtro", "value"),      # Qué lo dispara
)
def update(valor_filtro):
    df = query_df()
    # filtrar, transformar...
    return px.bar(df, x="...", y="...")
```

### Paso 4: Probá en local

```bash
# Borrar DB vieja y recrear
python seed.py --reset

# Levantar
python app.py
```

## Deploy en Koyeb (gratis)

### 1. Subí a GitHub

```bash
git add .
git commit -m "feat: mi dashboard personalizado"
git push
```

### 2. Creá la app en Koyeb

1. Ir a [koyeb.com](https://www.koyeb.com) → crear cuenta con GitHub
2. **Create Web Service** → seleccionar tu repo
3. Builder: **Buildpack** (detecta Python automáticamente)
4. Instancia: **Free**
5. Deploy

### 3. Creá la base de datos

1. En Koyeb: **Create Database Service** → Free tier (PostgreSQL)
2. Koyeb te da una `DATABASE_URL` automáticamente
3. Vinculá la DB al Web Service desde el panel

### 4. Seedeá la DB de producción

Desde la pestaña **Console** de tu Web Service en Koyeb:

```bash
python seed.py
```

¡Listo! Tu dashboard está online.

## Cómo funciona la conexión a la DB

El archivo `database.py` hace la magia:

- **Sin variable de entorno** → usa SQLite local (`data.db`) para desarrollo
- **Con `DATABASE_URL`** → usa PostgreSQL en producción (Koyeb la setea automáticamente)

No tenés que cambiar NADA en el código para pasar de local a producción.

## Tipos de gráficos disponibles

Todos los gráficos usan [Plotly Express](https://plotly.com/python/plotly-express/):

| Función | Tipo |
|---------|------|
| `px.scatter()` | Dispersión / burbujas |
| `px.bar()` | Barras verticales/horizontales |
| `px.line()` | Líneas temporales |
| `px.pie()` | Torta |
| `px.treemap()` | Mapa de árbol (jerarquías) |
| `px.histogram()` | Histograma |
| `px.box()` | Box plot |
| `px.imshow()` | Heatmap / correlación |
| `px.choropleth()` | Mapa geográfico |
| `px.sunburst()` | Gráfico solar (jerarquías) |

## Componentes interactivos

| Componente | Para qué |
|------------|----------|
| `dcc.Dropdown()` | Seleccionar una o varias opciones |
| `dcc.Slider()` | Elegir un valor numérico |
| `dcc.RangeSlider()` | Elegir un rango |
| `dcc.RadioItems()` | Elegir una opción (radio buttons) |
| `dcc.Checklist()` | Elegir varias opciones (checkboxes) |
| `dcc.DatePickerRange()` | Elegir rango de fechas |
| `dcc.Input()` | Campo de texto libre |

## Pedir ayuda a una IA

Si usás una IA para que te ayude a armar tu dashboard, dale este contexto:

> Tengo un proyecto en Python con Dash + SQLAlchemy. Los archivos principales son
> `models.py` (modelo de datos), `seed.py` (carga de datos), y `app.py` (dashboard).
> Necesito adaptar el modelo para [describí tus datos], crear el seed desde
> [CSV/Excel/API], y armar gráficos de [describí qué querés ver].

Cuanto más específico seas con tus datos y qué querés visualizar, mejor resultado vas a obtener.
