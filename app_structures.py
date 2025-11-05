"""
Application Dash pour afficher les structures DSN
"""
import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd

# Connexion à la base de données
conn = sqlite3.connect('dsn.db')
df = pd.read_sql_query("SELECT code, nom, description, ordre FROM structures ORDER BY ordre", conn)
conn.close()

# Initialisation de l'application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Structures Hiérarchiques DSN", className="text-center mt-4 mb-4"),
        ])
    ]),

    dbc.Row([
        dbc.Col([
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
                    'padding': '10px',
                    'fontSize': '14px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ])
    ])
], fluid=True)

if __name__ == '__main__':
    print("🚀 Application démarrée sur http://localhost:8050")
    app.run(debug=True, host='0.0.0.0', port=8050)
