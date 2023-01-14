import gdown

ALLOWED_EXTENSIONS = (['wav','csv','mp3'])

def drive_download(url, output):
    gdown.download(url, output, quiet=False)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS