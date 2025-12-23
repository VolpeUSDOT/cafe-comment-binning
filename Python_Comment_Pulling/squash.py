import os
import shutil

# Squashed download.py output into single folder, with file names prefixed by their containing folder + "___"

BASE_DIR = "C://Users//Vincent.Livant//Documents//GitHub//cafe-comment-binning//temp/"

if __name__ == "__main__":
    # Get list of all directories for download.py comment outputs.
    dir_list = os.listdir(BASE_DIR)

    if "squashed" in dir_list:
        dir_list.remove("squashed")

    # Make new squashed directory if it doesn't exist.
    squashed_dir = BASE_DIR + "squashed/"
    if not os.path.isdir(squashed_dir):
        os.mkdir(squashed_dir)
    
    # Copy all files into squashed directory
    for directory in dir_list:
        full_path = BASE_DIR + directory
        if os.path.isdir(full_path):
            for file in os.listdir(full_path):
                source_path = full_path + '/' + file
                desitination_path = squashed_dir + directory + '___' + file
                shutil.copy(source_path, desitination_path)