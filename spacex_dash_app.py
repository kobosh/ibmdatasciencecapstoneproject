# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
options=[{'label':'ALL','value':'ALL'}]
options.extend([{'label':site,'value':site} for site in launch_sites_df['Launch Site']])
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=options,
                                value="ALL",placeholder="select site",searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),



                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                            id='payload-slider',
                                            min=min_payload,  # Minimum payload mass from dataset
                                            max=max_payload,  # Maximum payload mass from dataset
                                            step=1000,  # Adjust step size as needed
                                            marks={i: str(i) for i in range(int(min_payload), int(max_payload) + 1, 2000)},  # Labels every 2000kg
                                            value=[min_payload, max_payload]  # Default range (full range)
                                            ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', 
component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    if entered_site == 'ALL':
        print("all all ")
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Success rates for launch sites')
        return fig  # Always return a figure
    
    else:
        
        # Count successes (1) and failures (0)
        success_count = filtered_df['class'].sum()  # Sum of ones gives count of successes
        failure_count = len(filtered_df) - success_count  # Total - successes = failures
        # Create new DataFrame for pie chart
        site_data = pd.DataFrame({
            'Outcome': ['Success', 'Failure'],
            'Count': [success_count, failure_count]
        })
        # Create Pie Chart
        fig = px.pie(
            site_data, 
            values='Count', 
            names='Outcome', 
            title=f'Success vs Failure for {entered_site}'
        )
        return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    # Extract min/max payload values from the slider
    min_payload, max_payload = payload_range
    
    # Filter data based on site selection
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Apply additional payload mass filter
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= min_payload) &
                              (filtered_df['Payload Mass (kg)'] <= max_payload)]

    # Create scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='class',  # Success (1) vs Failure (0)
        color_discrete_map={0: 'black', 1: 'red'},
        title=f'Payload vs. Success for {entered_site}',
        labels={'class': 'Launch Outcome'},
        hover_data=['Booster Version']
    )
    fig.update_layout(
        plot_bgcolor='white',  # White background
        paper_bgcolor='white',  # White outer background
        font=dict(color='black')  # Black text
    )

    fig.update_traces(marker=dict(size=10, line=dict(width=1, color='darkgray')))  # Bigger markers with borders

    return fig  # Return updated figure
 # Run the app
if __name__ == '__main__':
    app.run_server()
