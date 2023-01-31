import os
#to work with json files
import json
#sh util copy and overwrite operations
import shutil
#allow us to run any terminal command
from subprocess import PIPE, run
#to get access to command line arguments
import sys


GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]


def find_all_game_paths(source):
    game_paths = []

    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)

        break

    return game_paths


def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)

    return new_names


def create_dir(path):
    #if the path doesn't exist already we make a new path
    if not os.path.exists(path):
        os.mkdir(path)


def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)


def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)


def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    os.chdir(cwd)

def main(source, target):
    #os.getcwd() gets the current working directory
    cwd = os.getcwd()
    print ("printing out the cwd", cwd)
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source_path)
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    create_dir(target_path)

    #information on zip function
    """
    >>> a = [1, 2, 3]
    >>> b = [10, 20, 30]
    >>> result = list(zip(a, b))
    >>> print(result)
    [(1, 10), (2, 20), (3, 30)]
    """

    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


#name is a special variable in python it is automatically defined and has a default value of '__main__' when python file is executed.
#like in c++ main
if __name__ == "__main__":
    #sys.argv takes in our arguments from command line and saved in args
    #example python get_game_data.py data new_data would return if we print ['get_game_date.py', 'data', 'new_data']
    args = sys.argv
    print (args)
    if len(args) != 3:
        raise Exception("You must pass a source and target directory - only.")

    #source = the first argument
    #target = the second argument
    #extra a 
    source, target = args[1:]
    main(source, target)
