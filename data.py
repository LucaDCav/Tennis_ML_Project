import pandas as pd
import numpy as np

data = pd.read_csv("./raw_data/atp_matches_till_2022.csv")

#droping unused columns (too many empty values)
cols_to_drop = ['winner_seed', 'winner_entry', 'loser_seed', 'loser_entry']
data.drop(columns=cols_to_drop, inplace= True)
new_data = data.drop(columns=data.iloc[:, 22:])

#filling na's with the mode
cols_to_fill = ['winner_hand', 'loser_hand']
modes = {col: new_copy[col].mode()[0] for col in cols_to_fill}
new_copy = new_data.fillna(modes)

#filling na's with the mean
cols = ['winner_ht', 'winner_age', 'loser_ht', 'loser_age']
new_data[cols] = new_data[cols].apply(lambda col: col.fillna(col.mean()))

#droping rows that have empty values (84 rows removed in total)
new_data = new_data.dropna(subset=['score', 'loser_ioc', 'winner_ioc'])