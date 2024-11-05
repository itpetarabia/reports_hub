import os

import pandas as pd
import paramiko
import streamlit as st

# Example of locations dictionary
locations = {
    "Budaiya Branch/Stock": "46890",
    "Saar Branch/Stock": "46891",
    "Manama Branch/Stock": "46894",
    "Sanad Branch/Stock": "46895",
    "Physical Locations/Amwaj Branch/Stock": "46896"
}

os.makedirs('talabat_files', exist_ok=True)

def process_file(stock_file_as_binary):
    # Load the product and stock files
    products_df = pd.read_csv('products.csv', dtype={'Product/Barcode': str})  # Contains barcodes
    products_df.drop('Price', axis=1, inplace=True)

    stock_df = pd.read_csv(stock_file_as_binary, dtype={'Product/Barcode': str})        # Contains stock info, including 'Location' and 'Quantity' columns

    # Pivot stock data to have one column per location
    stock_df.dropna(subset='Product/Barcode', axis=0, inplace=True)
    # prices_df = stock_df[['Product/Barcode', 'Product/Sales Price']].drop_duplicates()
    prices_df = pd.read_csv('all.products.csv', dtype={'Public Price': float})

    columns_to_select = ['Product/Barcode', 'Location', 'Available Quantity']
    stock_df = stock_df[columns_to_select].copy()
    stock_df = stock_df[stock_df.Location.isin(locations.keys())].copy()
    stock_df = stock_df.groupby(['Product/Barcode', 'Location']).sum().reset_index()



    stock_pivot = stock_df.pivot_table(index='Product/Barcode', columns='Location', values='Available Quantity', aggfunc='sum')

    # Ensure that all locations in the locations dictionary are present as columns
    for loc in locations.keys():
        if loc not in stock_pivot.columns:
            stock_pivot[loc] = 0  # Initialize missing location columns with 0

    # # Reset index to turn 'barcode' back into a column
    stock_pivot.reset_index(inplace=True)

    # # Merge the products dataframe with the stock pivoted dataframe on 'barcode'
    merged_df = pd.merge(products_df, stock_pivot, on='Product/Barcode', how='left')

    # # Fill any remaining NaN values with 0 (in case some barcodes are missing stock info for some locations)
    merged_df = merged_df.fillna(0)
    merged_df = merged_df.merge(prices_df, on='Product/Barcode', how='left')
    merged_df.drop('id', axis=1, inplace=True)
    merged_df.rename(columns={'Product/Barcode': 'Barcode', 'Public Price': 'original_price'}, inplace=True)
    # print(merged_df)
    # # Save the final result to a CSV
    output_file = 'updated_stock.csv'

    merged_df.to_csv(output_file, index=False)
    
    necessary_columns = pd.read_csv('sftp_format.csv').columns
    
    print(merged_df)
    # Talabat Specifications
    for col, talabat_id in locations.items():
        branch_df = pd.concat([merged_df[['Barcode', 'original_price']], merged_df[[col]]], axis=1)
        branch_df.rename(columns={col: 'active'}, inplace=True)
        branch_df.active = branch_df.active.apply(lambda x: 1 if x>0 else 0)
        columns_hidden = list(set(necessary_columns) - set(branch_df.columns))
        branch_df[columns_hidden] = ''
        

        branch_df[necessary_columns].to_csv(f'talabat_files/petarabia_{talabat_id}.csv', index=False)
        # break

    print(f"Stock information updated and saved to {output_file}")




# SFTP server detail
# env = st.secrets

hostname = st.secrets['SFTP_HOSTNAME']
port = int(st.secrets['SFTP_PORT'])
username = st.secrets['SFTP_USER']
password = st.secrets['SFTP_PASS']
remote_folder = 'assortment'  # The remote folder where you want to copy the file


def sftp_upload_files(list_of_file_paths):
    try:
        # Initialize Transport object
        transport = paramiko.Transport((hostname, port))
        
        # Connect to the server
        transport.connect(username=username, password=password)
        
        # Initialize SFTP session
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Upload the file to the remote folder
        for local_file in list_of_file_paths:
            remote_path = os.path.join(remote_folder, os.path.basename(local_file))
            sftp.put(local_file, remote_path)
            print(f'Successfully uploaded {local_file} to {remote_path}')
        
        # Close the SFTP session
        sftp.close()
        transport.close()
    
    except Exception as e:
        raise f"An error occurred: {e}"


# if __name__ == '__main__':

def process_and_send_stock(binary_file):
    
    process_file(binary_file)
    my_bar = st.progress(0, text='Processing')
    my_bar.progress(0.33, text='Reading File')

    files = [os.path.join('talabat_files', file) for file in os.listdir('talabat_files')]
    my_bar.progress(0.66, text='Sending To Talabat')
    sftp_upload_files(files)
    my_bar.empty()
    st.success('Done 🎉')
    
