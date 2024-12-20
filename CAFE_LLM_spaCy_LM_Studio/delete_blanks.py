import pandas as pd

data_frame = pd.read_excel('CAFE LD NPRM_comments_binning_Deliberative_for ROADII.xlsx')
data_frame = data_frame.dropna(how='all', axis=0)
data_frame.to_excel('no_blanks.xlsx', index=False)
