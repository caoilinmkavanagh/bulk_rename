from flask import Flask, render_template, request, redirect, url_for, flash
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'jpg', 'jpeg', 'png'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB
app.secret_key = 'your_secret_key'  # Needed for flashing messages

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def secure_filename(filename):
    return filename.replace(' ', '_').lower()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        new_name = request.form.get('new_name')
        
        if not new_name:
            flash('New name is required!')
            return redirect(request.url)
        
        # Track the number of successfully renamed files
        success_count = 0
        failure_count = 0
        
        for i, file in enumerate(files):
            if file and allowed_file(file.filename):
                # File size check
                if len(file.read()) > app.config['MAX_CONTENT_LENGTH']:
                    flash(f"File {file.filename} is too large (max size is 10 MB).")
                    failure_count += 1
                    continue

                # Reset file pointer
                file.seek(0)
                
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"{new_name}_{i+1}.{file_ext}"
                
                try:
                    # Save the file first
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    print(f"File saved as: {file_path}")

                    # Rename the file
                    new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                    os.rename(file_path, new_file_path)
                    print(f"File renamed to: {new_file_path}")
                    
                    success_count += 1
                except Exception as e:
                    print(f"Error renaming file {filename}: {e}")
                    flash(f"Error renaming file {filename}.")
                    failure_count += 1

        if success_count > 0:
            flash(f'Successfully renamed {success_count} files.')
        if failure_count > 0:
            flash(f'Failed to rename {failure_count} files.')

        return redirect(url_for('index'))
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
