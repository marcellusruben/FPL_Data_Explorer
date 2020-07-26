# -*- coding: utf-8 -*-
"""
"""

import pandas as pd
import requests
import streamlit as st
import base64
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.title('Fantasy Premier League Data Explorer')

st.markdown("""
This app performs webscraping of Fantasy Premier League (FPL) player stats data to make it easier for you to get the necessary data to perform EDA of FPL players or clubs.

You can choose which data from which player or club you want to further analyze by choosing the value from user input features.

Once you get your desired data, you can easily download the table as CSV file and further analyze the data from there.

* **Data source:** [fantasy.premierleague.com](https://fantasy.premierleague.com/api/bootstrap-static/).
""")

st.sidebar.header('User Input Features')

@st.cache
def load_data(name):

    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    u_client = requests.get(url)
    json = u_client.json()

    df = pd.DataFrame(json[name])

    return df

final_df = load_data('elements')
final_df = final_df[['first_name','second_name']+[c for c in final_df if c not in ['first_name','second_name']]] 


teams = load_data('teams')
teams = teams.append({'name':'(All)'}, ignore_index=True)


position = load_data('element_types')
position = position.append({'singular_name':'(All)'}, ignore_index=True)

elements_list = sorted(final_df.columns)

stats = load_data('element_stats')
starter_elements_list = stats['name'].tolist()
names =['first_name','second_name']
starter_elements_list[:0] = names

selected_pos = st.sidebar.selectbox('Position', position['singular_name'], len(position['singular_name'])-1)
selected_team = st.sidebar.selectbox('Team', teams['name'],len(teams['name'])-1) 


selected_element = st.sidebar.multiselect('Features (You can add or remove more than one features)', elements_list, starter_elements_list)


if selected_team != '(All)' and selected_pos != '(All)':
    df = final_df[(final_df.team.isin(teams[teams.name == selected_team]['id'])) & (final_df.element_type.isin(position[position.singular_name == selected_pos]['id']))]
    selected_df = df[selected_element]

elif selected_team == '(All)' and selected_pos == '(All)':
    selected_df = final_df[selected_element]
    
elif selected_team == '(All)' or selected_pos == '(All)':
    if selected_team == '(All)':
        df = final_df[(final_df.element_type.isin(position[position.singular_name == selected_pos]['id']))]
        selected_df = df[selected_element]
        
    else:
        df = final_df[(final_df.team.isin(teams[teams.name == selected_team]['id']))]
        selected_df = df[selected_element]

st.header('Display Player Stats of Selected User Inputs')
st.write('Data Dimension: ' + str(selected_df.shape[0]) + ' rows and ' + str(selected_df.shape[1]) + ' columns.')
st.dataframe(selected_df)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="Premier_League_Stats.csv">Download as CSV File</a>'
    return href

st.markdown(filedownload(selected_df), unsafe_allow_html=True)

st.header('Intercorrelation Matrix Heatmap')
selected_df.to_csv('output.csv',index=False)
df = pd.read_csv('output.csv')
df = df.drop(['first_name','second_name'], axis=1)

corr = df.corr()
mask = np.zeros_like(corr)
mask[np.triu_indices_from(mask)] = True
with sns.axes_style("white"):
        f, ax = plt.subplots(figsize=(13, 11))
        ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
st.pyplot()

plt.rcParams["patch.force_edgecolor"] = True

st.header('Features Data Distribution')

columns = 2
rows = np.ceil(len(df.columns)/columns).astype(int)


plt.figure(figsize=(20,50))

for i in range (len(df.columns)):
    
    plt.subplot(rows, columns, i+1)
    ax = sns.distplot(df[df.columns[i]], norm_hist=False, kde=False, bins = 10)

st.pyplot()
