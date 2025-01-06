import pandas as pd

def get_cats(file_path, start_row, end_row, column_index):
    df = pd.read_excel(file_path, header=None)
    categories = df.iloc[start_row-1:end_row, column_index].apply(lambda x: str(x).strip().lower()).unique().tolist()
    return categories

file_path = 'CAFE LD NPRM_comments_binning_Deliberative_for ROADII.xlsx'
start_row = 2
end_row = 1150
column_index = 7  

unique_cats = get_cats(file_path, start_row, end_row, column_index)
print(unique_cats)