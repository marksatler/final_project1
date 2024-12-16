"""
Class: CS230--Section 1 
Name: Mark Satler
Description: Final Project
I pledge that I have completed the programming assignment independently. 
I have not copied the code from a student or any source.
I have not given my code to any student. 
"""
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np
import folium
from streamlit_folium import st_folium


#[PY3] Error checking w/ try
def load_data():
    try:
        data = pd.read_csv('nuclear_explosions.csv')

#[DA1] Clean column names
        data.columns = data.columns.str.strip()

#[DA1] Construct a date column
        data['Date'] = pd.to_datetime(
            data[['Date.Year', 'Date.Month', 'Date.Day']].astype(str).agg('-'.join, axis=1),
            errors='coerce'
        )

#[DA9] Make sure 'Yield' column is numeric
        if 'Yield' in data.columns:
            data['Yield'] = pd.to_numeric(data['Yield'], errors='coerce')
        else:
            data['Yield'] = np.nan

        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


#[PY1] A fcn w/ 2 or more parameters, one of which has a default value
def filter_data_by_country_and_date(data, country="USA", start_date="1950-01-01", end_date="1998-12-31"):
#Filter by country and date range
    filtered_data = data[
        (data['WEAPON SOURCE COUNTRY'] == country) &
        (data['Date'] >= start_date) &
        (data['Date'] <= end_date)
        ]
    return filtered_data


#[PY2] A fcn that returns more than one value
def get_top_test_years(data, top_n=5):
    #Group data by year and count occurrences
    grouped = data.groupby(data['Date'].dt.year).size()
#Sort by count and return top N years
    sorted_years = grouped.sort_values(ascending=False).head(top_n)
    return sorted_years.index, sorted_years.values


#[PY4] A list comprehension
def get_unique_purposes(data):
#Extract unique purposes of nuclear tests
    return [purpose for purpose in data['Data.Purpose'].dropna().unique()]


#Initialize streamlit
data = load_data()
st.set_page_config(page_title="Nuclear Tests Analysis", layout="wide")

#[ST4] Sidebar navigation
st.sidebar.title("Navigation")
menu = ["Introduction", "Query 1: Total Tests Over Time", "Query 2: Test Locations", "Query 3: Tests by Purpose"]
choice = st.sidebar.radio("Go to:", menu, key="unique_navigation_key")

if data.empty:
    st.error("The dataset could not be loaded. Please check the file and try again.")
else:
    if choice == "Introduction":
        st.title("Nuclear Explosions Data Explorer")
        st.markdown("""
                    This application allows you to explore data on nuclear explosions from 1945 to 1998. 
                    You can analyze the number of tests conducted by different countries, their locations, and the purpose of the tests.
                """)
#[VIZ1] Displaying audio/visuals
        st.audio('explosion.mp3', format='audio/mp3')
        st.image('pic_4.JPEG', caption="EXPLOSION", use_container_width=True)
        st.image(['pic_1.png', 'pic_2.png', 'pic_3.png'], caption=['BOOM', '🤯', 'POW'], use_container_width=True)

    elif choice == "Query 1: Total Tests Over Time":
        st.title("Total Number of Nuclear Tests Over Time")

#[ST1] Dropdown for selecting the country
        countries = data['WEAPON SOURCE COUNTRY'].dropna().unique()
        selected_country = st.selectbox("Select a Country", countries)

#[ST2] Slider for date range
        min_date, max_date = data['Date'].min().date(), data['Date'].max().date()
        date_range = st.slider("Select Date Range", min_value=min_date, max_value=max_date, value=(min_date, max_date))
        date_range = (pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]))

#Filter data by the selected country and date range
        filtered_data = data[(data['WEAPON SOURCE COUNTRY'] == selected_country) &
                             (data['Date'] >= date_range[0]) &
                             (data['Date'] <= date_range[1])]

#[DA6] Analyze data with pivot tables
        timeline = filtered_data.groupby(filtered_data['Date'].dt.year).size().reset_index(name="Count")

#[VIZ2] Plot using Matplotlib
        fig, ax = plt.subplots()
        ax.plot(timeline['Date'], timeline['Count'], marker='o', linestyle='-', color='blue')
        ax.set_title(f"Nuclear Tests Over Time ({selected_country})")
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Tests")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    elif choice == "Query 2: Test Locations":
        st.title("Locations of Nuclear Tests")

#[ST3] Dropdown for selecting the country
        countries = data['WEAPON SOURCE COUNTRY'].dropna().unique()
        selected_country = st.selectbox("Select a Country", countries)

        if 'Location.Cordinates.Latitude' in data.columns and 'Location.Cordinates.Longitude' in data.columns:
            location_data = data[data['WEAPON SOURCE COUNTRY'] == selected_country].dropna(
                subset=['Location.Cordinates.Latitude', 'Location.Cordinates.Longitude'])
            if not location_data.empty:
#[MAP] Folium map w/ markers
                center_lat = location_data['Location.Cordinates.Latitude'].mean()
                center_lon = location_data['Location.Cordinates.Longitude'].mean()
                test_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

                for _, row in location_data.iterrows():
                    folium.Marker(
                        location=[row['Location.Cordinates.Latitude'], row['Location.Cordinates.Longitude']],
                        popup=(
                            f"Date: {row['Date'].strftime('%Y-%m-%d')}<br>"
                            f"Purpose: {row['Data.Purpose'] if 'Data.Purpose' in row else 'Unknown'}<br>"
                            f"Yield: {row['Yield'] if 'Yield' in row else 'N/A'}"
                        )
                    ).add_to(test_map)
                st_folium(test_map, width=800, height=500)

    elif choice == "Query 3: Tests by Purpose":
        st.title("Number of Tests by Purpose")

#[ST3] Multiselect for selecting test purposes
        if 'Data.Purpose' in data.columns:
            purposes = data['Data.Purpose'].dropna().unique()
            selected_purposes = st.multiselect("Select Test Purposes", purposes, default=purposes)

#[DA5] Filter data by multiple conditions
            purpose_data = data[data['Data.Purpose'].isin(selected_purposes)]
            if not purpose_data.empty:
#[DA2] Sort data in descending order
                purpose_summary = purpose_data.groupby('WEAPON SOURCE COUNTRY').size().reset_index(
                    name="Count").sort_values(
                    by="Count", ascending=False)

#[VIZ3] Bar chart visualization
                st.bar_chart(purpose_summary.set_index('WEAPON SOURCE COUNTRY')['Count'])

#[VIZ4] Display data as a table
                st.dataframe(purpose_summary)
