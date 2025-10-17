"""Container Offices Interactive BI Dashboard - V2."""
import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from dashboard.data_loader import DataLoader

# Initialize app
app = dash.Dash(
    __name__,
    title="Container Offices BI Dashboard V2",
    update_title="Loading...",
)

# Color scheme
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'building_a': '#2E86AB',
    'building_b': '#A23B72',
    'forecast': '#FF6B6B',
    'background': '#F8F9FA',
    'card': '#FFFFFF',
    'text': '#212529',
}

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Container Offices", style={'margin': 0, 'color': 'white'}),
            html.P("Business Intelligence Dashboard V2", style={'margin': 0, 'color': '#E8E8E8', 'fontSize': '14px'}),
        ], style={'flex': 1}),

        # Controls
        html.Div([
            # Window selector
            html.Div([
                html.Label("Time Window:", style={'color': 'white', 'marginRight': '8px', 'fontSize': '12px'}),
                dcc.Dropdown(
                    id='window-selector',
                    options=[
                        {'label': 'All Time', 'value': 'all'},
                        {'label': 'Year to Date', 'value': 'ytd'},
                        {'label': '12 Months', 'value': '12m'},
                        {'label': '9 Months', 'value': '9m'},
                        {'label': '6 Months', 'value': '6m'},
                        {'label': '3 Months', 'value': '3m'},
                    ],
                    value='all',
                    clearable=False,
                    style={'width': '150px', 'marginRight': '20px'}
                ),
            ], style={'display': 'inline-block'}),

            # Own-use toggle
            html.Div([
                html.Label("Exclude Own-Use:", style={'color': 'white', 'marginRight': '8px', 'fontSize': '12px'}),
                dcc.Checklist(
                    id='own-use-toggle',
                    options=[{'label': '', 'value': 'exclude'}],
                    value=[],
                    style={'display': 'inline-block', 'color': 'white'}
                ),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),

            # Show forecast toggle
            html.Div([
                html.Label("Show Forecast:", style={'color': 'white', 'marginRight': '8px', 'fontSize': '12px'}),
                dcc.Checklist(
                    id='forecast-toggle',
                    options=[{'label': '', 'value': 'show'}],
                    value=[],
                    style={'display': 'inline-block', 'color': 'white'}
                ),
            ], style={'display': 'inline-block'}),
        ], style={'display': 'flex', 'alignItems': 'center'}),
    ], style={
        'background': COLORS['primary'],
        'padding': '20px 40px',
        'marginBottom': '30px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center',
    }),

    html.Div([
        # KPI Cards Row (dynamic)
        html.Div(id='kpi-cards-container'),

        # Charts Row 1: Revenue & Occupancy Trends
        html.Div([
            # Revenue Trend
            html.Div([
                html.H3("Revenue Trends", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='revenue-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
                'marginRight': '20px',
            }),

            # Occupancy Trend
            html.Div([
                html.H3("Occupancy Trend", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='occupancy-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '30px',
        }),

        # Charts Row 2: NOI & Building Comparison
        html.Div([
            # NOI Trend
            html.Div([
                html.H3("NOI (Net Operating Income)", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='noi-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
                'marginRight': '20px',
            }),

            # Building A vs B
            html.Div([
                html.H3("Building A vs B Occupancy", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='building-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '30px',
        }),

        # Charts Row 3: Collection Rate & Expenses
        html.Div([
            # Collection Rate
            html.Div([
                html.H3("Collection Rate", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='collection-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
                'marginRight': '20px',
            }),

            # Expenses
            html.Div([
                html.H3("Expenses (Actual vs Budget)", style={'marginBottom': '15px', 'color': COLORS['text']}),
                dcc.Graph(id='expense-chart', config={'displayModeBar': False}),
            ], style={
                'background': COLORS['card'],
                'padding': '20px',
                'borderRadius': '8px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
                'flex': 1,
            }),
        ], style={
            'display': 'flex',
            'marginBottom': '30px',
        }),

        # Suite Details Table
        html.Div([
            html.H3("Suite Details", style={'marginBottom': '15px', 'color': COLORS['text']}),
            html.Div(id='suite-table-container'),
        ], style={
            'background': COLORS['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'marginBottom': '30px',
        }),

    ], style={
        'maxWidth': '1600px',
        'margin': '0 auto',
        'padding': '0 40px 40px 40px',
    }),

    # Footer
    html.Div([
        html.P("Container Offices Business Intelligence Dashboard V2 | Data updated from warehouse",
               style={'margin': 0, 'color': '#999', 'textAlign': 'center', 'fontSize': '12px'}),
    ], style={
        'padding': '20px',
        'borderTop': '1px solid #E0E0E0',
        'marginTop': '40px',
    }),

], style={'background': COLORS['background'], 'minHeight': '100vh'})


# Callbacks
@app.callback(
    Output('kpi-cards-container', 'children'),
    [Input('window-selector', 'value'),
     Input('own-use-toggle', 'value')]
)
def update_kpi_cards(window, own_use_toggle):
    """Update KPI cards based on filters."""
    loader = DataLoader()
    exclude_own_use = 'exclude' in (own_use_toggle or [])
    stats = loader.get_summary_stats(exclude_own_use=exclude_own_use)
    loader.close()

    cards = html.Div([
        # Occupancy Card
        html.Div([
            html.H4("Occupancy Rate", style={'color': '#666', 'fontSize': '14px', 'margin': 0}),
            html.H2(f"{stats['occupancy']:.1f}%", style={'color': COLORS['primary'], 'margin': '10px 0'}),
            html.P(f"{int(stats['leased_sqft']):,} / {stats['total_sqft']:,} sqft" +
                   (" (excl own-use)" if exclude_own_use else ""),
                   style={'color': '#999', 'fontSize': '12px', 'margin': 0}),
        ], style={
            'background': COLORS['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'flex': 1,
            'marginRight': '20px',
        }),

        # Revenue Card
        html.Div([
            html.H4("Monthly Revenue", style={'color': '#666', 'fontSize': '14px', 'margin': 0}),
            html.H2(f"${stats['monthly_revenue']:,.0f}", style={'color': COLORS['success'], 'margin': '10px 0'}),
            html.P(f"Collection: {stats['collection_rate']:.0f}%",
                   style={'color': '#999', 'fontSize': '12px', 'margin': 0}),
        ], style={
            'background': COLORS['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'flex': 1,
            'marginRight': '20px',
        }),

        # NOI Card
        html.Div([
            html.H4("NOI (Proto)", style={'color': '#666', 'fontSize': '14px', 'margin': 0}),
            html.H2(f"${stats['noi_proto']:,.0f}", style={'color': COLORS['warning'], 'margin': '10px 0'}),
            html.P(f"Margin: {stats['noi_margin_pct']:.1f}%",
                   style={'color': '#999', 'fontSize': '12px', 'margin': 0}),
        ], style={
            'background': COLORS['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'flex': 1,
            'marginRight': '20px',
        }),

        # Suites Card
        html.Div([
            html.H4("Suite Status", style={'color': '#666', 'fontSize': '14px', 'margin': 0}),
            html.H2(f"{stats['total_suites']}", style={'color': COLORS['secondary'], 'margin': '10px 0'}),
            html.P(f"Vacant: {stats['vacant_suites']} | Own-Use: {stats['own_use_suites']}",
                   style={'color': '#999', 'fontSize': '12px', 'margin': 0}),
        ], style={
            'background': COLORS['card'],
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 8px rgba(0,0,0,0.08)',
            'flex': 1,
        }),
    ], style={
        'display': 'flex',
        'marginBottom': '30px',
    })

    return cards


@app.callback(
    Output('revenue-chart', 'figure'),
    [Input('window-selector', 'value'),
     Input('forecast-toggle', 'value')]
)
def update_revenue_chart(window, forecast_toggle):
    """Update revenue trend chart."""
    loader = DataLoader()
    window_filter = None if window == 'all' else window
    df = loader.get_property_kpis(window=window_filter)

    show_forecast = 'show' in (forecast_toggle or [])
    forecasts = loader.get_forecasts() if show_forecast else None
    loader.close()

    fig = go.Figure()

    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['rent_base'],
            name='Rent Base',
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=8),
        ))

        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['collected'],
            name='Collected',
            mode='lines+markers',
            line=dict(color=COLORS['success'], width=2),
            marker=dict(size=8),
            fill='tonexty',
            fillcolor='rgba(6, 167, 125, 0.1)',
        ))

    # Add forecast
    if forecasts is not None and 'collected_p50' in forecasts.columns:
        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['collected_p50'],
            name='Forecast (P50)',
            mode='lines',
            line=dict(color=COLORS['forecast'], width=2, dash='dash'),
        ))

        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['collected_p90'],
            name='Forecast (P90)',
            mode='lines',
            line=dict(width=0),
            showlegend=False,
        ))

        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['collected_p10'],
            name='Forecast Range',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 107, 107, 0.2)',
            fill='tonexty',
        ))

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue ($)',
        hovermode='x unified',
        plot_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
    )

    return fig


@app.callback(
    Output('occupancy-chart', 'figure'),
    [Input('window-selector', 'value'),
     Input('own-use-toggle', 'value'),
     Input('forecast-toggle', 'value')]
)
def update_occupancy_chart(window, own_use_toggle, forecast_toggle):
    """Update occupancy trend chart."""
    loader = DataLoader()
    window_filter = None if window == 'all' else window
    exclude_own_use = 'exclude' in (own_use_toggle or [])
    df = loader.get_property_kpis(window=window_filter, exclude_own_use=exclude_own_use)

    show_forecast = 'show' in (forecast_toggle or [])
    forecasts = loader.get_forecasts() if show_forecast else None
    loader.close()

    occupancy_col = 'occupancy_pct_excl_own_use' if exclude_own_use else 'occupancy_pct'

    fig = go.Figure()

    if len(df) > 0 and occupancy_col in df.columns:
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df[occupancy_col],
            name='Occupancy %',
            mode='lines+markers',
            line=dict(color=COLORS['primary'], width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.1)',
        ))

    # Add forecast
    if forecasts is not None and 'occupancy_pct_p50' in forecasts.columns:
        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['occupancy_pct_p50'],
            name='Forecast (P50)',
            mode='lines',
            line=dict(color=COLORS['forecast'], width=2, dash='dash'),
        ))

    fig.add_hline(
        y=85,
        line_dash="dash",
        line_color="gray",
        annotation_text="Target: 85%",
        annotation_position="right",
    )

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Occupancy (%)',
        yaxis_range=[0, 100],
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
    )

    return fig


@app.callback(
    Output('noi-chart', 'figure'),
    [Input('window-selector', 'value'),
     Input('forecast-toggle', 'value')]
)
def update_noi_chart(window, forecast_toggle):
    """Update NOI trend chart."""
    loader = DataLoader()
    window_filter = None if window == 'all' else window
    df = loader.get_property_kpis(window=window_filter)

    show_forecast = 'show' in (forecast_toggle or [])
    forecasts = loader.get_forecasts() if show_forecast else None
    loader.close()

    fig = go.Figure()

    if len(df) > 0:
        fig.add_trace(go.Scatter(
            x=df['month'],
            y=df['noi_proto'],
            name='NOI',
            mode='lines+markers',
            line=dict(color=COLORS['warning'], width=2),
            marker=dict(size=8),
        ))

    # Add forecast
    if forecasts is not None and 'noi_proto_p50' in forecasts.columns:
        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['noi_proto_p50'],
            name='Forecast (P50)',
            mode='lines',
            line=dict(color=COLORS['forecast'], width=2, dash='dash'),
        ))

        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['noi_proto_p90'],
            name='Upper',
            mode='lines',
            line=dict(width=0),
            showlegend=False,
        ))

        fig.add_trace(go.Scatter(
            x=forecasts['forecast_month'],
            y=forecasts['noi_proto_p10'],
            name='Forecast Range',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 107, 107, 0.2)',
            fill='tonexty',
        ))

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='NOI ($)',
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
    )

    return fig


@app.callback(
    Output('building-chart', 'figure'),
    [Input('window-selector', 'value'),
     Input('own-use-toggle', 'value')]
)
def update_building_chart(window, own_use_toggle):
    """Update building comparison chart."""
    loader = DataLoader()
    window_filter = None if window == 'all' else window
    exclude_own_use = 'exclude' in (own_use_toggle or [])
    df = loader.get_building_kpis(window=window_filter, exclude_own_use=exclude_own_use)
    loader.close()

    occupancy_col = 'occupancy_pct_excl_own_use' if exclude_own_use else 'occupancy_pct'

    if len(df) > 0:
        latest_month = df['month'].max()
        df_latest = df[df['month'] == latest_month]

        fig = go.Figure(data=[
            go.Bar(
                name='Building A',
                x=['Occupancy %'],
                y=[df_latest[df_latest['building'] == 'A'][occupancy_col].iloc[0] if len(df_latest[df_latest['building'] == 'A']) > 0 else 0],
                marker_color=COLORS['building_a'],
            ),
            go.Bar(
                name='Building B',
                x=['Occupancy %'],
                y=[df_latest[df_latest['building'] == 'B'][occupancy_col].iloc[0] if len(df_latest[df_latest['building'] == 'B']) > 0 else 0],
                marker_color=COLORS['building_b'],
            ),
        ])

        fig.update_layout(
            barmode='group',
            yaxis_title='Occupancy (%)',
            yaxis_range=[0, 100],
            plot_bgcolor='white',
            margin=dict(l=40, r=20, t=20, b=40),
            height=300,
        )
    else:
        fig = go.Figure()

    return fig


@app.callback(
    Output('collection-chart', 'figure'),
    [Input('window-selector', 'value')]
)
def update_collection_chart(window):
    """Update collection rate chart."""
    loader = DataLoader()
    window_filter = None if window == 'all' else window
    df = loader.get_property_kpis(window=window_filter)
    loader.close()

    fig = go.Figure()

    if len(df) > 0:
        fig.add_trace(go.Bar(
            x=df['month'],
            y=df['collection_rate_pct'],
            name='Collection Rate',
            marker_color=COLORS['success'],
        ))

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="green",
        annotation_text="Target: 100%",
        annotation_position="right",
    )

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Collection Rate (%)',
        yaxis_range=[0, 110],
        hovermode='x unified',
        plot_bgcolor='white',
        margin=dict(l=40, r=20, t=20, b=40),
        height=300,
    )

    return fig


@app.callback(
    Output('expense-chart', 'figure'),
    Input('window-selector', 'value')
)
def update_expense_chart(window):
    """Update expense chart."""
    loader = DataLoader()
    df = loader.get_expense_facts()
    loader.close()

    if len(df) > 0:
        # Group by category
        fig = go.Figure()

        categories = df['expense_category'].unique()
        for category in categories:
            df_cat = df[df['expense_category'] == category]
            fig.add_trace(go.Bar(
                name=category.title(),
                x=df_cat['as_of_month'],
                y=df_cat['total_actual'],
            ))

        fig.update_layout(
            barmode='stack',
            xaxis_title='Month',
            yaxis_title='Expenses ($)',
            hovermode='x unified',
            plot_bgcolor='white',
            margin=dict(l=40, r=20, t=20, b=40),
            height=300,
        )
    else:
        fig = go.Figure()
        fig.add_annotation(
            text="No expense data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

    return fig


@app.callback(
    Output('suite-table-container', 'children'),
    Input('window-selector', 'value')
)
def update_suite_table(window):
    """Update suite details table."""
    loader = DataLoader()
    suite_details = loader.get_suite_details()
    loader.close()

    suite_details_display = suite_details.assign(
        status=suite_details.apply(
            lambda row: 'Own-Use' if row['is_own_use'] else ('Vacant' if row['is_vacant'] else 'Leased'),
            axis=1
        )
    )

    table = dash_table.DataTable(
        id='suite-table',
        columns=[
            {'name': 'Suite', 'id': 'suite_id'},
            {'name': 'Building', 'id': 'building'},
            {'name': 'Tenant', 'id': 'tenant'},
            {'name': 'SqFt', 'id': 'sqft', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
            {'name': 'Monthly Rent', 'id': 'rent_monthly', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': 'Annual Rent', 'id': 'rent_annual', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': '$/SF/Yr', 'id': 'rent_psf_yr', 'type': 'numeric', 'format': {'specifier': '$,.2f'}},
            {'name': 'Status', 'id': 'status'},
        ],
        data=suite_details_display.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontSize': '14px',
        },
        style_header={
            'backgroundColor': COLORS['primary'],
            'color': 'white',
            'fontWeight': 'bold',
        },
        style_data_conditional=[
            {
                'if': {'filter_query': '{status} = "Vacant"'},
                'backgroundColor': '#FFF3CD',
            },
            {
                'if': {'filter_query': '{status} = "Own-Use"'},
                'backgroundColor': '#D1ECF1',
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#F8F9FA',
            },
        ],
        page_size=10,
        sort_action='native',
        filter_action='native',
    )

    return table


if __name__ == '__main__':
    print("=" * 60)
    print("Container Offices BI Dashboard V2")
    print("=" * 60)
    print("\nFeatures:")
    print("  - Time window selection (3m/6m/9m/12m/YTD/All)")
    print("  - Own-use toggle")
    print("  - Forecast visualization (P10/P50/P90)")
    print("  - NOI tracking")
    print("  - Expense analysis")
    print("\nStarting dashboard server...")
    print("Open your browser to: http://127.0.0.1:8050")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=8050)
