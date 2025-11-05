"""
Application DSN - Gestion de la norme DSN
"""
import dash
from dash import html, dcc, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd

# Initialisation avec thème Bootstrap
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    suppress_callback_exceptions=True
)

# Menu latéral
sidebar = dbc.Nav(
    [
        dbc.NavLink(
            [html.I(className="bi bi-house-door me-2"), "Accueil"],
            href="/",
            active="exact",
        ),
        dbc.NavLink(
            [html.I(className="bi bi-diagram-3 me-2"), "Structures"],
            href="/structures",
            active="exact",
        ),
        dbc.NavLink(
            [html.I(className="bi bi-list-ul me-2"), "Rubriques"],
            href="/rubriques",
            active="exact",
        ),
        dbc.NavLink(
            [html.I(className="bi bi-bar-chart me-2"), "Analyse"],
            href="/analyse",
            active="exact",
        ),
    ],
    vertical=True,
    pills=True,
    className="flex-column"
)

# Layout principal avec sidebar Bootstrap
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        # Sidebar
        dbc.Col([
            html.Div([
                html.H3("DSN", className="text-primary mb-4"),
                html.Hr(),
                sidebar
            ], className="p-3 bg-light", style={"min-height": "100vh"})
        ], width=2, className="p-0"),

        # Contenu principal
        dbc.Col([
            html.Div(id='page-content', className="p-4")
        ], width=10)
    ], className="g-0")
], fluid=True, className="p-0")

# Page Accueil
def page_accueil():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Bienvenue", className="mb-4"),
                html.P("Application de gestion de la norme DSN", className="lead")
            ])
        ])
    ])

# Page Structures
def page_structures():
    conn = sqlite3.connect('dsn.db')
    df = pd.read_sql_query("SELECT ordre, code, nom, description FROM structures ORDER BY ordre", conn)
    conn.close()

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Structures Hiérarchiques DSN", className="mb-3"),
                html.P("Les structures principales de la norme DSN", className="text-muted mb-4"),
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='table-structures',
                            columns=[
                                {"name": "Ordre", "id": "ordre"},
                                {"name": "Code", "id": "code"},
                                {"name": "Nom", "id": "nom"},
                                {"name": "Description", "id": "description"}
                            ],
                            data=df.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '12px',
                                'fontSize': '14px'
                            },
                            style_header={
                                'backgroundColor': '#2C3E50',
                                'color': 'white',
                                'fontWeight': 'bold',
                                'border': '1px solid #ddd'
                            },
                            style_data={
                                'border': '1px solid #ddd'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f8f9fa'
                                },
                                {
                                    'if': {'row_index': 'even'},
                                    'backgroundColor': 'white'
                                }
                            ],
                            page_size=25,
                            filter_action="native",
                            sort_action="native",
                            locale_format={
                                'symbol': ['', ''],
                                'decimal': ',',
                                'group': ' ',
                                'grouping': [3],
                                'percent': '%',
                                'nan': 'N/A',
                                'nully': '',
                            },
                            css=[{
                                'selector': '.dash-filter',
                                'rule': 'font-family: Arial, sans-serif;'
                            }]
                        )
                    ])
                ], className="shadow-sm")
            ])
        ])
    ], fluid=True)

# Page Rubriques
def page_rubriques():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Rubriques DSN", className="mb-4"),
                dbc.Alert([
                    html.I(className="bi bi-info-circle me-2"),
                    "Cette section sera développée pour gérer les rubriques DSN"
                ], color="info")
            ])
        ])
    ])

# Page Analyse
def page_analyse():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Analyse DSN", className="mb-4"),
                dbc.Alert([
                    html.I(className="bi bi-info-circle me-2"),
                    "Cette section sera développée pour analyser les fichiers DSN"
                ], color="info")
            ])
        ])
    ])

# Callback pour la navigation
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/structures':
        return page_structures()
    elif pathname == '/rubriques':
        return page_rubriques()
    elif pathname == '/analyse':
        return page_analyse()
    else:
        return page_accueil()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Application DSN démarrée")
    print("📍 URL: http://localhost:8050")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=8050)
