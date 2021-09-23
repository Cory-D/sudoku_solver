#!/usr/bin/env python3

# Author: Cory Dunn

# import dependencies

import numpy as np
import pandas as pd
import random
import sys

# Load and prepare input sudoku

filename = str(input('Enter the filename of the input suduko (CSV): '))
input_sudoku = pd.read_csv(filename, header = None)
input_sudoku_F = input_sudoku.copy()
input_sudoku_F = input_sudoku_F.fillna(-1)
input_sudoku_F = input_sudoku_F.astype('int8')

# Determine a set of possible entries at each blank space within the sudoku

def possibility_matrix(input_sudoku):
    
    # Set up the possibility dataframe
    
    information_quantity_tabular = pd.DataFrame(index=range(81),columns=['Sudoku_Row','Sudoku_Column','Sudoku_Value','Number_of_Possibilities','List_Possibilities','Not_Possibilities'],dtype='int8')
    information_quantity_tabular['List_Possibilities'] = information_quantity_tabular['List_Possibilities'].astype('object')
    information_quantity_tabular['Not_Possibilities'] = information_quantity_tabular['Not_Possibilities'].astype('object')
    
    # Read the values at each sudoku position and limit the dataframe to blank positions
    
    information_quantity_tabular_counter = 0
    for coli in range(9):
        for rowj in range(9):
            sudoku_value_at_row_column = input_sudoku.iloc[rowj,coli]
            information_quantity_tabular.at[information_quantity_tabular_counter,'Sudoku_Row'] = rowj
            information_quantity_tabular.at[information_quantity_tabular_counter,'Sudoku_Column'] = coli
            information_quantity_tabular.at[information_quantity_tabular_counter,'Sudoku_Value'] = sudoku_value_at_row_column
            information_quantity_tabular_counter += 1
    information_quantity_tabular = information_quantity_tabular[information_quantity_tabular.Sudoku_Value == -1]
    
    # Determine the possible values that could be placed at each position
    
    for fill_number_possibilities in information_quantity_tabular.index.values.tolist():

        possible_set = set([1, 2, 3, 4, 5, 6, 7, 8, 9])

        chosen_row = information_quantity_tabular.at[fill_number_possibilities,'Sudoku_Row']
        chosen_column = information_quantity_tabular.at[fill_number_possibilities,'Sudoku_Column']
        
        # Row values taken
        
        row_values_set = set(input_sudoku.iloc[int(chosen_row),:])
        
        # Column values taken
        
        column_values_set = set(input_sudoku.iloc[:,int(chosen_column)])
        
        # Square values taken
        
        list_of_values_in_square = []
        row_start = int(chosen_row // 3) * 3
        col_start = int(chosen_column // 3) * 3
        for r in range(row_start, row_start + 3):
            for c in range(col_start, col_start + 3):
                list_of_values_in_square.append(input_sudoku[c][r])
        square_values_set = set(list_of_values_in_square)

        not_possible_set =  row_values_set.union(column_values_set, square_values_set)
        possible_set = possible_set - not_possible_set

        possible_set_list = list(possible_set)
        not_possible_set_list = list(not_possible_set)

        information_quantity_tabular.at[fill_number_possibilities,'Not_Possibilities'] = not_possible_set_list
        information_quantity_tabular.at[fill_number_possibilities,'List_Possibilities'] = possible_set_list
        information_quantity_tabular.at[fill_number_possibilities,'Number_of_Possibilities'] = len(possible_set_list)
        
    return information_quantity_tabular

# Change the sudoku based upon possible entries

def change_sudoku(input_working_copy_sudoku):
    
    # Read the possibility matrix given the input sudoku
    
    input_working_information_quantity_tabular = possibility_matrix(input_working_copy_sudoku)
    changed_input_copy_sudoku = input_working_copy_sudoku.copy()
    
    # Find positions most limited in possibilities
    
    minimum_choices = input_working_information_quantity_tabular['Number_of_Possibilities'].min()
    smaller_choice_set = input_working_information_quantity_tabular.loc[input_working_information_quantity_tabular['Number_of_Possibilities'] <= minimum_choices]
    
    # Pick, at random, one of the possibilities for that position and place it in the sudoku
    
    random_choice_of_replacement = smaller_choice_set.sample(frac=1,replace=False)
    row_to_change = random_choice_of_replacement.iloc[0,0]
    column_to_change = random_choice_of_replacement.iloc[0,1]
    value_to_place = random.choice(random_choice_of_replacement.iloc[0,4])
    changed_input_copy_sudoku.at[row_to_change,column_to_change] = value_to_place

    return changed_input_copy_sudoku

# Determine if the sudoku is solved

def main(input_sudoku,input_possibility_matrix):
    current_sudoku = input_sudoku
    updated_possibility_matrix = input_possibility_matrix
    for i in range(len(input_possibility_matrix)):
        current_sudoku = change_sudoku(current_sudoku)
        updated_possibility_matrix = possibility_matrix(current_sudoku)
        
        deadend_flag = updated_possibility_matrix['Number_of_Possibilities'].isin([0]).any()
        if deadend_flag:
            return current_sudoku,updated_possibility_matrix,False

    return current_sudoku,updated_possibility_matrix,True

# Print sudoku dataframe without index and column names

def print_DF_no_row_column(DF):
   
   DF_F = DF.copy()
   DF_F.columns = ['', '', '', '','','','','','']
   DF_F.index = ['' for _ in range(len(DF))]
   print(DF_F.to_string())

# Solve the sudoku

new_possibility_matrix = possibility_matrix(input_sudoku_F)
solve_flag = False
counter = 0
while solve_flag == False:
    output_soduku, output_matrix, solve_flag = main(input_sudoku_F,new_possibility_matrix)
    counter += 1

print("\n\nNumber of restarts as a result of reaching a 'dead-end':", counter)
print("\nSudoku input: ")

input_sudoku = input_sudoku.fillna('-')
input_sudoku = input_sudoku.astype(str).replace('\.0', '', regex=True)
print_DF_no_row_column(input_sudoku)

print("\nSudoku solved: ")
print_DF_no_row_column(output_soduku)
