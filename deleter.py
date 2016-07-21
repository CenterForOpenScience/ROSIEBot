# import statements should be here
import shutil
# import codecs
# import json


class Node:
    def __init__(self, guid):
        self.folder_path = self.get_path_from_guid(guid)
        self.pathFound = True

    def get_path_from_guid(self, guid):
        path = 'archive/' + guid
        return path


class Deletion:
    def __init__(self, initial_list, subsequent_list):
        self.previously_active_nodes = initial_list
        self.currently_active_nodes = subsequent_list

    def generate_nodes_list(self):
        nodes_list = []
        self.previously_active_nodes.sort()
        for guid in self.previously_active_nodes:
            print("Checking this guid: ", guid)
            if guid not in self.currently_active_nodes:
                node = Node(guid)
                nodes_list.append(node)
                print("Appending ", guid, " to nodes_list")
                self.previously_active_nodes.remove(guid)
        return nodes_list

    def delete_node(self, node):
        print("Deleting", node.folder_path)
        if os.path.exists(node.folder_path):
            shutil.rmtree(node.folder_path)
        else:
            node.pathFound = False
            print(node.folder_path, " Not Found")


def run_deleter(initial_list, subsequent_list):
    print("inside run_deleter")
    macc = Deletion(initial_list, subsequent_list)
    print("Created macc")
    nodes_list = macc.generate_nodes_list()
    for node in nodes_list:
        macc.delete_node(node)


# def main(json1, json2):
#     with codecs.open(json1, mode='r', encoding='utf-8') as previous_tf:
#         previous_task_file = json.load(previous_tf)
#     with codecs.open(json2, mode='r', encoding='utf-8') as current_tf:
#         current_task_file = json.load(current_tf)
#     run_deleter(previous_task_file['list_of_active_registrations'], current_task_file['list_of_active_registrations'])
#     run_deleter(previous_task_file['list_of_active_users'], current_task_file['list_of_active_users'])
#     run_deleter(previous_task_file['list_of_active_nodes'], current_task_file['list_of_active_nodes'])
#
# if __name__ == '__main__':
#     main("list1.json", "list2.json")
