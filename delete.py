import os
import random

dir_path = os.getcwd() + '\\pictures\\'  # Replace with your directory path

# Get a list of all files in the directory
all_files = os.listdir(dir_path)

# Choose 40 random files from the list
random_files = random.sample(all_files, 40)

# Delete each of the randomly selected files
for file in random_files:
    file_path = os.path.join(dir_path, file)
    os.remove(file_path)
