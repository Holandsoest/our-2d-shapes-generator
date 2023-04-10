"""Grabs all `%NAME% (%NUMBER%).%EXTENSION%` files from subdirectories and merges the numbers in an output folder

Run this script inside the folder you want to sort."""
from progress.bar import ShadyBar
from enum import Enum
import shutil
import os

class MoveModes(Enum):
    MOVE = 0
    COPY = 1
    MOVE_ZIP = 2
    COPY_ZIP = 3
class KnownSolution:
    def __init__ (self, find_all:list, filename_output:str, start_iterator_at:int, absolute_directory:str)->None:
        """- `find_all` is a list of strings that all must be found in order to determine that it is the correct file
        - `filename_output` is a string that is the output. Note: supply a `#` for the number iterator."""
        self.find_all = find_all
        self.filename_output = filename_output
        self.iterator = start_iterator_at
        self.path = absolute_directory
    def give_filename(self)->str:
        """Returns the full filepath"""
        first, last = self.filename_output.split('#',1)
        self.iterator+=1
        return os.path.join(self.path, f'{first}{self.iterator-1}{last}')
class FancyBar(ShadyBar):
    message = 'Total progress'
    suffix = '[%(index)d/%(max)d]  -  %(percent).1f%%  -  %(eta_td)s remaining  -  %(elapsed_td)s elapsed'
    # suffix = '[%(index)d/%(max)d]\t%(percent)d%\t[%(eta_td)s remaining]\t[%(elapsed_td)s remaining]'

known_solutions = []
def get_new_filename(filename:str, default_dst:str)->str:
    """If unknown it prompts the user what to do with the filename"""
    for known_solution in known_solutions:
        found = True
        for find_str in known_solution.find_all:
            if filename.find(find_str) == -1:
                found = False
                break
        if not found: continue
        # We found it :)
        return known_solution.give_filename()
    # We did not find it :(
    find_all = []
    filename_output = ''

    user_entry = ''
    while True:
        user_entry = input(f'\nHello, found myself a file and i dont know what to do.\n\nThe filename is `{filename}`\nWhat should the name of this item be?\nPlease place a `#` where you want a number to appear.\nDont forget to also add the file_extension. `.txt` for example\nNew name: ')
        if (user_entry.find('#') == -1):
            print('ERROR: It must contain an `#`')
            continue
        filename_output = user_entry
        break
    print ('\nGreat\n')

    user_entry = ''
    while True:
        user_entry = input(f'\nCurrently the file must have all of the following in its filename for me to recognize it:\n{str(find_all)}\n\nWhat do you want to add?  (close by pressing enter on empty field)\nDont forget to also add the file_extension.\n')
        if (user_entry == f''): break
        find_all.append(user_entry)
    print('\nLast question (for this file format)\n')

    user_entry = ''
    while True:
        user_entry = input(f'\nShould it have its own directory?\nPath: {default_dst}/')
        if (user_entry == f''): break
    known_solutions.append(KnownSolution(find_all=find_all, filename_output=filename_output, start_iterator_at=1, absolute_directory=os.path.join(default_dst,user_entry)))
    print ('\nSaved, Thank you.')

    return get_new_filename(filename, default_dst)
def count_items_in_folder(absolute_path:str)->tuple[int,int]:
    files = 0
    folders = 0
    for name in os.listdir(absolute_path):
        if not os.path.isdir(os.path.join(absolute_path, name)): # Its a file
            files += 1
            continue
        # Its a folder
        output = count_items_in_folder(os.path.join(absolute_path, name))
        files+=output[0]
        folders+=output[1]
        folders += 1
    return (files, folders)
def move_files(mode:MoveModes, absolute_source:str, absolute_destination:str, progress_bar:FancyBar)->None:
    for name in os.listdir(absolute_source):
        if os.path.isdir(os.path.join(absolute_source, name)): # Its a folder
            if os.path.join(absolute_source, name) == absolute_destination: continue # Skip our output folder
            move_files(mode, 
                       os.path.join(absolute_source, name),
                       absolute_destination, progress_bar)
            continue
        
        # Its a file
        src = os.path.join(absolute_source, name)
        dst = os.path.join(get_new_filename(name, absolute_destination))
        dst_folder = os.path.dirname(dst)
        if not os.path.exists(dst_folder): os.makedirs(dst_folder)
        if mode == MoveModes.MOVE or mode == MoveModes.MOVE_ZIP:
            os.rename(src,dst)
        else:
            shutil.copy2(src,dst)

        # Update progression
        try: progress_bar.next()
        except: pass
def sort(dir:str, mode:MoveModes)->None:

    # Update progress bar
    total_files = 0
    total_folders = 0
    total_files, total_folders = count_items_in_folder(dir)
    if mode == MoveModes.MOVE_ZIP or mode == MoveModes.MOVE: title = f'Moving files\t'
    else: title = f'Copying files\t'
    progress_bar = FancyBar(title, max=total_files)
    progress_bar.start()

    # Move the files
    move_files(mode, 
               absolute_source=     dir,
               absolute_destination=os.path.join(dir, 'output'),
               progress_bar=progress_bar)
    progress_bar.finish()

    # Zip the files
    if mode == MoveModes.MOVE_ZIP or mode == MoveModes.COPY_ZIP:
        progress_bar = FancyBar(f'Creating .zip\t', max=1)
        progress_bar.start()
        shutil.make_archive('output','zip',
                            dir,
                            os.path.join(dir, 'output'),
                            verbose=True)
        progress_bar.next()
        progress_bar.finish()
if __name__ == '__main__':
    dir = os.path.join(os.getcwd(),'files','shape_generator','2000x2000')
    known_solutions.append(KnownSolution(['img','.txt'],'img #.txt', start_iterator_at=1, absolute_directory=os.path.join(dir, 'output', 'annotations')))
    known_solutions.append(KnownSolution(['img','.jpg'],'img #.jpg', start_iterator_at=1, absolute_directory=os.path.join(dir, 'output', 'images')))
    sort(dir ,mode=MoveModes.COPY_ZIP)
        
    
