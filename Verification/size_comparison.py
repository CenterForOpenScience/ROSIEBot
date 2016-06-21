"""
STEP 2: Compare page sizes to a minimum acceptable size. Rejects move immediately to retry_scrape.py.
        Passing pages are sent to spot check to verify various fields are rendered.

Logging on this page:
    SIZE_CHECK [insufficient/sufficient + size]

"""

import os, sys
import Verification.initialize_list as initialize

mirror_path = initialize.mirror_path

success_log = open('Verification/Logs/test_success.log', 'a')
failure_log = open('Verification/Logs/test_failure.log', 'a')
send_to_retry = initialize.send_to_retry


# Super class for min_size comparison between bare minimum and actual files.
class SizeArbiter:
    """
    Initialize subclasses with type (e.g. `project/`), page (e.g. `files/`), acceptable minimum (e.g. 400, in KB).
    Minimum acceptable size is of a entirely-new fully-rendered page.
    """
    def __init__(self):
        self.files = []
        self.min_size = 0
        self.send_to_spot_check = []

    def compare(self):
        for file in self.files:
            file_size = os.path.getsize(file) / 1000  # in KB
            meets_expectations = file_size > self.min_size
            relative_name = file.replace(mirror_path, '')
            if meets_expectations:
                message = [relative_name, 'SIZE_CHECK', 'sufficient:', str(file_size), '\n']
                success_log.write('\t'.join(message))
                self.send_to_spot_check.append(file)
            else:
                message = [relative_name, 'SIZE_CHECK', 'insufficient:', str(file_size), '\n' ]
                failure_log.write('\t'.join(message))
                send_to_retry.append(file)
        return self.send_to_spot_check


# Project verification classes
# Min sizes are rough numbers based on template sizes

class ProjectDashboard(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 410
        self.files = initialize.get_files('project/')
        self.send_to_spot_check = self.compare()


class ProjectFiles(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('project/', 'files/')
        self.send_to_spot_check = self.compare()


class ProjectWiki(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 410
        self.files = initialize.get_files('project/', 'wiki/')
        self.send_to_spot_check = self.compare()


class ProjectAnalytics(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('project/', 'analytics/')
        self.send_to_spot_check = self.compare()


class ProjectRegistrations(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 390
        self.files = initialize.get_files('project/', 'registrations/')
        self.send_to_spot_check = self.compare()


class ProjectForks(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('project/', 'forks/')
        self.send_to_spot_check = self.compare()


# Registration verification classes


class RegistrationDashboard(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 410
        self.files = initialize.get_files('registrations/')
        self.send_to_spot_check = self.compare()


class RegistrationFiles(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('', 'files/')
        self.send_to_spot_check = self.compare()


class RegistrationWiki(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 410
        self.files = initialize.get_files('', 'wiki/')
        self.send_to_spot_check = self.compare()


class RegistrationAnalytics(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('', 'analytics/')
        self.send_to_spot_check = self.compare()


class RegistrationForks(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 380
        self.files = initialize.get_files('', 'forks/')
        self.send_to_spot_check = self.compare()


# User Verification Class

class UserProfile(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 80
        self.files = initialize.get_files('profile/')
        self.send_to_spot_check = self.compare()


# Institution Verification Class

class InstitutionProfile(SizeArbiter):
    def __init__(self):
        SizeArbiter.__init__(self)
        self.min_size = 350
        self.files = initialize.get_files('institutions/')
        self.send_to_spot_check = self.compare()
