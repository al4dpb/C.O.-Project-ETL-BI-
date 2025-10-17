"""Simple Container Offices BI Dashboard - No infinite loops."""
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dashboard.data_loader import DataLoader

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Container Offices BI"

# Load data once at startup
loader = DataLoader()
prop_kpis = loader.get_property_kpis()
building_kpis = loader.get_building_kpis()
suite_details = loader.get_suite_details()
stats = loader.get_summary_stats()

# Layout
app.layout = html.Div([
    html.Div([
        html.H1("Container Offices BI Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Hr(),
    ], style={'padding': '20px'}),

    # KPI Cards
    html.Div([
        html.Div([
            html.H3(f"{stats['occupancy']:.1f}%", style={'margin': '0', 'color': '#27ae60'}),
            html.P("Occupancy", style={'margin': '5px 0', 'color': '#7f8c8d'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '10px', 'borderRadius': '8px', 'textAlign': 'center'}),

        html.Div([
            html.H3(f"${stats['monthly_revenue']:,.0f}", style={'margin': '0', 'color': '#3498db'}),
            html.P("Monthly Revenue", style={'margin': '5px 0', 'color': '#7f8c8d'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '10px', 'borderRadius': '8px', 'textAlign': 'center'}),

        html.Div([
            html.H3(f"${stats['price_per_sf']:.2f}", style={'margin': '0', 'color': '#e74c3c'}),
            html.P("$/SF/Year", style={'margin': '5px 0', 'color': '#7f8c8d'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '10px', 'borderRadius': '8px', 'textAlign': 'center'}),

        html.Div([
            html.H3(f"{stats['collection_rate']:.1f}%", style={'margin': '0', 'color': '#f39c12'}),
            html.P("Collection Rate", style={'margin': '5px 0', 'color': '#7f8c8d'})
        ], style={'flex': '1', 'padding': '20px', 'backgroundColor': '#ecf0f1', 'margin': '10px', 'borderRadius': '8px', 'textAlign': 'center'}),
    ], style={'display': 'flex', 'padding': '20px'}),

    # Charts Row 1
    html.Div([
        html.Div([
            dcc.Graph(id='revenue-chart', config={'displayModeBar': False})
        ], style={'flex': '1', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='occupancy-chart', config={'displayModeBar': False})
        ], style={'flex': '1', 'padding': '10px'}),
    ], style={'display': 'flex', 'padding': '20px'}),

    # Charts Row 2
    html.Div([
        html.Div([
            dcc.Graph(id='building-chart', config={'displayModeBar': False})
        ], style={'flex': '1', 'padding': '10px'}),

        html.Div([
            dcc.Graph(id='collection-chart', config={'displayModeBar': False})
        ], style={'flex': '1', 'padding': '10px'}),
    ], style={'display': 'flex', 'padding': '20px'}),

    # Suite Details Table
    html.Div([
        html.H3("Suite Details", style={'color': '#2c3e50'}),
        dash_table.DataTable(
            id='suite-table',
            columns=[
                {'name': 'Suite', 'id': 'suite_id'},
                {'name': 'Building', 'id': 'building'},
                {'name': 'Tenant', 'id': 'tenant'},
                {'name': 'Sq Ft', 'id': 'sqft'},
                {'name': 'Monthly Rent', 'id': 'rent_monthly', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
                {'name': 'Vacant', 'id': 'is_vacant', 'type': 'text'},
                {'name': 'Own Use', 'id': 'is_own_use', 'type': 'text'},
            ],
            data=suite_details.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#34495e', 'color': 'white', 'fontWeight': 'bold'},
            style_data_conditional=[
                {'if': {'filter_query': '{is_vacant} = True'}, 'backgroundColor': '#ffebee'},
                {'if': {'filter_query': '{is_own_use} = True'}, 'backgroundColor': '#e8f5e9'},
            ],
            page_size=10,
            sort_action='native',
            filter_action='native',
        )
    ], style={'padding': '20px'}),
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#ffffff'})


# Static charts (no callbacks, no infinite loops)
@app.callback(
    Output('revenue-chart', 'figure'),
    Input('revenue-chart', 'id')  # Dummy input, fires once
)
def create_revenue_chart(_):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prop_kpis['month'],
        y=prop_kpis['rent_base'],
        mode='lines+markers',
        name='Base Rent',
        line={'color': '#3498db', 'width': 2}
    ))
    fig.add_trace(go.Scatter(
        x=prop_kpis['month'],
        y=prop_kpis['collected'],
        mode='lines+markers',
        name='Collected',
        line={'color': '#27ae60', 'width': 2}
    ))
    fig.update_layout(
        title='Revenue Trends (2025)',
        xaxis_title='Month',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='white',
        margin={'l': 50, 'r': 20, 't': 40, 'b': 40}
    )
    return fig


@app.callback(
    Output('occupancy-chart', 'figure'),
    Input('occupancy-chart', 'id')
)
def create_occupancy_chart(_):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prop_kpis['month'],
        y=prop_kpis['occupancy_pct'],
        mode='lines+markers',
        name='Occupancy',
        line={'color': '#e74c3c', 'width': 2},
        fill='tozeroy',
        fillcolor='rgba(231, 76, 60, 0.1)'
    ))
    fig.update_layout(
        title='Occupancy Trend (2025)',
        xaxis_title='Month',
        yaxis_title='Occupancy %',
        hovermode='x unified',
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='white',
        margin={'l': 50, 'r': 20, 't': 40, 'b': 40}
    )
    return fig


@app.callback(
    Output('building-chart', 'figure'),
    Input('building-chart', 'id')
)
def create_building_chart(_):
    # Get latest month data for each building
    latest = building_kpis.sort_values('month').groupby('building').last().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=latest['building'],
        y=latest['occupancy_pct'],
        text=[f"{v:.1f}%" for v in latest['occupancy_pct']],
        textposition='auto',
        marker={'color': ['#3498db', '#e74c3c']}
    ))
    fig.update_layout(
        title='Building A vs B Occupancy (Latest)',
        xaxis_title='Building',
        yaxis_title='Occupancy %',
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='white',
        margin={'l': 50, 'r': 20, 't': 40, 'b': 40}
    )
    return fig


@app.callback(
    Output('collection-chart', 'figure'),
    Input('collection-chart', 'id')
)
def create_collection_chart(_):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=prop_kpis['month'],
        y=prop_kpis['collection_rate_pct'],
        mode='lines+markers',
        name='Collection Rate',
        line={'color': '#f39c12', 'width': 2}
    ))
    fig.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="100% Target")
    fig.update_layout(
        title='Collection Rate Trend (2025)',
        xaxis_title='Month',
        yaxis_title='Collection Rate %',
        hovermode='x unified',
        plot_bgcolor='#ecf0f1',
        paper_bgcolor='white',
        margin={'l': 50, 'r': 20, 't': 40, 'b': 40}
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=False, host='127.0.0.1', port=8050)
