import mimetypes
import os


# analyze all the MIME types in the resources file folder
def analyze(folder_path):
    files = os.listdir(folder_path)
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isdir(file_path):
            analyze(file_path)
            continue
        mime_type = mimetypes.guess_type(file_path)
        print(file_path, mime_type[0])


if __name__ == '__main__':
    analyze('resources')
