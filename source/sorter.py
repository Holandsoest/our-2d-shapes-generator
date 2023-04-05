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
    def __init__ (self, find_all:list, filename_output:str, start_iterator_at:int)->None:
        """- `find_all` is a list of strings that all must be found in order to determine that it is the correct file
        - `filename_output` is a string that is the output. Note: supply a `#` for the number iterator."""
        self.find_all = find_all
        self.filename_output = filename_output
        self.iterator = start_iterator_at
    def give_filename(self)->str:
        first, last = self.filename_output.split('#',1)
        self.iterator+=1
        return f'{first}{self.iterator-1}{last}'
class FancyBar(ShadyBar):
    message = 'Total progress'
    suffix = '[%(index)d/%(max)d]  -  %(percent).1f%%  -  %(eta_td)s remaining  -  %(elapsed_td)s elapsed'
    # suffix = '[%(index)d/%(max)d]\t%(percent)d%\t[%(eta_td)s remaining]\t[%(elapsed_td)s remaining]'

known_solutions = []
def get_new_filename(filename:str)->str:
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
        user_entry = input(f'How should i recognize these files?\n\nCurrently the file must have all of the following in its filename for me to recognize it:\n{str(find_all)}\n\nWhat do you want to add?  (close by typing `%EXIT%`)\nDont forget to also add the file_extension.\n')
        if (user_entry == f'%EXIT%'): break
        find_all.append(user_entry)
    known_solutions.append(KnownSolution(find_all=find_all, filename_output=filename_output, start_iterator_at=1))
    print ('\nSaved, Thank you.')

    return get_new_filename(filename)
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
def move_files(mode:MoveModes, absolute_source:str, absolute_destination:str)->None:
    for name in os.listdir(absolute_source):
        if os.path.isdir(os.path.join(absolute_source, name)): # Its a folder
            if os.path.join(absolute_source, name) == absolute_destination: continue # Skip our output folder
            move_files(mode, 
                       os.path.join(absolute_source, name),
                       absolute_destination)
            continue
        
        # Its a file
        src = os.path.join(absolute_source, name)
        dst = os.path.join(absolute_destination, get_new_filename(name))
        if mode == MoveModes.MOVE or mode == MoveModes.MOVE_ZIP:
            os.rename(src,dst)
        else:
            shutil.copy2(src,dst)

        # Update progression
        try: progress_bar.next()
        except: pass
def sort(dir:str, mode:MoveModes)->None:
    total_files = 0
    total_folders = 0
    total_files, total_folders = count_items_in_folder(dir)
    progress_bar = FancyBar(f'{mode.name.lower()}ing files', max=total_files)
    progress_bar.start()

    if not os.path.exists(os.path.join(dir, 'output')): os.makedirs(os.path.join(dir, 'output'))

    file_counter = 0
    move_files(mode, 
               absolute_source=     dir,
               absolute_destination=os.path.join(dir, 'output'))
    progress_bar.finish()
    if mode == MoveModes.MOVE_ZIP or mode == MoveModes.COPY_ZIP:
        progress_bar = FancyBar(f'Creating .zip', max=1)
        progress_bar.start()
        shutil.make_archive('output','zip',
                            dir,
                            os.path.join(dir, 'output'),
                            verbose=True)
        progress_bar.next()
        progress_bar.finish()
if __name__ == '__main__':
    sort(dir=os.getcwd() ,mode=MoveModes.COPY_ZIP)
        
    
