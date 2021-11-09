from flask import Flask
import dash
from dash import dcc
from dash import html
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import scipy as sp
from statsmodels.formula.api import ols
external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']

server=Flask(__name__)
app=dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)


chart1Source=pd.DataFrame({
    'GSR':[384, 425, 399, 344, 379, 443, 460, 387, 399, 398,357,393,407,439,371,403,375,245,162,168],
    'HRV':[0.929152,0.696864,0.763232,0.763232,0.962336,0.91256,0.846192,0.763232,0.74664,0.8296,
           0.779824,0.564128,0.91256,0.8296,0.564128,0.929152,0.730048,0.813008,0.431392,0.613904],
    'Temperature':[33.34,33.38,33.62,33.66,33.52,33.61,33.3,33.23,33.21,33.21,
                   33.3,33.24,33.24,33.25,33.72,33.38,33.05,32.92,32.7,32.17]
})
#GSRFormula = -0.05 * Temperature + 400 (Dummy formula)
chart1Source['GSRCalculated']=chart1Source['Temperature']*(-0.05) + 400
chart1Source['deltaGSR']=chart1Source['GSRCalculated']-chart1Source['GSR']
chart1Source['Healthy']=chart1Source.apply(lambda row : row['deltaGSR']>0, axis=1).astype(int)
chart1Source['Healthy']=np.where(chart1Source['Healthy'], 'Healthy', 'Unhealthy')
#chart1Source['Healthy'].replace('True', "Healthy")
#chart1Source['Healthy'].replace(False, "Unhealthy")
#chart1Source['healthyHRV']=chart1Source.loc[chart1Source['deltaGSR']>=0]['HRV']

figure1=px.scatter(chart1Source, x='deltaGSR', y='HRV', color='Healthy', trendline="ols", trendline_scope="overall",
                   title="GSR vs HRV")
figure1.add_vline(x=0, line_dash="dot")
figure1.add_vrect(x0=0, x1=300, 
              annotation_text="Healthy HRV", annotation_position="top left",
              fillcolor="blue", opacity=0.1, line_width=0)
figure1.add_vrect(x0=-100, x1=0, annotation_text="Unhealthy HRV", annotation_position="top right", fillcolor="red", opacity=0.1, line_width=0)


chart2Source=pd.DataFrame({
    'Time':[1557286092300, 1557286182500, 1557286663900, 1557287476100, 1557288258200,
            1557288739500, 1557290604800, 1557291056200, 1557291116100, 1557291567400,
            1557292289300, 1557292469800, 1557292770700, 1557294124300, 1557294337700,
            1557294395900, 1557294425900, 1557294455900, 1557294485300, 1557294576500],
    'HRV':[0.929152,0.696864,0.763232,0.763232,0.962336,0.91256,0.846192,0.763232,0.74664,0.8296,
           0.779824,0.564128,0.91256,0.8296,0.564128,0.929152,0.730048,0.813008,0.431392,0.613904]
})

chart2Source['Timestamp']=pd.to_datetime(chart2Source['Time'], unit='ms')
chart2Source['Healthy']=chart2Source.apply(lambda row : row['HRV']>0.799592, axis=1).astype(int)
chart2Source['Healthy']=np.where(chart2Source['Healthy'], 'Healthy', 'Unhealthy')

#figure2=px.scatter(chart2Source, x='Timestamp', y='HRV', color='Healthy', title="time vs HRV")
figure2=go.Figure()
figure2.add_trace(go.Scatter(x=chart2Source['Timestamp'], y=chart2Source['HRV'], mode='lines+markers'))

threshold1=chart2Source['HRV'].max()
threshold2=chart2Source['HRV'].quantile(q=0.8413)
threshold3=chart2Source['HRV'].quantile(q=0.5)
threshold4=chart2Source['HRV'].quantile(q=0.1587)
threshold5=chart2Source['HRV'].min()

figure2.add_hrect(y0=threshold2, y1=1, 
              annotation_text="No Stress at all", annotation_position="top right",
              fillcolor="blue", opacity=0.3, line_width=0)

figure2.add_hrect(y0=threshold3, y1=threshold2, 
              annotation_text="Healthy Stress", annotation_position="top right",
              fillcolor="blue", opacity=0.1, line_width=0)

figure2.add_hrect(y0=threshold4, y1=threshold3, 
              annotation_text="Slight Stress", annotation_position="top right",
              fillcolor="red", opacity=0.1, line_width=0)

figure2.add_hrect(y0=0.4, y1=threshold4, 
              annotation_text="Severe Stress", annotation_position="top right",
              fillcolor="red", opacity=0.3, line_width=0)

app.layout=html.Div(children=[
    html.Div(children=['chart 1 - GSR vs HRV']),
    dcc.Graph(
        id='chart1',
        #figure={l
        #    'data': [{
        #        'x':chart1Source['deltaGSR'],
        #        'y':chart1Source['HRV']
        #    }]
        #}
        figure=figure1
    ),
    html.div(children=['chart 2 - time vs HRV']),
    dcc.Graph(
        id='chart2',
        figure=figure2
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)