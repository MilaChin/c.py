import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Load dataset
file_path = "top150.csv"
data = pd.read_csv(file_path, encoding='unicode_escape')
chosen_grp = ""
chosen_act = ""

# [theme]
# base="light"
# primaryColor="#b5d7e4"
# secondaryBackgroundColor="#f1f1f1"
# textColor="#000000"

def find(s, el):
    for i in s.index:
        if s[i] == el:
            return i
    return None

def selection(new_data):
    filter = st.selectbox("Choose a filter", list(["Current annualized turnover", "Current operating profit", "Current operating margin", "Current ROCE"]))
    if filter == "Current annualized turnover":
        chosen_grp = 'AT_current'
    elif filter == "Current operating profit":
        chosen_grp = 'OP_current'
    elif filter == "Current operating margin":
        chosen_grp = 'OM_current'
    elif filter == "Current ROCE":
        chosen_grp = 'ROCE_current(%)'

    TOP_NUM = st.selectbox("Top", list(range(1, len(new_data) + 1)), 9)
    new_data[chosen_grp] = pd.to_numeric(new_data[chosen_grp], errors='coerce')

    print(new_data)
    st.subheader(f"Top {TOP_NUM} {filter}")
    filtered_data = new_data.nlargest(TOP_NUM, chosen_grp)

    print(filtered_data[chosen_grp])
    fig = px.bar(filtered_data, x='comp_name', y=chosen_grp, labels={'comp_name':'Company', chosen_grp:filter})
    fig.update_traces(marker_color='lightblue')
    st.plotly_chart(fig)

def branded():
    # Streamlit input'
    st.subheader("Branded companies")
    new_data = data[data["activity"].isin(["B"])]
    selection(new_data)

def own_brand():
    # Streamlit input'
    st.subheader("Own Branded companies")
    new_data = data[data["activity"].isin(["O/L"])]
    selection(new_data)

def yearend_range(data):
    # Streamlit input
    data = data.sort_values(by='year_end', ascending=True)
    yrend = pd.to_datetime(data["year_end"], format='%b-%y', errors='coerce')

    st.subheader("Calculate companies overall performance")
    min_date = datetime.strptime(str(yrend[0]), '%Y-%m-%d %H:%M:%S')
    max_date = datetime.strptime(str(yrend[yrend.notnull()].max()), '%Y-%m-%d %H:%M:%S')

    selected_date = st.slider(
        "Select a date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MM/YYYY"
    )

    start_date, end_date = selected_date
    start = pd.to_datetime(start_date, format='%b-%y')
    end = pd.to_datetime(end_date, format='%b-%y')

    data['year_end'] = pd.to_datetime(data['year_end'], format='%b-%y')
    filtered_df = data[(data['year_end'] >= start) & (data['year_end'] <= end)]
    # print(filtered_df)


    st.subheader("Select weight of each metric:")
    at_weight = st.selectbox("Annualized turnover: (%)", list(range(0, 100, 10)))
    op_weight = st.selectbox("Operating profit: (%)", list(range(0, 100, 10)))
    roce_weight = st.selectbox("ROCE: (%)", list(range(0, 100, 10)))

    #checking if total weight = 100
    error = False
    if at_weight + op_weight + roce_weight != 100:
        st.markdown(":red[Error: Total weight must add up to 100]")
        error = True


    #ranking
    filtered_df['at_rank'] = pd.Series(dtype='float')
    filtered_df['at_rank'] = filtered_df['AT_yoy'].rank(method='max')

    filtered_df['op_rank'] = pd.Series(dtype='float')
    filtered_df['op_rank'] = filtered_df['OP_yoy'].rank(method='max')

    filtered_df['roce_rank'] = pd.Series(dtype='float')
    filtered_df['roce_rank'] = filtered_df['ROCE_current'].rank(method='max')


    #calculate composite score
    if error == False:
        filtered_df['score'] = pd.Series(dtype='float')
        filtered_df['score'] = filtered_df['at_rank']* at_weight + filtered_df['op_rank'] * op_weight + filtered_df['roce_rank']* roce_weight

        #plot table with order of score
        filtered_df = filtered_df.sort_values(by='score', ascending=False)
        fig = go.Figure(data = [go.Table(
            header = dict(values=['rank', 'Company name', 'AT y-o-y (%)', 'OP y-o-y (%)', 'current ROCE (%)', 'composite score'],
                        fill_color ='lightblue',
                        font = dict(color = 'black'),
                        align ='left'),
            cells = dict(values = [len(filtered_df)+1-filtered_df['score'].rank(method='max', na_option='top'), filtered_df.comp_name, filtered_df.AT_yoy, filtered_df.OP_yoy, filtered_df.ROCE_current, filtered_df.score],
                        fill_color ='beige',
                        font = dict(color = 'black'),
                        align ='left'))
        ])
        st.divider()
        st.subheader("calculate companies overall ranks")
        st.plotly_chart(fig)


def main():
    st.sidebar.title("Market Performance")
    page = st.sidebar.radio(
        "Select one:", ["Branded companies performance", "Own branded companies performance", "Calculate companies overall performance"]
    )
    if page == "Branded companies performance":
        branded()
    elif page == "Own branded companies performance":
        own_brand()
    elif page == "Calculate companies overall performance":
        yearend_range(data)

if __name__ == "__main__":
    main()