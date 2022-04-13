from flask import Flask,  request, jsonify
import os
from werkzeug.utils import secure_filename
from azure.storage.blob import BlockBlobService
app = Flask(__name__)

app.secret_key = "camcorders-ednalan"

curr_dir = os.path.abspath(os.path.join(os.path.abspath(os.getcwd())))
UPLOAD_FOLDER = curr_dir + '/Upload'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return 'Homepage'


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'files' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    account_name = 'pm360ngdevelopmentfe'
    account_key = 'lcQA3/mjYvN8m4oUe/ZlAc62hcdBNjhOigd74d9RRfcw+zhKCSxHmg7hOWTxe9XIChBVE0wQ1BM3qV99/mUU1A=='
    container_name = 'new'
    block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
    files = request.files.getlist('files')

    errors = {}
    success = False
    path = f"{UPLOAD_FOLDER}"
    file_names = os.listdir(path)
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_names = os.listdir(path)
            print(file_names)
            for file_name in file_names:
                blob_name = f"{file_name}"
                file_path = f"{path}/{file_name}"
                block_blob_service.create_blob_from_path(container_name, blob_name, file_path)
                os.remove(f"{UPLOAD_FOLDER}/{file_name}")
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


if __name__ == '__main__':
    app.run(debug=True)