import shutil
import os
import codecs
import json
ROOTDIR = 'archive/'


class Node:
    def __init__(self, filename, guid):
        self.folder_path = self.get_path_from_guid(filename, guid)
        self.pathFound = True

    def get_path_from_guid(self, filename, guid):
        path = ROOTDIR + filename + guid
        return path


class Deletion:
    def __init__(self, active_nodes):
        self.active_nodes_list = active_nodes

    def generate_archive_list(self, filename):
        subdirs_list = []
        for x in os.walk(ROOTDIR+filename).next()[1]:
            subdirs_list.append(x)

        return subdirs_list

    def generate_nodes_list(self, filename, archive_list):
        nodes_list = []

        for subdir in archive_list:
            print("Checking this subdir ", subdir)
            if subdir not in self.active_nodes_list:
                node = Node(filename, subdir)
                nodes_list.append(node)
                print("Appending ", subdir, " to nodes_list")
                archive_list.remove(subdir)

        # self.active_nodes_list.sort()
        # for subdir in os.walk(ROOTDIR):
        #     sub = str(subdir)
        #     directory = "/"+sub+"/"
        #     path = str(os.path.abspath(directory))
        #     print("on subdir", path)
        #     if subdir not in self.active_nodes_list:
        #         print("Deleting the path: ", path)
        #         print("*********")
        #         print("*********")
        #         print("*********")
        #         shutil.rmtree(os.path.abspath(directory))
        #
        #     for guid in self.previously_active_nodes:
        #         print("Checking this guid: ", guid)
        #         if guid not in self.currently_active_nodes:
        #             node = Node(guid)
        #             nodes_list.append(node)
        #             print("Appending ", guid, " to nodes_list")
        #             self.previously_active_nodes.remove(guid)
        return nodes_list

    def delete_node(self, node):
        if os.path.exists(node.folder_path):
            print("Deleting", node.folder_path)
            shutil.rmtree(node.folder_path)
        else:
            node.pathFound = False
            print(node.folder_path, " Not Found")


def run_deleter(initial_list, filename):
    print("inside run_deleter")
    macc = Deletion(initial_list)
    print("Created macc")
    archive_list = macc.generate_archive_list(filename)
    nodes_list = macc.generate_nodes_list(filename, archive_list)
    for node in nodes_list:
        macc.delete_node(node)


def main(json_filename):
    with codecs.open(json_filename, mode='r', encoding='utf-8') as file:
        current_task_file = json.load(file)
    run_deleter(current_task_file['list_of_active_registrations'], 'registration/')
    run_deleter(current_task_file['list_of_active_users'], 'profile/')
    run_deleter(current_task_file['list_of_active_nodes'], 'project/')

if __name__ == '__main__':
    main('list1.json')
