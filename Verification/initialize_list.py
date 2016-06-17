"""
STEP 1: Get list of specified pages in mirror, compare to task list from the crawler.
        Check that directory format is correct and fully in place leading up to the file.

Logging on this page:
    FIND_TYPE [not_found]
    FIND_INSTANCES [missing]
    FIND_FOLDER [not_found]
    FIND_FILE [not_found]

"""
import sys, os
import settings

absolute_python_root = sys.path[1]                                              #   Absolute root of this project
relative_mirror_root = settings.base_urls[0].split('//', 1)[1].strip('//')      # + Folder name of the mirror
mirror_path = absolute_python_root + '/' + relative_mirror_root + '/'           # = Absolute path to the mirror

success_log = open('Logs/test_success.log', 'a')
failure_log = open('Logs/test_failure.log', 'a')

send_to_retry = []

# FOR DEVELOPMENT ONLY -  a fake task list - needs to be reworked with absolute paths
expected = ['2c9ke', '2kfya', '2sq3u', '357k9', '3749s', '3btvx', '3czhs', '3gft7', '3k5xm', '42bkp', '43qsy', '45r3y', '4embk', '4vyhn', '58tje', '5d8zc', '5hrxg', '5qvm3', '6gm2d', '6rnt5', '8jap9', '8jrev', '8namr', '8vj59', '95aqp', '9bc6m', '9hzqf', '9njhs', '9nwxv', 'a9rpt', 'abfnx', 'aqdx2', 'aqtvs', 'b3x7m', 'b53ku', 'bf6k4', 'bnztq', 'bqadg', 'bt5ve', 'c5gzw', 'cqsu6', 'crnmj', 'cu6fk', 'd67se', 'd9bq6', 'dfe4c', 'eds2x', 'erp3j', 'et72m', 'eud2q', 'eyrn3', 'gw8td', 'htuzg', 'jast6', 'jfe94', 'jpr9x', 'jt4hc', 'k4b5v', 'k7tyf', 'kgq73', 'kscwm', 'kvj75', 'm26ej', 'm4z6g', 'mfn6r', 'mj8t5', 'nrh98', 'r96e5', 'rh6fb', 'rzskd', 's6ydj', 's8cvd', 'sjqau', 'smz65', 'snrwd', 'tdehc', 'tncp9', 'tneqa', 'ut7zx', 'v37gz', 'wjvqg', 'wsyhb', 'wx3c8', 'wz2uv', 'xcbzk', 'xvrwj', 'y9ckz', 'yd3kr', 'ywjk5', 'zb74t', 'znpd5']
# TODO: READ FROM TASKS FILE
def read_crawler_tasks():
    pass


# Finds missing task file elements
def ensure_all_instances(expected_list, instance_list, type):
    for instance in expected_list:
        if instance in instance_list:
            continue
        else:
            message = ['FIND_INSTANCES', type + instance, 'not_found', '\n']
            failure_log.write('\t'.join(message))
            send_to_retry.append(instance)


# Get absolute paths to the specific page for a type of resource.
def get_files(osf_type, page=''):
    """
    Parameter osf_type should be `project/`, `profile/`, `institution/` or `` for registrations.
    Page should be `` for dashboard or the name of folder within a osf_type instance,
        ex. 'files/' for the file page of a node.

    """
    file_paths = []
    type_folder = mirror_path + osf_type                        # `localhost:70/project`

    if not os.path.exists(type_folder):                         # No /project folder
        print(type_folder)
        message = ['FIND_TYPE', osf_type, 'not_found', '\n']
        failure_log.write('\t'.join(message))
        send_to_retry.append(type_folder)
        return file_paths

    type_instances = os.listdir(type_folder)                    # GUID folders within the project folder
    ensure_all_instances(expected, type_instances, osf_type)    # Did we forget to download any type instances?

    for instance in type_instances:                             # A folder for a specific project, user, etc.
        instance_path = type_folder + instance + '/' + page     # `localhost:70/project/GUID/files`

        if not os.path.isdir(instance_path):           # `Files` folder not found.
            message = ['FIND_FOLDER', osf_type + instance + '/' + page, 'not_found', '\n']
            failure_log.write('\t'.join(message))
            send_to_retry.append(instance_path)
            continue

        fname = instance_path + 'index.html'                    # Finally! The path to the file we want.
        if os.path.exists(fname):
            file_paths.append(fname)
        else:
            message = ['FIND_FILE', osf_type + instance + '/' + page, 'not_found', '\n']
            failure_log.write('\t'.join(message))
            send_to_retry.append(fname)
    return file_paths
