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

---

## PARTE 1: Setup local

### Requisitos previos

- Python 3.10 o superior instalado
- Git instalado
- Una cuenta de GitHub

### Instalación

```bash
# 1. Clonar el repo
git clone https://github.com/gbreard/dash-david.git
cd dash-david

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

---

## PARTE 2: Deploy en Koyeb (paso a paso completo)

### 2.1 Crear cuenta en Koyeb

1. Ir a **https://www.koyeb.com**
2. Click en **"Get Started"** (botón arriba a la derecha)
3. Elegir **"Continue with GitHub"** (recomendado, vincula directo tu repo)
4. Autorizar Koyeb a acceder a tu cuenta de GitHub
5. Completar el registro (no pide tarjeta de crédito)

### 2.2 Crear la Base de Datos PostgreSQL

**IMPORTANTE: Crear la base de datos ANTES que el Web Service.**

1. Una vez logueado, en el panel principal click en **"Create Service"**
2. Seleccionar **"Database"**
3. Configurar:
   - **Name**: `dash-db` (o el nombre que quieras)
   - **Region**: elegir la más cercana (ej: `Washington, D.C. (us-east)` para América)
   - **Plan**: **Free** (incluye 50 horas/mes, suficiente para desarrollo y demos)
4. Click en **"Create Database"**
5. Esperar a que el estado cambie a **"Healthy"** (tarda ~1 minuto)

#### Datos de conexión de la DB

Una vez creada, en la página de la base de datos vas a ver:

- **Host**: algo como `ep-xxxxx.us-east-2.aws.neon.tech`
- **Port**: `5432`
- **Database**: `koyebdb`
- **Username**: tu usuario
- **Password**: se muestra una vez (copiala y guardala)
- **Connection string**: `postgresql://usuario:password@host:5432/koyebdb?sslmode=require`

**No necesitás copiar nada de esto manualmente.** Koyeb puede inyectar la `DATABASE_URL` automáticamente al vincular la DB con tu servicio.

### 2.3 Crear el Web Service (tu dashboard)

1. En el panel principal, click en **"Create Service"**
2. Seleccionar **"Web Service"**
3. Elegir **"GitHub"** como source

#### Conectar el repositorio

4. Si es la primera vez, click en **"Install GitHub App"** para dar acceso a tus repos
5. Seleccionar el repo **`dash-david`** (o el nombre de tu fork)
6. Branch: **`main`**

#### Configuración del build

7. **Builder**: seleccionar **"Buildpack"** (detecta Python automáticamente por el `requirements.txt`)
8. Koyeb detecta el `Procfile` y usa el comando: `gunicorn --bind :$PORT app:server`
   - Si NO lo detecta, ponerlo manualmente en **"Run command"**

#### Configuración de la instancia

9. **Instance type**: seleccionar **"Free"**
   - Free incluye: 512 MB RAM, CPU compartida
   - Suficiente para dashboards con datos moderados

#### Variables de entorno

10. En la sección **"Environment variables"**, click en **"Add variable"**
11. **Opción A (recomendada)**: Vincular la DB automáticamente
    - Click en **"Reference a Database Service"**
    - Key: `DATABASE_URL`
    - Seleccionar la base de datos que creaste (`dash-db`)
    - Koyeb genera la URL de conexión automáticamente
12. **Opción B (manual)**: Si necesitás poner la URL a mano
    - Key: `DATABASE_URL`
    - Value: `postgresql://usuario:password@host:5432/koyebdb?sslmode=require`
    - (Usar los datos de conexión de la sección 2.2)

#### Nombre y región

13. **Service name**: `dash-analytics` (o el nombre que quieras, aparece en la URL)
14. **Region**: la misma que la base de datos (importante para latencia)
15. Click en **"Deploy"**

### 2.4 Primer deploy

Koyeb va a:
1. Clonar tu repo de GitHub
2. Detectar que es Python (por `requirements.txt`)
3. Instalar las dependencias
4. Ejecutar el comando del `Procfile`

**El build tarda entre 2 y 5 minutos la primera vez.**

Podés ver el progreso en:
- **"Build"** tab → logs del build (instalación de dependencias)
- **"Runtime"** tab → logs de la app corriendo

Cuando el estado cambie a **"Healthy"**, tu app está online.

### 2.5 Seedear la base de datos de producción

La base de datos de PostgreSQL en Koyeb arranca VACÍA. Necesitás cargar los datos.

#### Método 1: Desde la consola web de Koyeb

1. Ir a tu Web Service en el panel de Koyeb
2. Click en la pestaña **"Console"** (terminal web)
3. Ejecutar:
   ```bash
   python seed.py
   ```
4. Deberías ver: `Seed completado: 1625 registros (65 países × 25 años).`

#### Método 2: Seed automático al deployar

Si querés que se seedee automáticamente cada vez que deployás, podés modificar el `Procfile`:

```
web: python seed.py && gunicorn --bind :$PORT app:server
```

**OJO**: `seed.py` ya tiene protección contra duplicados (verifica si hay datos antes de insertar), así que no hay riesgo de datos repetidos.

### 2.6 Verificar que funciona

1. En el panel de tu Web Service, buscá la URL pública
   - Tiene la forma: `https://dash-analytics-TU_ORG.koyeb.app`
2. Click en la URL o copiala en el browser
3. Deberías ver el dashboard completo con todos los gráficos

---

## PARTE 3: Gestión y configuración de Koyeb

### 3.1 Panel de control

Después de loguearte en **https://app.koyeb.com**, ves:

- **Services**: lista de todos tus servicios (Web, DB, Workers)
- **Activity**: historial de deploys y eventos

Click en cualquier servicio para ver su detalle.

### 3.2 Tabs del Web Service

| Tab | Qué tiene |
|-----|-----------|
| **Overview** | Estado, URL pública, métricas de uso |
| **Deployments** | Historial de deploys (cada push a GitHub triggerea uno nuevo) |
| **Logs** | Logs en tiempo real de tu app (errores, requests, prints) |
| **Console** | Terminal web para ejecutar comandos dentro del container |
| **Settings** | Configuración del servicio (ver sección 3.3) |
| **Metrics** | Uso de CPU, RAM y red |

### 3.3 Settings importantes

Desde la pestaña **Settings** de tu Web Service:

#### Source
- **Repository**: qué repo de GitHub usa
- **Branch**: qué branch deploya (default: `main`)
- **Autodeploy**: activado por defecto. Cada push a `main` triggerea un deploy automático

#### Build
- **Builder**: Buildpack o Dockerfile
- **Build command**: generalmente vacío (Buildpack lo maneja)
- **Run command**: se toma del `Procfile`. Si no lo detecta, poné manualmente:
  ```
  gunicorn --bind :$PORT app:server
  ```

#### Instance
- **Type**: Free, Nano ($2.5/mes), Micro ($5/mes), etc.
- **Scaling**: en Free es fijo (1 instancia). En planes pagos podés configurar autoscaling

#### Environment variables
- Acá se configuran las variables de entorno
- `DATABASE_URL` es la más importante
- Podés agregar otras (ej: `DEBUG=false`, `SECRET_KEY=xxx`)

#### Health checks
- Koyeb verifica que tu app esté viva haciendo requests periódicos
- **Path**: `/` (default, funciona bien con Dash)
- **Port**: detectado automáticamente del `$PORT`

### 3.4 Tabs de la Database

| Tab | Qué tiene |
|-----|-----------|
| **Overview** | Estado, host, puerto, nombre de la DB |
| **Connection** | String de conexión completa, credenciales |
| **Settings** | Región, nombre, opción de borrar |

### 3.5 Redeploy manual

Si necesitás forzar un redeploy sin hacer push:

1. Ir a tu Web Service
2. Tab **"Deployments"**
3. Click en **"Redeploy"** en el deployment más reciente

### 3.6 Ver logs en tiempo real

1. Ir a tu Web Service
2. Tab **"Logs"**
3. Podés filtrar por:
   - **Build logs**: lo que pasa durante la instalación de dependencias
   - **Runtime logs**: lo que pasa mientras la app corre (errores, prints, requests)

Si tu app no levanta, los logs te dicen exactamente por qué.

### 3.7 Ejecutar comandos en el container

La pestaña **Console** te da una terminal dentro del container donde corre tu app:

```bash
# Ver si la DB tiene datos
python -c "from database import SessionLocal; from models import Country; s=SessionLocal(); print(s.query(Country).count()); s.close()"

# Re-seedear la DB
python seed.py --reset

# Ver variables de entorno (verificar DATABASE_URL)
echo $DATABASE_URL

# Verificar que las tablas existen
python -c "from database import engine; from sqlalchemy import inspect; print(inspect(engine).get_table_names())"
```

### 3.8 Dominio personalizado (opcional)

Si querés que tu dashboard tenga una URL propia (ej: `dashboard.tuempresa.com`):

1. Ir a **Settings** → **Domains**
2. Click en **"Add Domain"**
3. Escribir tu dominio (ej: `dashboard.tuempresa.com`)
4. Koyeb te da un registro CNAME que tenés que configurar en tu proveedor de dominio
5. Una vez propagado el DNS (~5 min), Koyeb genera un certificado SSL automáticamente

El Free tier permite hasta 5 dominios custom.

### 3.9 Límites del Free Tier

| Recurso | Límite |
|---------|--------|
| Web Services | 1 |
| Database | 1 (50 horas/mes) |
| RAM | 512 MB |
| CPU | Compartida |
| Dominios custom | 5 |
| Bandwidth | Sin límite explícito |
| Builds | Sin límite |
| Autodeploy | Incluido |
| SSL/HTTPS | Automático |

**50 horas/mes de base de datos** = ~1.6 horas por día. Si tu dashboard solo lo consultan en horario laboral, alcanza.
Si necesitás más, el plan Starter con pago por uso empieza en fracciones de centavo por segundo.

### 3.10 Pausar/Eliminar servicios

**Pausar** (no consume recursos):
- Ir al servicio → **Settings** → **"Pause Service"**
- El servicio se detiene pero mantiene la configuración
- Para reactivar: **"Resume Service"**

**Eliminar**:
- Ir al servicio → **Settings** → **"Delete Service"**
- CUIDADO: esto es irreversible. Los datos de la DB se pierden.
- El código sigue en GitHub, solo se elimina el deploy.

---

## PARTE 4: Cómo adaptarlo a tu propio proyecto

### Paso 1: Forkeá el repo

1. Ir a **https://github.com/gbreard/dash-david**
2. Click en **"Fork"** (arriba a la derecha)
3. Esto crea una copia en tu cuenta de GitHub
4. Cloná tu fork:
   ```bash
   git clone https://github.com/TU_USUARIO/dash-david.git
   cd dash-david
   ```

### Paso 2: Definí tu modelo de datos

Editá `models.py` con las columnas que necesites. Ejemplo para un dashboard de ventas:

```python
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Venta(Base):
    __tablename__ = "ventas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    producto: Mapped[str] = mapped_column(String(100), nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fecha: Mapped[str] = mapped_column(String(10), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    ingreso_total: Mapped[float] = mapped_column(Float, nullable=False)
```

### Paso 3: Cargá tus datos

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

### Paso 4: Armá tu dashboard

Editá `app.py`. Las piezas clave son:

**1. Función para leer de la DB:**
```python
def query_df():
    session = SessionLocal()
    rows = session.query(TuModelo).all()
    session.close()
    return pd.DataFrame([{...} for r in rows])
```

**2. Layout (lo que se ve en pantalla):**
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

### Paso 5: Probá en local

```bash
# Borrar DB vieja y recrear
python seed.py --reset

# Levantar
python app.py
# Abrir http://127.0.0.1:8050
```

### Paso 6: Pusheá y deployá

```bash
git add .
git commit -m "feat: mi dashboard personalizado"
git push
```

Si ya tenés el Web Service en Koyeb conectado a tu repo, el deploy es automático.
Si no, seguí los pasos de la PARTE 2.

---

## PARTE 5: Referencia rápida

### Archivos que tenés que modificar

| Quiero... | Editar... |
|-----------|-----------|
| Cambiar las tablas/columnas de la DB | `models.py` |
| Cambiar cómo se cargan los datos | `seed.py` |
| Cambiar gráficos, filtros, layout | `app.py` |
| Agregar una dependencia de Python | `requirements.txt` |
| Cambiar la versión de Python | `runtime.txt` |

### Archivos que NO tenés que tocar

| Archivo | Por qué |
|---------|---------|
| `database.py` | Ya maneja SQLite y PostgreSQL automáticamente |
| `Procfile` | Ya tiene el comando correcto para Koyeb |
| `.gitignore` | Ya ignora lo necesario |

### Cómo funciona la conexión a la DB

El archivo `database.py` hace la magia:

- **Sin variable de entorno** → usa SQLite local (`data.db`) para desarrollo
- **Con `DATABASE_URL`** → usa PostgreSQL en producción (Koyeb la setea automáticamente)

No tenés que cambiar NADA en el código para pasar de local a producción.

### Tipos de gráficos disponibles

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

### Componentes interactivos

| Componente | Para qué |
|------------|----------|
| `dcc.Dropdown()` | Seleccionar una o varias opciones |
| `dcc.Slider()` | Elegir un valor numérico |
| `dcc.RangeSlider()` | Elegir un rango |
| `dcc.RadioItems()` | Elegir una opción (radio buttons) |
| `dcc.Checklist()` | Elegir varias opciones (checkboxes) |
| `dcc.DatePickerRange()` | Elegir rango de fechas |
| `dcc.Input()` | Campo de texto libre |

---

## PARTE 6: Pedir ayuda a una IA

Si usás una IA (ChatGPT, Claude, etc.) para que te ayude a armar tu dashboard, dale este contexto:

> Tengo un proyecto en Python con Dash + SQLAlchemy + PostgreSQL. Los archivos principales son:
> - `models.py` (modelo de datos con SQLAlchemy)
> - `seed.py` (script para cargar datos en la DB)
> - `app.py` (dashboard con Dash + Plotly + Bootstrap)
> - `database.py` (conexión a la DB, no tocar)
>
> El proyecto se deploya en Koyeb con Gunicorn.
>
> Necesito adaptar el modelo para [DESCRIBÍ TUS DATOS], crear el seed desde
> [CSV/Excel/API/datos inventados], y armar gráficos de [DESCRIBÍ QUÉ QUERÉS VER].

### Ejemplo de prompt específico

> Tengo el template de Dash + SQLAlchemy. Necesito adaptarlo para un dashboard de ventas
> de una cadena de supermercados. Mis datos están en un Excel con columnas:
> sucursal, producto, categoría, fecha_venta, cantidad, precio, total.
> Quiero ver: ventas por sucursal (barras), evolución mensual (líneas),
> top 10 productos (barras horizontales), y un filtro por rango de fechas.
> Modificá models.py, seed.py y app.py manteniendo la misma arquitectura.

Cuanto más específico seas con tus datos y qué querés visualizar, mejor resultado vas a obtener.

---

## Troubleshooting

### La app no levanta en Koyeb
- Revisar **Logs** → **Runtime** en el panel de Koyeb
- Error `ModuleNotFoundError`: falta una dependencia en `requirements.txt`
- Error `no such table`: hay que correr `python seed.py` desde la Console

### Los gráficos aparecen vacíos
- La DB está vacía. Correr `python seed.py` desde la Console de Koyeb

### Error "database is locked" en local
- Estás corriendo dos procesos al mismo tiempo contra SQLite
- Cerrar uno de los dos (ej: si tenés dos terminales con `python app.py`)

### El deploy tarda mucho
- El primer build tarda más (descarga todas las dependencias)
- Los siguientes usan cache y son más rápidos (~1-2 min)

### La DB se queda sin horas (Free tier)
- El Free tier da 50 horas/mes de DB
- Si se agotan, la DB se pausa hasta el próximo mes
- Solución: pausar el servicio cuando no lo uses, o subir a plan pago
