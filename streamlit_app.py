# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write(
    """Choose the fruit you want in your custom Smoothie!"""
)

name_on_order = st.text_input('Name on Smoothie:')

st.write(
    'The name on your smoothie will be:',
    name_on_order
)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get FRUIT_NAME and SEARCH_ON from the table
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select(
    col('FRUIT_NAME'),
    col('SEARCH_ON')
)

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Use FRUIT_NAME for the Multiselect
ingredients_list = st.multiselect(
    'choose upto 5 ingredients:',
    pd_df['FRUIT_NAME']
)

if ingredients_list:

    ingredients_string = ''

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + ' '

        # Get the SEARCH_ON value for the selected fruit
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen,
            'SEARCH_ON'
        ].iloc[0]

        st.write(
            'The search value for ',
            fruit_chosen,
            ' is ',
            search_on,
            '.'
        )

        # Display nutrition information
        st.subheader(
            fruit_chosen + ' Nutrition Information'
        )

        # Call SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Create INSERT statement
    my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

    # Submit button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success(
            'Your Smoothie is ordered!',
            icon="✅"
        )
