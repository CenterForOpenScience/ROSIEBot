"""
STEP 1: Compare page sizes to a minimum acceptable size. Rejects move immediately to retry_scrape.py.
        Passing pages are sent to spot check to verify various fields are rendered.

Classes organized by type ('projects', 'users', etc.)

Pages:

- Dashboard (project and registration)
- Files (project and registration)
- Wiki (project and registration)
- FORGONE: Analytics (project and registration) (These pages often look a mess anyway and rarely prerender)
- Forks (project and registration)
- Registrations

- Profile (user and institution)

"""

import os, shutil, sys
import settings

absolute_python_root = sys.path[1]                                              #   Absolute root of this project
relative_mirror_root = settings.base_urls[0].split('//', 1)[1].strip('//')      # + Folder name of the mirror
mirror_path = absolute_python_root + '/' + relative_mirror_root + '/'           # = Absolute path to the mirror

success_log = open('Logs/success.log', 'a')
failure_log = open('Logs/failure.log', 'a')


# Get absolute paths to the specific page for a type of resource.
def get_files(osf_type, page=''):
    """
    OSF_type should be `project/`, `profile/`, `institution/` or `` for registrations.
    Page should be `` for dashboard or the name of folder within a osf_type instance,
        ex. 'files/' for the file page of a node.

    get_files('project/', 'files/') gets every node's files page.
    """
    file_paths = []
    type_folder = mirror_path + osf_type                        # `localhost:70/project`

    if not os.path.exists(type_folder):                         # No /project folder
        message = ['FIND_TYPE', osf_type, 'NOT FOUND', '\n']
        failure_log.write('\t'.join(message))
        return file_paths

    type_instances = os.listdir(type_folder)                    # GUID folders within the project folder

    for instance in type_instances:                             # A folder for a specific project, user, etc.
        instance_path = type_folder + instance + '/' + page     # `localhost:70/project/GUID/files`

        if not os.path.isdir(type_folder + instance):           # Leave non-folders alone.
            continue
        if not os.path.isdir(instance_path):                    # Folder may not even be project.
            message = ['FIND_FOLDER', osf_type + instance + '/' + page, 'NOT FOUND', '\n']
            failure_log.write('\t'.join(message))
            continue

        fname = instance_path + 'index.html'                    # Finally! The path to the file we want.
        if os.path.exists(fname):
            file_paths.append(fname)
        else:
            message = ['FIND_FILE', osf_type + instance + '/' + page, 'NOT FOUND', '\n']
            failure_log.write('\t'.join(message))
    return file_paths


# Super class for min_size comparison between bare minimum and actual files.
class SizeArbiter:
    """
    Initialize subclasses with type (e.g. `project/`), page (e.g. `files/`), acceptable minimum (e.g. 400, in KB).
    Minimum acceptable size is of a entirely-new fully-rendered page.
    """
    def __init__(self):
        self.files = []
        self.min_size = 0

    def compare(self):
        for file in self.files:
            file_size = os.path.getsize(file) / 1000  # in KB
            print(file, file_size > self.min_size)


# Project verification classes

class ProjectDashboard(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



class ProjectFiles(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



class ProjectWiki(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)


# class ProjectAnalytics(SizeArbiter):
    # def __init__(self):
    #     SizeArbiter.__init__(self)


class ProjectForks(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



class ProjectRegistrations(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



# Registration verification classes


class RegistrationDashboard(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



class RegistrationFiles(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



class RegistrationWiki(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



# class RegistrationAnalytics(SizeArbiter):
    # def __init__(self):
    #     SizeArbiter.__init__(self)



class RegistrationForks(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)


# User Verification Class


class UserProfile(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)


# Institution Verification Class


class InstitutionProfile(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)



# success_log.close()
# failure_log.close()