import streamlit as st

import pandas as pd


product_file = st.file_uploader(
    "Choose the Product file (After Filling it Up)"
)

category_file = st.file_uploader(
    "Choose the Category file"
)





def get_report(product_file, categ_file):
    import pandas as pd
    prod = pd.read_csv(product_file)

    ## FILES
    prod_clean = (prod
    [['id', 'public_categ_ids']]
    .dropna(subset='public_categ_ids')
    )
    categ = pd.read_csv(categ_file).to_dict()


    # GET NAME_TO_ID MAPPER
    display_names, ids = (categ['Display Name'].values(), categ['External ID'].values())
    name_to_id = dict(zip(display_names, ids))

    # GET ROW MAPPER
    def mapper(x):
        categ_names = x.split(',')
        return ','.join([name_to_id[c] for c in categ_names])

    _ = prod_clean['public_categ_ids'].apply(mapper)
    prod_clean['public_categ_ids/id'] = _
    prod_clean.drop('public_categ_ids', axis=1, inplace=True)
    return prod_clean
    

if st.button('Get Report'):
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(get_report(product_file, category_file))

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="output.csv",
        mime="text/csv",
    )
