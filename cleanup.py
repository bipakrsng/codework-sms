import shutil
import os

def remove_dirs(dirs):
    for d in dirs:
        for root, dirs_found, files in os.walk('.', topdown=True):
            for name in dirs_found:
                if name == d:
                    shutil.rmtree(os.path.join(root, name), ignore_errors=True)

remove_dirs(['__pycache__', '.pytest_cache', 'dist', 'build'])