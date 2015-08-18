import numpy as np

from PIL import Image
from scipy import misc

from sklearn.neighbors import KNeighborsClassifier
import cPickle as pickle


class SudokuImage():
    
    
    def __init__(self, fname):
        
        # needs to be a b/w representation of the image
        img = None
        self.process_file(fname)


        corners = None
        slants = None
        self.set_edgeinfo()
        
        rows = None
        cols = None
        self.set_columns()
        self.set_rows()

        filled_cells = None
        self.extract_cells()
        

    #--------------------------------------------------#
    #               Find Rows and Cols                 #
    #--------------------------------------------------#

    def set_rows(self):
        
        corners = self.corners
        diff = self.slants
        
        left_diff = diff[0]
        
        nw_row_index = corners[0][0]
        nw_col_index = corners[0][1]
        
        row_length = len(self.img[nw_row_index, :]) + corners[1][1] - corners[0][1]
        col_length = len(self.img[:,nw_col_index]) + corners[3][0] - corners[0][0]
        
        jump = col_length/15
        window_width = row_length/20
        
        Left_indeces = [nw_row_index]
        curr_row_index = jump + nw_row_index
        
        
        while curr_row_index < col_length - jump/5:
            
            travel = curr_row_index - nw_row_index #distance traveled so far
            curr_col_index  = nw_col_index + left_diff*travel/col_length
            
            if self.img[curr_row_index, curr_col_index: curr_col_index + window_width].mean()< 50:
                Left_indeces.append(curr_row_index)
                curr_row_index += jump

            curr_row_index +=1
            
        Left_indeces.append(col_length + corners[0][0])
        
        
        if len(Left_indeces)==10:
            self.rows = Left_indeces
        else:
            self.rows = False

    def set_columns(self):
        
        corners = self.corners
        diff = self.slants
        
        top_diff = diff[1]
        
        nw_row_index = corners[0][0]
        nw_col_index = corners[0][1]
        
        row_length = len(self.img[nw_row_index, :]) + corners[1][1] - corners[0][1]
        col_length = len(self.img[:,nw_col_index]) + corners[3][0] - corners[0][0]
        
        jump = row_length/15
        window_width = col_length/20
        
        curr_col_index = jump + nw_col_index
        
        Top_indeces = [nw_col_index]
        

        
        while curr_col_index < row_length - jump/5:
            
            travel = curr_col_index - nw_col_index #distance traveled so far
            curr_row_index  = nw_row_index + top_diff*travel/row_length
            
            if self.img[curr_row_index: curr_row_index + window_width
                         , curr_col_index].mean()< 50:
                Top_indeces.append(curr_col_index)
                curr_col_index += jump
                
            curr_col_index +=1
            
        Top_indeces.append(row_length + corners[0][1]) 

        if len(Top_indeces)==10:
            self.cols = Top_indeces
        else:
            self.cols = False


    #--------------------------------------------------#
    #            Find Corners and Slant                #
    #--------------------------------------------------#
    
    def set_edgeinfo(self):
        
        bar_height = len(self.img[:,1])/10

        # compute the averages along the edges
        # produce list of the form (avg, index)
        left1 = [(self.img[:bar_height, x].mean(),x) 
                 for x in range(len(self.img[1,:])/15)]
        left2 = [(self.img[-bar_height:, x].mean(),x) 
                 for x in range(len(self.img[1,:])/15)]
        
        right1 = [(self.img[:bar_height, -x-1].mean(),-x-1) 
                  for x in range(len(self.img[1,:])/15)]
        right2 = [(self.img[-bar_height:, -x-1].mean(),-x-1) 
                  for x in range(len(self.img[1,:])/15)]
        
        top1 = [(self.img[x, :bar_height].mean(),x) 
                for x in range(len(self.img[1,:])/15)]
        top2 = [(self.img[x, -bar_height:].mean(),x) 
                for x in range(len(self.img[1,:])/15)]
        
        bottom1 = [(self.img[-x-1, :bar_height].mean(),-x-1) 
                   for x in range(len(self.img[1,:])/10)]
        bottom2 = [(self.img[-x-1, -bar_height:].mean(),-x-1) 
                   for x in range(len(self.img[1,:])/10)]
        
        # reduce the list to the minimal values (darkest cells)
        left1 = [(x,i) for (x,i) in left1 if x < min(left1)[0]+5]
        left2 = [(x,i) for (x,i) in left2 if x < min(left2)[0]+5]
        
        right1 = [(x,i) for (x,i) in right1 if x < min(right1)[0]+5]
        right2 = [(x,i) for (x,i) in right2 if x < min(right2)[0]+5]
        
        top1 = [(x,i) for (x,i) in top1 if x < min(top1)[0]+10]
        top2 = [(x,i) for (x,i) in top2 if x < min(top2)[0]+10]
        
        bottom1 = [(x,i) for (x,i) in bottom1 if x < min(bottom1)[0]+10]
        bottom2 = [(x,i) for (x,i) in bottom2 if x < min(bottom2)[0]+10]
        
        
        # sort the tuples by index, keeping only the index
        left1 = sorted(left1, key = lambda x:x[1])
        left2 = sorted(left2, key = lambda x:x[1])

        right1 = sorted(right1, key = lambda x:x[1])
        right2 = sorted(right2, key = lambda x:x[1])

        top1 = sorted(top1, key = lambda x:x[1])
        top2 = sorted(top2, key = lambda x:x[1])

        bottom1 = sorted(bottom1, key = lambda x:x[1])
        bottom2 = sorted(bottom2, key = lambda x:x[1])
        
        
        # set the indeces
        left1 = left1[len(left1)/2][1] ; left2 = left2[len(left2)/2][1]
        right1 = right1[len(right1)/2][1] ; right2 = right2[len(right2)/2][1]
        top1 = top1[len(top1)/2][1] ; top2 = top2[len(top2)/2][1]
        bottom1 = bottom1[len(bottom1)/2][1] ; bottom2 = bottom2[len(bottom2)/2][1]
        
        # compute the total difference between edges
        top_diff = top2 - top1
        bottom_diff = bottom2 - bottom1
        left_diff = left2 - left1
        right_diff = right2 - right1
    
        # first value corresponds to row
        # secnd value corresponds to col
        nw = (top1, left1)    ; ne = (top2, right1)
        sw = (bottom1, left2) ; se = (bottom2, right2)
        
        
        self.corners  = [nw, ne, se, sw]
        self.slants = [left_diff, top_diff, right_diff, bottom_diff]
        

    
        
    #--------------------------------------------------#
    #          Image Processing Functions              #
    #--------------------------------------------------#
    def process_file(self, fname):
        self.img = np.array(Image.open(fname).convert('L'))
        

        v_threshold = np.vectorize(self.threshold)
        tol = .70

        # partition the rows and columns for iteration
        A = np.linspace(0,self.img.shape[0], num = 25, dtype = int)
        B = np.linspace(0,self.img.shape[1], num = 25, dtype = int)
        
        # A = [int(x) for x in A]
        # B = [int(x) for x in B]

        for i in range(len(A)-1):
            for j in range(len(B)-1):
                
                window = self.img[A[i]:A[i+1], B[j]:B[j+1]]
                white = window.max()
                self.img[A[i]:A[i+1], B[j]:B[j+1]] = v_threshold(window, white, tol)



    def threshold(self, cell_value, white, tol):
        if cell_value > white*tol:
            return 255
        else:
            return 0

    def normalize_image(self,cell_value):
        if cell_value < 70 : 
            return 0
        else:
            return 255

    #--------------------------------------------------#
    #        Cell info Extraction Functions            #
    #--------------------------------------------------#
    def extract_cells(self):
        

        if self.rows == False or self.cols == False:

            self.filled_cells = False
            return 
       

        cells = []
        
        diffs = self.slants
        
        left_diff = diffs[0]
        top_diff = diffs[1]
        right_diff = diffs[2]
        bot_diff = diffs[3]
        

        v_threshold = np.vectorize(self.threshold)
        v_normalize = np.vectorize(self.normalize_image)

        for col in range(9):
            for row in range(9):
                
                h_slope = int((top_diff*(8-row) + bot_diff*(row))/8.)
                v_slope = int((left_diff*(8-col) + right_diff*(col))/8.)
                
                top_row = self.rows[row] + (h_slope*col)/10
                bot_row = self.rows[row+1] + (h_slope*(col+1))/10
                
                left_col = self.cols[col] + (v_slope*row)/10
                right_col = self.cols[col+1] + (v_slope*(row+1))/10
                
                window = self.get_cell(self.img[top_row:bot_row, left_col:right_col])

                if window != None:
                    window = misc.imresize(window, (12,12))#.flatten() # this changes the values
                    window = v_normalize( window )   # renormalize the cell
                    #window = v_threshold( window, window.max(), .8)
                    cells.append( (row, col, window) )


        self.filled_cells = cells


    def get_cell(self, x):

        left = self.find_left(x)
        right = self.find_right(x)
        top = self.find_top(x)
        bottom = self.find_bottom(x)

        if top >= bottom or left >= right: 
            return None
        else:
            return x[top:bottom, left:right]



    def find_top(self, x):
        width = len(x[:,1])/4
        mid_row = len(x[:,1])/2
        while mid_row >= 0:
            if x[mid_row, width:-width].mean() >= 249 : return mid_row 
            mid_row -=1

    def find_bottom(self, x):
        width = len(x[:,1])/4
        mid_row = len(x[:,1])/2
        while mid_row <= len(x[:,1])-1:
            if x[mid_row, width:-width].mean() >= 249 : return mid_row 
            mid_row +=1


    def find_left(self, x):
        width = len(x[1,:])/4
        mid_col = len(x[1,:])/2
        while mid_col >= 0:
            if x[width:-width, mid_col].mean() >= 249 : return mid_col 
            mid_col -=1

    def find_right(self, x):
        width = len(x[1,:])/4
        mid_col = len(x[1,:])/2
        while mid_col <= len(x[1,:])-1:
            if x[width:-width, mid_col].mean() >= 249 : return mid_col 
            mid_col +=1


    def predict_cells(self):
        neigh = pickle.load(open("sudoku_knn.p", "rb"))
        cells = []

        for cell in self.filled_cells:
            cells.append((cell[0], cell[1], neigh.predict(cell[2].flatten())[0]))
        return cells
            
