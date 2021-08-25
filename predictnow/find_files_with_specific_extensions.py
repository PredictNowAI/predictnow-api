import os


def find_files_with_specific_extensions(path: str, extension: str = ""):
    extension = extension if not extension or extension.startswith(".") else "." + extension
    list_of_file_paths = list()
    list_of_files_and_folders = [os.path.join(path, i) for i in os.listdir(path)]

    for i in list_of_files_and_folders:
        if os.path.isdir(i):
            list_of_file_paths += find_files_with_specific_extensions(i, extension)
        elif i.endswith(extension):
            list_of_file_paths.append(i)

    return list_of_file_paths
