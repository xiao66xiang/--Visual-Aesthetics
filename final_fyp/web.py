#################### Import Library #########################
import os
from flask import Flask, render_template, request, redirect, url_for,send_from_directory
from werkzeug import secure_filename
from werkzeug.datastructures import FileStorage
from PIL import Image
import pytesseract
import numpy as np
import cv2
import re
import utility
from utility import image_preprocess, detect_objects, detect_words_images, detect_TLCs, score
from flask import Response

############# Flask Web Applicantion Start Here ##############

# Initialize the Flask application
app = Flask(__name__)
result = []
filenm = ''
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'upload'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['gif', 'jpg', 'jpeg', 'png'])

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']




# this is the home page of web application
#home page address: 127.0.0.1:5000/ or localhost:5000/
@app.route('/')
def index():
    return render_template('index.html')



# Route that will process the file upload
@app.route('/uploaded', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['uploadedPhoto']
    #file = request.files['myform']
    
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect(url_for('uploaded_file',
                                filename=filename))
    else:
    	return 'Sorry you need to choose a file first.'

@app.route('/score/Explanation', methods=['POST'])
def explanation():
   	result[5] = filenm+'dilation.png'
   	return render_template('score.html', result = result)

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/score/<filename>')
def uploaded_file(filename):
  
    ################ Using cv2 to detect object #################    
    #load image
    global result
    global filenm 
    filenm = filename
    imCv2 = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    edged = image_preprocess(imCv2)
    
    total_objects = detect_objects(imCv2,edged)
 #   print(total_objects)
    total_words,total_images,words_size,images_size = detect_words_images(total_objects)
    total_TLCs = detect_TLCs(filename,imCv2,edged)

    # apply formular for Visual Complexity
    vs = round(1.743 + 0.097*total_TLCs + 0.00053*words_size/total_words + 0.00003*images_size/total_images,2)
 #   vs = round(1.743 + 0.097*total_TLCs + 0.053*total_words + 0.003*total_images,2)
    
    final_score = score(vs)
    result = [total_words, total_images,total_TLCs,vs,final_score,filename]
    
    ##############################################################
    return render_template('score.html', result = result)
                           

@app.route('/image/<filename>')
def image(filename):
    return send_from_directory('upload',filename)

if __name__ == '__main__':
    app.run(
        
        debug=True
       
    )

