from flask import Flask, flash,render_template, url_for, request, redirect
from werkzeug import secure_filename
import os
import numpy as np

from SudokuImage import SudokuImage
from Sudoku import Sudoku

application = Flask(__name__)

application.config['UPLOAD_FOLDER'] = 'static/uploads/'
application.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
application.config['SECRET_KEY'] = "hard to guess!string"


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        # Get the name of the uploaded file
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))


            return redirect(url_for('sudoku',
                                    fname = filename))

    return render_template('index.html')
    


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in application.config['ALLOWED_EXTENSIONS']


@application.route('/sudokusolver',methods=['GET', 'POST'])
def sudokusolver():
    
    if request.method == 'POST':

        file = request.files['file']

        if file and allowed_file(file.filename):
            
            filename = secure_filename(file.filename)

            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            
            return redirect(url_for('sudoku',
                                    fname = filename))
            
    return render_template('sudokusolver.html')
    
    


@application.route('/image/<fname>', methods = ['GET', 'POST'])
def sudoku(fname):
    f_path = os.path.join(application.config['UPLOAD_FOLDER'], fname)
    

    # create sudokuimage object
    sdku_img = SudokuImage(f_path)     
    
    # catch any initial image processing errors
    # if len(rows/cols) != 10, the object sets them to false
    if sdku_img.rows and sdku_img.cols:
        
        sudoku_grid = np.zeros((9,9), dtype = int)
        # note: empty cells will be denoted by 0        
        

        # use knn to predict the value of non-empty sdku_img cells
        for cell in sdku_img.predict_cells():
            sudoku_grid[cell[0], cell[1]] = cell[2]
        

        no_failure = True
        solved_grid = sudoku_grid.copy()

        if request.method == 'POST':

            sdku = Sudoku(solved_grid) # create sudoku object

            no_failure, solution = sdku.solve() # solve sudoku
        

            # if sudoku cant be solved, redirect with error message
            # typically this is due to bad prediction
            if not no_failure:
                flash("Oops, I am having trouble processing your Sudoku!  Take a clearer photo and try again.")
                return redirect(url_for('sudokusolver'))

                
            # render when everything goes according to plan
            return render_template('sudoku_image.html',image =
                                   url_for('static', 
                                           filename = 'uploads/'+fname),
                                   initial_sudoku = sudoku_grid, 
                                   solved_sudoku = solved_grid)
        
        # initial rendering to user, before they hit submit
        return render_template('sudoku_image.html',image =
                               url_for('static', 
                                       filename = 'uploads/'+fname),
                               initial_sudoku = sudoku_grid, 
                               solved_sudoku = solved_grid)

    else:

        # this is rendered when the image can't be processed initially
        flash("Oops, I am having trouble processing your Sudoku!  Take a clearer photo and try again.")
        return redirect(url_for('sudokusolver'))



if __name__ == "__main__":
    application.run(debug=False)
