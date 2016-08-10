import shutil
import os
import codecs
import json

MIRROR = 'archive'


class Deleter:
    def __init__(self, json_filename):
        with codecs.open(json_filename, mode='r', encoding='utf-8') as file:
            active_lists = json.load(file)
            self.active_node_guids = active_lists["list_of_active_nodes"]
            self.active_registration_guids = active_lists["list_of_active_registrations"]
            self.active_user_guids = active_lists["list_of_active_users"]

    def compare_to_mirror(self, osf_type, active_list):

        mirror_list = os.listdir(MIRROR + '/' + osf_type)
        print("OSF type: " + osf_type)

        for subdir in mirror_list:
            print("Checking", subdir)
            if subdir not in active_list:
                print(subdir, "inactive. Deleting")
                subdir_path = '/'.join([MIRROR, osf_type, subdir])
                self.delete_directory(subdir_path)

    def delete_directory(self, directory_path):
        print(directory_path)
        if os.path.isdir(directory_path):
            shutil.rmtree(directory_path)
            print("Deleted", directory_path)

    def run(self):
        self.compare_to_mirror('project', self.active_node_guids)
        self.compare_to_mirror('registration', self.active_registration_guids)
        self.compare_to_mirror('profile', self.active_user_guids)
