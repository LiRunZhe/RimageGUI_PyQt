import os
import sys

def find_rimage():
    """
    Finds the rimage.exe executable.
    Checks the current directory and then the system's PATH.
    """
    # Check current directory first
    current_dir = os.path.dirname(sys.argv[0])
    rimage_path_local = os.path.join(current_dir, "rimage.exe")
    if os.path.exists(rimage_path_local):
        return rimage_path_local

    # Check PATH
    rimage_path_in_path = None
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        rimage_path_candidate = os.path.join(path_dir, "rimage.exe")
        if os.path.exists(rimage_path_candidate):
            rimage_path_in_path = rimage_path_candidate
            break # Found it, no need to check further

    return rimage_path_in_path
