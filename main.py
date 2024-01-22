from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
import re
import shutil

app = Flask(__name__, template_folder='v/html', static_folder='v/x')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Function to sanitize a name
def sanitize_name(name):
    sanitized_name = re.sub(r'[^\w\-.]', '', name)
    sanitized_name = sanitized_name.replace(' ', '_')
    return sanitized_name

# Function to create a folder
def create_folder(path, folder_name):
    sanitized_folder_name = sanitize_name(folder_name)
    folder_path = os.path.join(path, sanitized_folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        flash(f'Successfully created folder: {sanitized_folder_name}', 'success')

# Function to list files and folders in a directory
def list_files_and_folders(path):
    items = os.listdir(path)
    return [item for item in items if os.path.isdir(os.path.join(path, item)) or os.path.isfile(os.path.join(path, item))]

# Function to get the parent directory
def get_parent_directory(path):
    return os.path.dirname(path)

# Route for the main page
@app.route('/')
def index():
    current_path = os.getcwd()
    return render_template('index.html', current_path=current_path, items=list_files_and_folders(current_path))

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    current_path = request.form['current_path']
    if file:
        sanitized_file_name = sanitize_name(file.filename)
        file.save(os.path.join(current_path, sanitized_file_name))
        flash(f'Successfully added file: {sanitized_file_name}', 'success')

    # Redirect back to the current folder after uploading the file
    return render_template('index.html', current_path=current_path, items=list_files_and_folders(current_path))

# Route to handle folder creation
@app.route('/create_folder', methods=['POST'])
def create_folder_route():
    folder_name = request.form['folder_name']
    current_path = request.form['current_path']
    create_folder(current_path, folder_name)

    # Redirect back to the current folder after creating the folder
    return render_template('index.html', current_path=current_path, items=list_files_and_folders(current_path))

# Route to delete selected files and folders
@app.route('/delete', methods=['POST'])
def delete_items():
    current_path = request.form['current_path']
    selected_items = request.form.getlist('selected_items')
    passcode = request.form['passcode']

    # Check the passcode (replace 'your_actual_passcode' with the actual passcode)
    if passcode != 'johnlesterdev119119119119119':
        flash('Incorrect passcode. Operation canceled.', 'error')
        return render_template('index.html', current_path=current_path, items=list_files_and_folders(current_path))

    for item in selected_items:
        item_path = os.path.join(current_path, item)
        if os.path.isdir(item_path):
            # Delete folder and its subdirectories
            try:
                shutil.rmtree(item_path)  # Use shutil.rmtree for recursive directory removal
                flash(f'Successfully deleted folder: {item}', 'success')
            except OSError as e:
                flash(f'Error deleting folder: {item} - {e}', 'error')
        elif os.path.isfile(item_path):
            # Delete file
            try:
                os.remove(item_path)
                flash(f'Successfully deleted file: {item}', 'success')
            except OSError as e:
                flash(f'Error deleting file: {item} - {e}', 'error')

    # Redirect back to the current folder after deleting the file
    return render_template('index.html', current_path=current_path, items=list_files_and_folders(current_path))

# Route to handle "Go Up" button
@app.route('/go_up', methods=['POST'])
def go_up():
    current_path = request.form['current_path']

    # Check if the current path is the root directory
    if current_path == "/":
        return redirect(url_for('index'))  # Redirect to the root page

    # Redirect back to the current folder after going up
    return render_template('index.html', current_path=get_parent_directory(current_path), items=list_files_and_folders(get_parent_directory(current_path)))

# Route to handle "Go Up" one level button
@app.route('/go_up_one_level', methods=['POST'])
def go_up_one_level():
    current_path = request.form['current_path']

    # Check if the current path is the root directory
    if current_path == "/":
        return redirect(url_for('index'))  # Redirect to the root page

    # Redirect back to the current folder after going up one level
    return render_template('index.html', current_path=get_parent_directory(current_path), items=list_files_and_folders(get_parent_directory(current_path)))

# Route to navigate into a folder
@app.route('/enter_folder/<folder_name>')
def enter_folder(folder_name):
    current_path = request.args.get('current_path', os.getcwd())
    new_path = os.path.join(current_path, folder_name)

    # Convert Windows path separator to Unix-like separator for the URL
    new_path_for_url = new_path.replace(os.sep, '/')

    return render_template('index.html', current_path=new_path_for_url, items=list_files_and_folders(new_path))


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4545)
