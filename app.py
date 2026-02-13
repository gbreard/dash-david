from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from database import SessionLocal, engine
from models import Base, Country

# --- DB Init ---
Base.metadata.create_all(bind=engine)

METRIC_LABELS = {
    "lifeExp": "Esperanza de vida (años)",
    "gdpPercap": "PBI per cápita (USD)",
    "pop": "Población",
    "unemployment": "Desempleo (%)",
    "education": "Índice de educación",
    "health": "Gasto en salud (% PBI)",
    "co2": "CO₂ per cápita (ton)",
    "internet": "Usuarios de internet (%)",
}


def query_df() -> pd.DataFrame:
    session = SessionLocal()
    rows = session.query(Country).all()
    session.close()
    return pd.DataFrame(
        [
            {
                "country": r.country,
                "continent": r.continent,
                "year": r.year,
                "lifeExp": r.life_exp,
                "pop": r.pop,
                "gdpPercap": r.gdp_per_cap,
                "unemployment": r.unemployment,
                "education": r.education_index,
                "health": r.health_exp_pct,
                "co2": r.co2_per_cap,
                "internet": r.internet_pct,
            }
            for r in rows
        ]
    )


def get_years() -> list[int]:
    session = SessionLocal()
    years = [r[0] for r in session.query(Country.year).distinct().order_by(Country.year)]
    session.close()
    return years


def get_continents() -> list[str]:
    session = SessionLocal()
    continents = [r[0] for r in session.query(Country.continent).distinct().order_by(Country.continent)]
    session.close()
    return continents


# --- App ---
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

available_years = get_years()
available_continents = get_continents()

# --- Layout ---
app.layout = dbc.Container(
    [
        # Header
        dbc.Row(
            dbc.Col(html.H1("Dashboard Analítico Mundial", className="text-center my-3")),
        ),
        html.Hr(),

        # Filtros
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Continentes:", className="fw-bold"),
                        dcc.Dropdown(
                            id="continent-filter",
                            options=[{"label": c, "value": c} for c in available_continents],
                            value=available_continents,
                            multi=True,
                            placeholder="Seleccionar continentes...",
                        ),
                    ],
                    md=6,
                ),
                dbc.Col(
                    [
                        html.Label("Métrica principal:", className="fw-bold"),
                        dcc.Dropdown(
                            id="main-metric",
                            options=[{"label": v, "value": k} for k, v in METRIC_LABELS.items()],
                            value="lifeExp",
                        ),
                    ],
                    md=3,
                ),
                dbc.Col(
                    [
                        html.Label("Métrica secundaria:", className="fw-bold"),
                        dcc.Dropdown(
                            id="secondary-metric",
                            options=[{"label": v, "value": k} for k, v in METRIC_LABELS.items()],
                            value="gdpPercap",
                        ),
                    ],
                    md=3,
                ),
            ],
            className="mb-3",
        ),

        # Slider de año
        dbc.Row(
            dbc.Col(
                [
                    html.Label("Año:", className="fw-bold"),
                    dcc.Slider(
                        id="year-slider",
                        min=min(available_years) if available_years else 2000,
                        max=max(available_years) if available_years else 2024,
                        step=None,
                        marks={str(y): str(y) for y in available_years if y % 5 == 0},
                        value=max(available_years) if available_years else 2024,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                ],
                width=12,
                className="mb-4",
            ),
        ),

        # KPIs
        dbc.Row(id="kpi-cards", className="mb-4"),

        # Fila 1: Scatter + Barras
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="scatter-chart"), lg=7),
                dbc.Col(dcc.Graph(id="bar-chart"), lg=5),
            ],
            className="mb-4",
        ),

        # Fila 2: Línea temporal + Treemap
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="line-chart"), lg=7),
                dbc.Col(dcc.Graph(id="treemap-chart"), lg=5),
            ],
            className="mb-4",
        ),

        # Fila 3: Correlación + Top 10
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="correlation-chart"), lg=6),
                dbc.Col(dcc.Graph(id="top10-chart"), lg=6),
            ],
            className="mb-4",
        ),
    ],
    fluid=True,
)


def _filter_df(df: pd.DataFrame, year: int, continents: list[str]) -> pd.DataFrame:
    mask = (df["year"] == year) & (df["continent"].isin(continents))
    return df[mask]


# --- KPI Cards ---
@callback(
    Output("kpi-cards", "children"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
)
def update_kpis(year, continents):
    if not continents:
        return []
    df = query_df()
    filtered = _filter_df(df, year, continents)

    kpis = [
        ("Países", f"{filtered['country'].nunique()}", "primary"),
        ("Esperanza de vida", f"{filtered['lifeExp'].mean():.1f} años", "success"),
        ("PBI per cápita", f"${filtered['gdpPercap'].mean():,.0f}", "info"),
        ("Desempleo", f"{filtered['unemployment'].mean():.1f}%", "warning"),
        ("Internet", f"{filtered['internet'].mean():.1f}%", "secondary"),
        ("CO₂ per cápita", f"{filtered['co2'].mean():.1f} ton", "danger"),
    ]

    return [
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    [
                        html.P(label, className="text-muted mb-1", style={"fontSize": "0.85rem"}),
                        html.H4(value, className="mb-0"),
                    ]
                ),
                color=color,
                outline=True,
            ),
            md=2,
            xs=6,
            className="mb-2",
        )
        for label, value, color in kpis
    ]


# --- Scatter + Bar ---
@callback(
    Output("scatter-chart", "figure"),
    Output("bar-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
    Input("main-metric", "value"),
    Input("secondary-metric", "value"),
)
def update_scatter_bar(year, continents, main_m, sec_m):
    df = query_df()
    filtered = _filter_df(df, year, continents) if continents else df[df["year"] == year]

    scatter = px.scatter(
        filtered,
        x=sec_m,
        y=main_m,
        size="pop",
        color="continent",
        hover_name="country",
        log_x=sec_m == "gdpPercap",
        size_max=50,
        labels={main_m: METRIC_LABELS.get(main_m, main_m), sec_m: METRIC_LABELS.get(sec_m, sec_m)},
        title=f"{METRIC_LABELS.get(main_m, '')} vs {METRIC_LABELS.get(sec_m, '')} ({year})",
    )

    bar_data = filtered.groupby("continent", as_index=False)[main_m].mean()
    bar = px.bar(
        bar_data,
        x="continent",
        y=main_m,
        color="continent",
        labels={"continent": "Continente", main_m: METRIC_LABELS.get(main_m, main_m)},
        title=f"Promedio por continente ({year})",
    )

    return scatter, bar


# --- Línea temporal ---
@callback(
    Output("line-chart", "figure"),
    Input("continent-filter", "value"),
    Input("main-metric", "value"),
)
def update_line(continents, main_m):
    df = query_df()
    if continents:
        df = df[df["continent"].isin(continents)]

    avg = df.groupby(["year", "continent"], as_index=False)[main_m].mean()

    return px.line(
        avg,
        x="year",
        y=main_m,
        color="continent",
        markers=True,
        labels={"year": "Año", main_m: METRIC_LABELS.get(main_m, main_m), "continent": "Continente"},
        title=f"Evolución - {METRIC_LABELS.get(main_m, main_m)}",
    )


# --- Treemap ---
@callback(
    Output("treemap-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
    Input("main-metric", "value"),
)
def update_treemap(year, continents, main_m):
    df = query_df()
    filtered = _filter_df(df, year, continents) if continents else df[df["year"] == year]

    return px.treemap(
        filtered,
        path=["continent", "country"],
        values="pop",
        color=main_m,
        color_continuous_scale="RdYlGn",
        title=f"Población y {METRIC_LABELS.get(main_m, main_m)} ({year})",
        labels={main_m: METRIC_LABELS.get(main_m, main_m)},
    )


# --- Correlación ---
@callback(
    Output("correlation-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
)
def update_correlation(year, continents):
    df = query_df()
    filtered = _filter_df(df, year, continents) if continents else df[df["year"] == year]

    numeric_cols = ["lifeExp", "gdpPercap", "unemployment", "education", "health", "co2", "internet"]
    labels_short = {
        "lifeExp": "Esp. vida", "gdpPercap": "PBI p/c", "unemployment": "Desempleo",
        "education": "Educación", "health": "Salud", "co2": "CO₂", "internet": "Internet",
    }

    corr = filtered[numeric_cols].corr()
    corr = corr.rename(index=labels_short, columns=labels_short)

    return px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Correlación entre métricas ({year})",
    )


# --- Top 10 ---
@callback(
    Output("top10-chart", "figure"),
    Input("year-slider", "value"),
    Input("continent-filter", "value"),
    Input("main-metric", "value"),
)
def update_top10(year, continents, main_m):
    df = query_df()
    filtered = _filter_df(df, year, continents) if continents else df[df["year"] == year]

    top = filtered.nlargest(10, main_m)

    return px.bar(
        top.sort_values(main_m),
        x=main_m,
        y="country",
        color="continent",
        orientation="h",
        labels={main_m: METRIC_LABELS.get(main_m, main_m), "country": ""},
        title=f"Top 10 - {METRIC_LABELS.get(main_m, main_m)} ({year})",
    )


if __name__ == "__main__":
    app.run(debug=True)
