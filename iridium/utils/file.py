import os


def make_dirs_path_no_exist(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as err:
            raise err
