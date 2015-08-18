import numpy as np
from SudokuImage import SudokuImage as sdku_img

class Sudoku():
    
    def __init__(self, sudoku_array):
        self.cells = sudoku_array



    def solve(self):
        solved_sudoku = self.cells
        solution = self.sudoku_solver(solved_sudoku)
        return solution
        

    def sudoku_solver(self, sudoku_grid):
        
        TF,row,col = self.find_empty_cell(sudoku_grid)
        
        if TF == False: return True, sudoku_grid
        
        for n in range(1,10):
            if self.no_conflict(sudoku_grid, row, col, n):

                sudoku_grid[row,col] = n
                
                if( self.sudoku_solver(sudoku_grid)[0] ): 
                    return True, sudoku_grid
                    
                sudoku_grid[row, col] = 0
                
        return False, sudoku_grid


    def find_empty_cell(self, sudoku_grid):

        for i in range(9):
            row = i
            for j in range(9):
                col = j
                if sudoku_grid[i,j]==0: 
                    return True, row, col

        return False,-1,-1


    def no_conflict(self, sudoku_grid, row,col, value):
        
        notincol = False
        notinrow = False
        notinbox = False
        
        if value not in sudoku_grid[row,:]:
            notincol = True
            
        if value not in sudoku_grid[:,col]:
            notinrow = True
            
        start_row = row/3
        start_col = col/3
    
        if value not in sudoku_grid[start_row*3: start_row*3 + 3, 
                                    start_col*3: start_col*3 + 3]:
            notinbox = True
        
        
        return (notincol and notinrow and notinbox)
