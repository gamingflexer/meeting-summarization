import gdown

def drive_download(url, output):
    gdown.download(url, output, quiet=False)