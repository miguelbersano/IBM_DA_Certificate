import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# === Load your dataset ===
df = pd.read_csv(r"C:\Users\lenovo-miguel\OneDrive\IBM_Data_Analytics_Coursera\2016.csv")

#convert the relevant columns to numeric types (coercing non-numeric values to NaN).

# List of columns that should be numeric (adjust based on actual data)
numeric_cols = [
    "Happiness Rank",
    "Happiness Score",
    "Lower Confidence Interval",
    "Upper Confidence Interval",
    "Economy (GDP per Capita)",
    "Family",
    "Health (Life Expectancy)",
    "Freedom",
    "Trust (Government Corruption)",
    "Generosity",
    "Dystopia Residual"
]

# Convert to numeric where possible
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

#replace the missing values in each column by the column mean value
cols = [
    'Lower Confidence Interval',
    'Health (Life Expectancy)',
    'Upper Confidence Interval',
    'Economy (GDP per Capita)',
    'Freedom'
]

for col in cols:
    df[col] = df[col].fillna(df[col].mean())

# Columns for correlation
corr_cols = [
    'Economy (GDP per Capita)',
    'Family',
    'Health (Life Expectancy)',
    'Freedom',
    'Trust (Government Corruption)',
    'Generosity'
]

# === Initialize app ===
app = dash.Dash(__name__)

# === Layout ===
app.layout = html.Div([

    html.H1("World Happiness Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Select Region(s):"),
        dcc.Dropdown(
            options=[{'label': r, 'value': r} for r in sorted(df['Region'].unique())],
            value=sorted(df['Region'].unique()),
            multi=True,
            id='region-filter'
        )
    ], style={'width': '50%', 'margin': 'auto'}),

    html.Div([
        dcc.Graph(id='scatter-plot'),
        dcc.Graph(id='map-plot'),
        dcc.Graph(id='pie-chart'),
        dcc.Graph(id='corr-heatmap')
    ], style={'width': '90%', 'margin': 'auto'})

])

# === Callback ===
@app.callback(
    Output('scatter-plot', 'figure'),
    Output('map-plot', 'figure'),
    Output('pie-chart', 'figure'),
    Output('corr-heatmap', 'figure'),
    Input('region-filter', 'value')
)
def update_charts(selected_regions):

    # ✅ Handle empty selection
    if not selected_regions:
        filtered_df = df.copy()
    else:
        filtered_df = df[df['Region'].isin(selected_regions)]

    # Scatter
    fig_scatter = px.scatter(
        filtered_df,
        x='Economy (GDP per Capita)',
        y='Happiness Score',
        facet_col='Region',
        facet_col_wrap=3,
        hover_name='Country',
        hover_data={'Health (Life Expectancy)': ':.3f'},
        title='Happiness vs GDP per Capita by Region'
    )

    # Map
    fig_map = px.choropleth(
        filtered_df,
        locations='Country',
        locationmode='country names',
        color='Economy (GDP per Capita)',
        hover_name='Country',
        hover_data={'Health (Life Expectancy)': ':.3f'},
        color_continuous_scale='Viridis',
        title='Global GDP per Capita'
    )

    # Pie
    region_avg = filtered_df.groupby('Region', as_index=False)['Happiness Score'].mean()

    fig_pie = px.pie(
        region_avg,
        names='Region',
        values='Happiness Score',
        title='Average Happiness Score by Region'
    )

    # Correlation heatmap
    corr_matrix = filtered_df[corr_cols].corr()

    fig_corr = px.imshow(
        corr_matrix,
        text_auto=False,
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        title='Correlation Heatmap of Key Factors'
    )

    fig_corr.update_traces(
        text=corr_matrix.round(4).values,
        texttemplate="%{text}",
        textfont_size=14
    )

    fig_corr.update_layout(height=600)
    fig_corr.update_xaxes(tickangle=45)

    return fig_scatter, fig_map, fig_pie, fig_corr


# === Entry point ===
if __name__ == "__main__":
    app.run(debug=True)