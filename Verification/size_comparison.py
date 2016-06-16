"""
STEP 1: Get all the created pages and see if they're a lot larger than their templates.
If not, move on to retry_scrape.py
"""
# TODO: How much larger?

import os, shutil, sys
import settings

absolute_python_root = sys.path[1]                                              #   Absolute root of this project
relative_mirror_root = settings.base_urls[0].split('//', 1)[1].strip('//')      # + Folder name of the mirror
mirror_path = absolute_python_root + '/' + relative_mirror_root + '/'           # = Absolute path to the mirror

success_log = open('Logs/success.log', 'a')
failure_log = open('Logs/failure.log', 'a')


# Get absolute paths to the specific page for a type of resource.
def get_files(type, page=''):
    """
    Type should be `project/`, `profile/`, `institution/` or `/` for registrations.
    Page should be `` for dashboard or the name of folder within a type instance,
        ex. 'files' for the file page of a node.

    get_files('project', 'files') gets every node's files page.
    """
    files = []
    type_folder = mirror_path + type
    type_instances = os.listdir(type_folder)
    for instance in type_instances:
        instance_path = type_folder + instance + '/' + page
        fname = instance_path + 'index.html'        # Finally! The name of the folder we want.
        if os.path.isdir(instance_path):
            files.append(fname)
    return files


# Compare node page sizes to their respective templates
class NodeDashboard:
    def __init__(self):
        self.template_size = 00
        self.files = {}      #   self.urls['filename'] = int:file_size

    def get_pages_of_type(self):
        # add to URLs, get size
        host = (os.getcwd())
        file = ''
        self.files[file] = os.path.getsize(file)
        pass

    def get_page_size(self):
        for file in self.files:
            page_size = self.files[file]
            if page_size < self.template_size + 00:     #   Margin based on reasonable amount of specific content
                success_log.write('Size check: ' + file + ', Dashboard' + ', PageSizeSuccess:' + str(page_size) + '/' + str(self.template_size))
            else:
                success_log.write('Size check: ' + file + ', Dashboard' + ', PageSizeFailure:' + str(page_size) + '/' + str(self.template_size) + ' , Sending to spot_check.' )
                send_to_spot_check(file, 'node_dashboard')


# class NodeFilesPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class NodeWikiPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class NodeAnalyticsPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class NodeRegistrationsPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class NodeForksPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# # Compare registration page sizes to their respective templates
# class RegistrationDashboardPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class RegistrationFilesPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class RegistrationWikiPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class RegistrationAnalyticsPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class RegistrationForksPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# # Compare user and institution page sizes to their respective templates
# class UserProfilePageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# class InstitutionProfilePageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')
#
#
# # Compare index page size to its template
# class IndexPageSize:
#     def __init__(self):
#         self.template_size = 00
#
#
#     def get_page_size(self, url):
#         self.page_size = 00
#         if self.page_size < self.template_size + 00:
#             send_to_spot_check(self.url, 'type')


# def send_to_spot_check(page, type):
#     pass
#
# node_dashboard = NodeDashboard()
# node_dashboard.get_pages_of_type()

success_log.close()
failure_log.close()