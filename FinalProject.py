"""
Class: CS230--Section 3
Name: Tim Geromini
Description: This program is my final project. It is a StreamLit application that interprets data on Pubs in England
in various ways including through maps, bar charts, and pie charts.
I pledge that I have completed the programming assignment independently.
I have not copied the code from a student or any source.
I have not given my code to any student.
"""

import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Pubs in England",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache
# Reading in Data
def read_data():
    df = pd.read_csv("Pubs in England.csv", index_col=0, header=[0])
    df.ffill(axis=None, inplace=False, limit=None, downcast=None)
    df.latitude = pd.to_numeric(df.latitude)
    df.latitude = df.latitude.astype(float)
    df.longitude = pd.to_numeric(df.longitude)
    df.longitude = df.longitude.astype(float)
    return df

# Creating Map
def create_map(size, df=read_data()):
    mapFrame = df.filter(['name', 'latitude', 'longitude'])
    view_state = pdk.ViewState(latitude=mapFrame['latitude'].mean(), longitude=mapFrame['longitude'].mean(), zoom=5)
    pubs_layer = pdk.Layer(
        'ScatterplotLayer',
        data=mapFrame,
        get_position='[longitude, latitude]',
        get_radius=size,
        get_color=[232, 70, 70],
        pickable=True)

    tool_tip = {'html': 'Pub:<br><b>{name}</b>', 'style': {'backgroundColor': 'tomato', 'color': 'white'}}


    finalMap = pdk.Deck(
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state=view_state,
        layers=[pubs_layer],
        tooltip=tool_tip
    )
    st.pydeck_chart(finalMap)

# Create Table with Pubs from Unique City
def pub_table(city):
    df = read_data()
    table = df.loc[df['local_authority'].isin(city)]
    return table

# Limits Data to only in Chosen Authority(ies)
def authority_filter(chosen):
    df = read_data()
    df = df.loc[df['local_authority'].isin(chosen)]
    return df

# Counts Number of Pubs in each Chosen Authority
def authority_counter(authorities, df):
    return [df.loc[df['local_authority'].isin([local_authority])].shape[0] for local_authority in authorities]

# Builds Pie Chart Based on Local Authorities and the Frequency
def pie_chart(amount, chosen_authorities):
    plt.figure()
    plt.pie(amount, labels=chosen_authorities, autopct='%.2f', shadow=True)
    plt.title(f"Pub Frequency {', '.join(chosen_authorities)}")
    return plt

# Counts the Frequency of the Number of Selected Pubs
def count_names(data, numPubs):
    names = data['name'].value_counts()[:numPubs].index
    counts = data['name'].value_counts()[:numPubs]
    cord = [i for i in names]
    return names, counts, cord

# Build Bar Chart Based on Selected Number of Pubs and their Frequency
def pubs_bar_chart(pubs, num, cord):
    plt.figure()
    plt.bar(cord, num, color=['blue', 'orange', 'yellow'])
    plt.xticks(cord, pubs, rotation=90)
    for i in range(len(cord)):
        plt.text(i, num[i], num[i], ha = 'center')
    plt.xlabel("Pubs")
    plt.ylabel("Amount")
    plt.title("Popular Pubs and Their Amount")
    return plt

# Count Number of Pubs with Post Code based on Input
def count_postcodes(code, df):
    list = []
    for ind in df.index:
        if df['postcode'][ind] not in list:
            list.append(df['postcode'][ind])
    match = [s for s in list if code in s]
    count = len(match)
    return count

# Build Bar Chart with Post Code and Number
def code_bar_chart(code, count):
    plt.figure()
    plt.bar(code, count, width=0.8, color=['red'])
    plt.xlabel("Post Code")
    plt.ylabel("Number")
    plt.title("Number of Pubs with Selected Postal Code")
    return plt


# Page Layout
def main():
    st.sidebar.title("Directory")
    choice = st.sidebar.selectbox("Choose a Way to View the Data", ("Map", "Charts"))
    st.sidebar.markdown("***************")
    df = read_data()

    # When the user selects map, the map is displayed
    if choice == "Map":

        st.title("Map of Pubs in England")
        st.subheader("Cheers!")
        st.image("flag.jpg", width=750)

        st.markdown("Explore the various Pubs in England with these Interactive Maps")
        st.sidebar.title("Follow the Steps Below to View Specific Pubs in England")
        st.sidebar.markdown("***************")
        size = st.slider("Toggle Point Size", min_value=250, max_value=2000, value=1000, step=50)
        st.write("Map of Pubs (Default Map is Every Pub):")

        # User selects a city and clicks the button to update the map and create a table with only pubs in that city
        # The default for the map is every pub in England
        city = [st.sidebar.selectbox("1. Select a Specific City, or Type to Find a City", (df.local_authority.unique()))]
        st.sidebar.markdown("***************")
        button = st.sidebar.button("2. Click this to View Pubs in Selected City")
        if button:
            st.subheader("The Pubs in Your Selected City are Shown Below: ")
            result = pub_table(city)
            create_map(size, result)
            st.write(result)
        else:
            create_map(size)

    # Once authorities are selected, a pie chart with x number of authorities and their frequency of pubs is displayed
    if choice == "Charts":
        st.title("Analyze Pub Data through Charts")
        st.markdown("Explore the various Pubs in England with these Interactive Charts")
        st.header("Pie Chart")
        st.write("Choose Local Authorities to view Percentage of Pubs in each Authority based on Amount Selected: ")
        authority = st.multiselect("Select a Local Authority: ", (df.local_authority.unique()))
        data = authority_filter(authority)
        amount = authority_counter(authority, data)
        if len(authority) > 0:
            st.pyplot(pie_chart(amount, authority))

        # Once number of pubs is selected, a bar chart with x number of pubs and their frequency is displayed
        st.header("Bar Chart of Pubs")
        numPubs = st.slider("Choose a Number of Pubs to Display: ", min_value=0, max_value=50)
        st.write(f"Bar Chart of the Top {numPubs} Pub Names and their Frequency: ")
        data = read_data()
        if numPubs > 0:
            pubNames, pubCounts, cord = count_names(data, numPubs)
            st.pyplot(pubs_bar_chart(pubNames, pubCounts, cord))

        # Bar Chart showing Number of Pubs with Post Code provided
        st.header("Bar Chart of Postal Codes")
        search = st.text_input("Input the Postal Code you would like to Search For: ")
        data = read_data()
        if search != '':
            codeCount = count_postcodes(search, data)
            st.write(f"There are {codeCount} pubs with the Post Code: {search}")
            st.pyplot(code_bar_chart(search, codeCount))
main()
