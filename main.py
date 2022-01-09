import streamlit as st
import pandas as pd
from datetime import datetime
import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


#@st.cache(ttl=1000000000000000000)
@st.cache()
def load_data():
    df0 = pd.read_csv('marketing_campaign.csv', delimiter='\t')
    df0['Age'] = df0['Year_Birth'].apply(lambda x: datetime.now().year - x)
    df0['nos_year_enroll'] = ((datetime.now() - pd.to_datetime(df0['Dt_Customer'])).dt.days/365).apply(math.floor)
    return df0


def boxplot(df0, item_dict, row_nos, column_nos, group_by=False, gb_column=None):
    new_fig = make_subplots(rows=row_nos, cols=column_nos)
    r, c = 1, 1
    for key in item_dict.keys():
        if group_by:
            fig0 = go.Box(y=df0[key], x=df0[gb_column], name=f'Amount Spend on {item_dict.get(key)}', boxpoints=False)
        else:
            fig0 = go.Box(y=df0[key], name=f'Amount Spend on {item_dict.get(key)}', boxpoints=False)

        new_fig.append_trace(fig0, row=r, col=c)
        if c == column_nos:
            c = 1
            r += 1
        else:
            c += 1
    return new_fig


st.title('Customer Personality Analysis')

data_load_state = st.text('Loading data...')

df = load_data()

data_load_state.text('Loading data...done!')

feature_dict = {'Education Level': 'Education', 'Marital Status': 'Marital_Status', 'Income': 'Income',
                'Nos of Kid': 'Kidhome', 'Nos of Teen': 'Teenhome', 'Years of Enrollment': 'nos_year_enroll',
                'Days After Last Purchase': 'Recency', 'Age': 'Age'}

main_dropdown = st.sidebar.selectbox(
    "Section:", (["Raw Data", "Customer Information", "Purchasing Behavior", "Marketing Performance"]))


if main_dropdown == "Raw Data":
    st.subheader('Raw data')
    st.write(df)

elif main_dropdown == "Customer Information":
    feature_dropdown1 = st.sidebar.selectbox("Category:", list(feature_dict))

    filtering = st.sidebar.selectbox("Filter by:", ['None'] + list(feature_dict))

    if filtering != 'None':
        column = feature_dict.get(filtering)

        if filtering in ['Age', 'Income', 'Days After Last Purchase']:
            slider = st.slider("Range", value=[0, int(df[column].max())])
            filtered_df = df[(df[column] > slider[0]) & (df[column] < slider[1])]
        else:
            category = st.sidebar.multiselect(f"Select the {filtering}", options=df[column].unique(), default=df[column].unique())
            filtered_df = df[df[column].isin(category)]
    else:
        filtered_df = df

    if feature_dropdown1 in ['Income', 'Age', 'Days After Last Purchase']:
        fig = px.histogram(filtered_df, x=feature_dict.get(feature_dropdown1))
    else:
        new_df = filtered_df.groupby(feature_dict.get(feature_dropdown1)).size()
        fig = px.pie(new_df, values=new_df.values, names=new_df.index, title=f'Proportion of {feature_dropdown1}')

    st.plotly_chart(fig)

elif main_dropdown == "Purchasing Behavior":

    feature_dropdown2 = st.sidebar.selectbox("Group by Category:", ['None'] + list(feature_dict))

    if feature_dropdown2 in ['Income', 'Age', 'Days After Last Purchase']:
        column = feature_dict.get(feature_dropdown2)
        slider = st.slider("Range", value=[0, int(df[column].max())])
        filtered_df = df[(df[column] > slider[0]) & (df[column] < slider[1])]
    else:
        filtered_df = df

    item_dict = {'MntWines': 'Wines', 'MntFruits': 'Fruits', 'MntMeatProducts': 'Meat Products',
                 'MntFishProducts': 'Fish Products', 'MntSweetProducts': 'Sweet Products',
                 'MntGoldProds': 'Gold Products'}

    if feature_dropdown2 in ['None', 'Age', 'Income', 'Days After Last Purchase']:
        fig = boxplot(filtered_df, item_dict, 3, 2)

    else:
        column = feature_dict.get(feature_dropdown2)
        fig = boxplot(filtered_df, item_dict, 3, 2, group_by=True, gb_column=column)

    fig.update_layout(height=1200, width=1000)
    st.plotly_chart(fig)

else:
    feature_dropdown3 = st.sidebar.selectbox("Group by Category:", ['None'] + list(feature_dict))

    if feature_dropdown3 in ['Income', 'Age', 'Days After Last Purchase']:
        column = feature_dict.get(feature_dropdown3)
        slider = st.slider("Range", value=[0, int(df[column].max())])
        filtered_df = df[(df[column] > slider[0]) & (df[column] < slider[1])]
    else:
        filtered_df = df

    if feature_dropdown3 in ['None', 'Age', 'Income', 'Days After Last Purchase']:
        agg_df = filtered_df[['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']].sum()
        fig = px.bar(agg_df, x=agg_df.index, y=agg_df.values)
    else:
        gb_df = filtered_df.groupby(feature_dict.get(feature_dropdown3))[['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5']].sum().reset_index()
        new_gb_df = pd.melt(gb_df, id_vars=[feature_dict.get(feature_dropdown3)], value_vars=['AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5'])
        new_gb_df.columns = ['feature', 'campaign', 'sum']
        fig = px.bar(new_gb_df, x='campaign', y='sum', color='feature')

    st.plotly_chart(fig)


