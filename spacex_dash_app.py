# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                                                    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                                    value='ALL',
                                                    placeholder="Seleccionar un lugar de lanzamiento aquí",
                                                    searchable=True
                                            ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                #creamos las marcas en pasos de 2500. Después es la propia librería la 
                                                #que crea las marcas según los márgenes máximo y mínimo.
                                                marks={i: str(i) for i in range(0, 10001, 2500)},
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value')
                                             )
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Total de éxitos por sitio
        fig = px.pie(spacex_df, 
                     values='class', 
                     names='Launch Site', 
                     title='Total de lanzamientos exitosos por sitio'
                    )
    else:
        # Filtrar el DataFrame por el lugar de lanzamiento seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Agrupar por resultado (éxito = 1, fallo = 0)
        outcome_counts = filtered_df['class'].value_counts().reset_index()
        outcome_counts.columns = ['Outcome', 'Count']
        outcome_counts['Outcome'] = outcome_counts['Outcome'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(outcome_counts, 
                    values='Count', 
                    names='Outcome', 
                    title=f'Lanzamientos en {entered_site}: Éxitos vs Fallos',
                    # Con estas dos lineas puedo cambiar el color
                    color='Outcome',
                    color_discrete_map={'Success': 'green', 'Failure': 'red'}
                    )
    return fig


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    #filtramos por los valores que tengan low i high
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    #Si el sitio es 'ALL' muestra los datos seleccionados en el filtro anterior y dibujamos
    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         #size='Payload Mass (kg)',  Mostaria en el tamaño del punto el valor de Payload (es redundante en este caso)
                         #size_max=30,   Nos da el tamaño máximo de la bola (innecesario porque no usamos size)
                         hover_data=['Payload Mass (kg)'],
                         title='Payload to lunch succes ratio (all sites)',
                         labels={'class': 'Launch succes'})
    #Si seleccionamos un lugar de lanzamiento filtramos por ese lugar y dibujamos
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         #size='Payload Mass (kg)',  Mostaria en el tamaño del punto el valor de Payload (es redundante en este caso)
                         #size_max=30,  Nos da el tamaño máximo de la bola (innecesario porque no usamos size)
                         hover_data=['Payload Mass (kg)'],
                         title=f'Payload to success ratio in {selected_site}',
                         labels={'class': 'Launch succes'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
