import base64
import requests
import pandas as pd
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, callback_context

app = Dash(__name__)

response = requests.get("https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/get_unique_client_ids")

dropdown_options = [{'label': str(client_id), 'value': client_id} for client_id in response.json().get('client_ids', [])]

# Layout de l'application
app.layout = html.Div([
    dcc.Dropdown(
        id='endpoint-dropdown',
        options=[
            {'label': 'Prédiction Client', 'value': 'prediction_client'},
            {'label': 'Prédiction Client Live', 'value': 'prediction_client_live'},
            {'label': 'Data Drift', 'value': 'data_drift'},  # Option pour la fonction data_drift
            {'label': 'Interprétabilité', 'value': 'interpratibilite'},  # Option pour la fonction interpratibilite
            {'label': 'Interprétabilité Globale', 'value': 'interpratibilite_globale'},
            {'label': 'Summary Stats Plot', 'value': 'summary_stats_plot'}  # Option pour summary_stats_plot
        ],
        value='prediction_client'
    ),
    html.Div(id='endpoint-content'),
    
    html.Div(id='client-dropdown'),
    html.Div(id='client-prediction-output')    
])

# Callback pour mettre à jour le contenu en fonction de l'option sélectionnée
@app.callback(
    Output('endpoint-content', 'children'),
    [Input('endpoint-dropdown', 'value')]
)
def update_output(value):
    if value == 'data_drift':
        return html.Div([
            html.A("Cliquez ici pour voir le Data Drift", href=f"https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/data_drift", target="_blank")
        ])
    elif value == 'interpratibilite_globale':
            return None    
    elif value in ['prediction_client', 'prediction_client_live', 'interpratibilite', 'summary_stats_plot']:
        return html.Div([
            html.Label('Sélectionner le client_id :'),
            dcc.Dropdown(
                id='client-dropdown',
                options=dropdown_options,
                value=dropdown_options[0]['value']
            )
        ])

# Callback pour obtenir les prédictions ou le graphique en fonction de l'option sélectionnée
@app.callback(
    Output('client-prediction-output', 'children'),
    [Input('client-dropdown', 'value'),
     Input('endpoint-dropdown', 'value')] 
)
def update_client_prediction(client_id, value):
    if client_id is None:
        return html.Div()
    
    # Si l'option sélectionnée est une des fonctions de prédiction
    if value in ['prediction_client', 'prediction_client_live']:
        response = requests.get(f"https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/{value}?client_id={client_id}")
    # Si l'option sélectionnée est la fonction summary_stats_plot
    elif value == 'summary_stats_plot':
        response = requests.get(f"https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/summary_stats_plot?sk_id_to_display={client_id}")
    # Si l'option sélectionnée est la fonction data_drift
    elif value == 'data_drift':
        return None
    # Si l'option sélectionnée est la fonction data_drift
    elif value == 'interpratibilite_globale':
        response = requests.get("https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/interpratibilite_globale")
        image_base64 = base64.b64decode(response.content)
        return html.Img(src='data:image/png;base64,{}'.format(base64.b64encode(image_base64).decode()), style={'width': '100%'})
    # Si l'option sélectionnée est la fonction interpratibilite
    elif value == 'interpratibilite':
        response = requests.get(f"https://oc-p7-back-10k-13d55ca190cc.herokuapp.com/interpratibilite?sk_id_curr_value={client_id}")
        
    if response.status_code == 404:
        return html.Div('Client ID not found')
    else:
        # Si l'option sélectionnée est summary_stats_plot ou interpratibilite, afficher l'image ou décoder la réponse en base64
        if value in ['summary_stats_plot', 'interpratibilite']:
            response_content = base64.b64decode(response.content)
            return html.Img(src="data:image/png;base64,{}".format(base64.b64encode(response_content).decode()), style={'width': '100%'})
        else:
            # Si l'option sélectionnée est une des fonctions de prédiction ou data_drift, afficher les données
            client_data = response.json()
            formatted_data = "\n".join([f"{key}: {value}" for key, value in client_data.items()])
            return html.Div([
                html.H4(f"Résultats pour le client ID {client_id} :"),
                html.Pre(formatted_data)
            ])

#server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)