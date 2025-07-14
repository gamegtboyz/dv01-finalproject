import streamlit as st
import pandas as pd
import plotly.express as px

# Dashboard page and title creation
st.set_page_config(page_title = "Food Imports Summary", page_icon=":pizza:", layout='wide')
st.title(':pizza: US Food Import Dashboard 1999 - 2024')

# import data into work area
raw_data = pd.read_csv('FoodImports.csv', encoding='ISO-8859-1')
raw_data.drop('RowNumber', axis=1, inplace=True)

# preprocess the Import Value
data = raw_data[raw_data['SubCategory'] == 'Foods']
data = data[~data['Commodity'].str.contains('Total')]
data = data[data['UOM'] == 'Million $']
data = data[data['Country'] != 'WORLD']
data['YearNum'] = data['YearNum'].apply(pd.to_numeric)
data.reset_index(inplace=True,drop=True)

# preprocess the Import Quantity
qtydata = raw_data[(raw_data['Category'] == 'Food volume') & ((raw_data['UOM'] == '1,000 mt') | (raw_data['UOM'] == '1,000 litpf'))]
qtydata.rename(columns={'Category':'Dimension', 'Commodity':'Category'},inplace=True)
qtydata['YearNum'] = qtydata['YearNum'].apply(pd.to_numeric)

# preprocess the Import Price
pricedata = raw_data[(raw_data['SubCategory'] == 'Imported food prices') & (raw_data['UOM'] != 'Dollars')].reset_index(drop=True)
pricedata.rename(columns={'Category':'Dimension', 'Commodity':'Category'},inplace=True)
pricedata['YearNum'] = pricedata['YearNum'].apply(pd.to_numeric)

# add the side bar with filters
st.sidebar.header('Filters')
# add the year sidebar
selected_year = st.sidebar.multiselect('Year:',
                                       data['YearNum'].unique(),
                                       default=data['YearNum'].unique())

# add the Country sidebar
selected_country = st.sidebar.multiselect('Country:',
                                          data['Country'].unique(),
                                          default=data['Country'].unique())
# add the Commodity sidebar
selected_category = st.sidebar.multiselect('Commodities:',
                                            data['Category'].unique(),
                                            default=data['Category'].unique())

# create data filtering logic
filtered_amount = data.loc[data['YearNum'].isin(selected_year)&\
                           data['Country'].isin(selected_country)&\
                           data['Category'].isin(selected_category)]

filtered_qty = qtydata.loc[qtydata['YearNum'].isin(selected_year)]

filtered_price = pricedata.loc[pricedata['YearNum'].isin(selected_year)]


# create the dashboard component
# Elements for Metrics
total_import_amount = filtered_amount['FoodValue'].sum()
mostly_imported_food = filtered_amount.groupby('Commodity')['FoodValue'].sum().sort_values(ascending=False).index[0]

col1, col2 = st.columns(2)
col1.metric(label='Total Import Amount', value=f"${(total_import_amount/1000):,.2f}B")
col2.metric(label='Most Import on', value=mostly_imported_food)

# Figure 1: Total Food Import Amount by Country
# group the data
value_by_country = filtered_amount.groupby('Country')['FoodValue'].sum().sort_values(ascending=False)

# create the figure logic and layout
fig = px.choropleth(data_frame=value_by_country.to_frame(),
                    locations=value_by_country.index, locationmode='country names',
                    color=value_by_country.values,
                    color_continuous_scale=px.colors.sequential.YlOrRd,
                    labels={'color': 'Import Value (Million $)'},
                    title='Total US Food Import Amount by Country')

# render the figure on page
st.plotly_chart(fig, use_container_width=True)

# Figure 2: Total Food Import Amount by Category
# create the figure logic and layout
fig = px.bar(filtered_amount.groupby(['Category','Commodity'])[['FoodValue']].sum().sort_values(by='FoodValue',ascending=False).reset_index(),
             x='Category', y='FoodValue', color='Commodity')

fig.update_layout(title='Total US Food Import by Category',
                  yaxis={
                      'title':{
                          'text': 'Total Import Amount (Million $)'
                        }
                    }
                )
# render the figure on page
st.plotly_chart(fig, use_container_width=True)

# Figure 3: Import Quantity
# create the figure logic and layout
fig = px.line(filtered_qty,
              x='YearNum', y='FoodValue', color='Category', symbol='Category')

fig.update_layout(title='US Food Import Demand by Qty',
                  yaxis={
                      'title':{
                          'text': 'Import Qty (Metric Tons)'
                        }
                    },
                  xaxis={
                      'title':{
                          'text': 'Year'
                        }
                    }
                )
# render the figure on page
st.plotly_chart(fig, use_container_width=True)

# Figure 4: Commodity Price per Metric Tons
# create the figure logic and layout
fig = px.line(filtered_price,
              x='YearNum', y='FoodValue', color='Category', symbol='Category')

fig.update_layout(title='US Food Import Price per Metric Tons',
                  yaxis={
                      'title':{
                          'text': 'Price ($ per Metric Tons)'
                        }
                    },
                  xaxis={
                      'title':{
                          'text': 'Year'
                        }
                    }
                )
# render the figure on page
st.plotly_chart(fig, use_container_width=True)