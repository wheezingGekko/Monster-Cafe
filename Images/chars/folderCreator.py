import os
import re

from pathlib import Path
  
if __name__ == '__main__':
    for file in os.listdir():

        if path(file).is_dir():
            continue

        b = re.search('^(([a-z0-9])*_([a-z0-9])*)', file)

        if b is None:
            continue

        temp = b[0]

        if temp.endswith('_idle'):
            temp = temp[:-5]
        if temp.endswith('_run'):
            temp = temp[:-4]

        if not (Path(temp)).is_dir():
            os.mkdir(temp)
        
        os.rename(file, temp + "/" + file)