###################################
# import libraries
import streamlit as st
import pandas as pd
import plotly.express as px

###################################
# page config
st.set_page_config(
    page_title="US Population Insights Dashboard",
    layout="wide",
    initial_sidebar_state="expanded")

###################################
# load & preprocess data
df_main = pd.read_csv('data/layoff_data.csv')

# order months to ensure line graph doesn't change its index
months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
df_main['year'] = df_main['year'].astype(int)
df_main['month'] = pd.Categorical(df_main['month'], categories=months_order, ordered=True)

# fill in missing city data
df_main['city'].fillna("Unknown", inplace=True)

###################################
# sidebar
# assisgn select box for all categorical, assign slider for quantitative family size variable
st.sidebar.title('Variables:')
selected_year = st.sidebar.selectbox('Select Year', [None] + sorted(df_main['year'].unique().tolist()))
selected_layoff = st.sidebar.selectbox('Select Layoff Status', [None] + df_main['layoff'].unique().tolist(), index=1)
selected_sex = st.sidebar.selectbox('Select Sex', [None] + df_main['sex'].unique().tolist())
selected_educlevel = st.sidebar.selectbox('Select Education Level', [None] + df_main['educlevel'].unique().tolist())
selected_marstatus = st.sidebar.selectbox('Select Marital Status', [None] + df_main['marstatus'].unique().tolist())
selected_famincome = st.sidebar.selectbox('Select Family Income', [None] + df_main['famincome'].unique().tolist())
selected_famtype = st.sidebar.selectbox('Select Family Type', [None] + df_main['famtype'].unique().tolist())
selected_famsize_range = st.sidebar.slider('Select Family Size Range', 
                                            min_value=int(df_main['famsize'].min()), 
                                            max_value=int(df_main['famsize'].max()), 
                                            value=(int(df_main['famsize'].min()), int(df_main['famsize'].max())))
###################################
# still sidebar, donut chart logic
# subheader on sidebar for time- & location-based filters for donut chart
st.sidebar.subheader('Donut Chart Filters')
donut_year = st.sidebar.selectbox('Select Year for Donut Chart', [None] + sorted(df_main['year'].unique().tolist()))
donut_month = st.sidebar.selectbox('Select Month for Donut Chart', [None] + months_order)

# filter data for donut chart based on selected month and year -- separate from core dashboard filters
if donut_year and donut_month:
    df_donut = df_main[(df_main['year'] == donut_year) & (df_main['month'] == donut_month)]
else:
    df_donut = df_main

donut_region = st.sidebar.selectbox('Select Region', [None] + sorted(df_donut['region'].dropna().unique().tolist()))
donut_state = st.sidebar.selectbox('Select State', [None] + sorted(df_donut[df_donut['region'] == donut_region]['state'].dropna().unique().tolist()) if donut_region else [])
donut_city = st.sidebar.selectbox('Select City', [None] + sorted(df_donut[df_donut['state'] == donut_state]['city'].dropna().unique().tolist()) if donut_state else [])

if donut_region:
    df_donut = df_donut[df_donut['region'] == donut_region]
if donut_state:
    df_donut = df_donut[df_donut['state'] == donut_state]
if donut_city:
    df_donut = df_donut[df_donut['city'] == donut_city]
    
###################################
# add data filter function based on user selected demographic inputs
def filter_data(df, year, layoff, sex, educlevel, marstatus, famincome, famtype, famsize_range):
    # apply filters only if a specific selection is made
    if year:
        df = df[df['year'] == year]
    if layoff:
        df = df[df['layoff'] == layoff]
    if sex:
        df = df[df['sex'] == sex]
    if educlevel:
        df = df[df['educlevel'] == educlevel]
    if marstatus:
        df = df[df['marstatus'] == marstatus]
    if famincome:
        df = df[df['famincome'] == famincome]
    if famtype:
        df = df[df['famtype'] == famtype]
    if famsize_range:
        min_size, max_size = famsize_range
        df = df[(df['famsize'] >= min_size) & (df['famsize'] <= max_size)]
    return df


# create filtered dataframe given user selected filters
filtered_df = filter_data(df_main, selected_year, selected_layoff, selected_sex, selected_educlevel,
                          selected_marstatus, selected_famincome, selected_famtype, selected_famsize_range)

###################################
# visualizations based on user-filtered data

# create choropleth based on states to US-map
def create_choropleth(df):
    # aggregate the population data by state
    state_data = df.groupby('state')['propweight'].sum().reset_index()
    state_data['propweight'] = state_data['propweight'].round()
    state_data.rename(columns={'propweight': 'population'}, inplace=True)
    
    # map filtered data to choropleth
    fig = px.choropleth(state_data, 
                        locations='state', 
                        locationmode='USA-states', 
                        color='population', 
                        scope="usa", 
                        range_color=(0, max(state_data['population'])), 
                        title='Population by State',
                        labels={'population': 'Population'},
                        color_continuous_scale='Blues',
                        )
    # apply dark theme for continuity
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        )
    return fig

# create linegraph (quarterly to adjust for missing data due to layoff filter)
def create_linegraph(df, year):
    # print a warning if year is None to avoid error on dashboard
    if year is None:
        st.warning("Select a year to view trends.")
        return None

    # Map months to quarters
    month_to_quarter = {
        'Jan': 'Q1', 'Feb': 'Q1', 'Mar': 'Q1',
        'Apr': 'Q2', 'May': 'Q2', 'Jun': 'Q2',
        'Jul': 'Q3', 'Aug': 'Q3', 'Sep': 'Q3',
        'Oct': 'Q4', 'Nov': 'Q4', 'Dec': 'Q4'
    }

    # exclude cities missing data
    df_known_cities = df[df['city'] != 'Unknown']

    # create a 'quarter' column based on 'month' mapping above
    df_known_cities['quarter'] = df_known_cities['month'].map(month_to_quarter)

    # aggregate population by city to find top 5
    city_totals = df_known_cities[df_known_cities['year'] == selected_year].groupby('city')['propweight'].sum().reset_index()
    city_totals['propweight'] = city_totals['propweight'].round()
    # assign top 5 cities based on population after filtering
    top_cities = city_totals.nlargest(5, 'propweight')['city']
    
    # filter data to only pull the identified top cities
    df_top_cities = df_known_cities[df_known_cities['city'].isin(top_cities)]

    # prepare variables for line graph
    line_data = df_top_cities.groupby(['quarter', 'city'])['propweight'].sum().reset_index()
    line_data.sort_values(by=['quarter'], inplace=True)


    # set color scale for continuity
    num_cities = len(top_cities)
    colors = px.colors.sequential.Blues[-num_cities:]

    # create line graph
    fig = px.line(line_data, x='quarter', y='propweight', color='city', title=f'Top 5 Cities Population Trends in {selected_year} by Quarter',
                  markers=True, labels={'propweight': 'Population'},
                  color_discrete_map={city: colors[i] for i, city in enumerate(top_cities)})
    # apply dark theme for continuity
    fig.update_layout(
        template='plotly_dark', 
        plot_bgcolor='rgba(0, 0, 0, 0)', 
        paper_bgcolor='rgba(0, 0, 0, 0)',
        )
    return fig

###################################
# page layout
left_column, right_column = st.columns([0.25, 1])

# Left Column: donut chart and data disclaimer
with left_column:
    st.subheader("Population Proportion Chart")
    category = st.selectbox("Select Category", ['layoff', 'sex', 'educlevel', 'marstatus', 'famincome'])
    
    # Calculate the total and filtered populations
    total_population = df_main['propweight'].sum()
    filtered_population = df_donut['propweight'].sum()
    percentage_of_total = (filtered_population / total_population) * 100
    
    if not df_donut.empty:
        fig = px.pie(df_donut, names=category, title=f'Proportional Representation of {category}', hole=0.5)
        fig.update_layout(
            annotations=[dict(text=f'{percentage_of_total:.2f}% of total', x=0.5, y=0.5, font_size=16, showarrow=False)],
            uniformtext_minsize=15,
            uniformtext_mode='hide'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No data available for selected year and month.")
    
    st.write("Dataset Reservations:")
    st.markdown("""
    - The data was filtered to only include records with 'Yes' or 'No' in the laid off from full time job category.
    - Some location data are generalized or missing; entries without a specified city are labeled as 'Unknown'.
    """)

# Right Column: main visualizations
with right_column:

    # create choropleth map from the filtered data
    choropleth_map = create_choropleth(filtered_df)
    st.plotly_chart(choropleth_map, use_container_width=True)

    # create line graph from the filtered data
    line_graph = create_linegraph(filtered_df, selected_year)
    if line_graph:
        st.plotly_chart(line_graph, use_container_width=True)
