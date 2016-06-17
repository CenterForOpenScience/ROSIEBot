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
expected = ['project/2c9ke', 'project/2kfya', 'project/2sq3u', 'project/357k9', 'project/3749s', 'project/3btvx', 'project/3czhs', 'project/3gft7', 'project/3k5xm', 'project/42bkp', 'project/43qsy', 'project/45r3y', 'project/4embk', 'project/4vyhn', 'project/58tje', 'project/5d8zc', 'project/5hrxg', 'project/5qvm3', 'project/6gm2d', 'project/6rnt5', 'project/8jap9', 'project/8jrev', 'project/8namr', 'project/8vj59', 'project/95aqp', 'project/9bc6m', 'project/9hzqf', 'project/9njhs', 'project/9nwxv', 'project/a9rpt', 'project/abfnx', 'project/aqdx2', 'project/aqtvs', 'project/b3x7m', 'project/b53ku', 'project/bf6k4', 'project/bnztq', 'project/bqadg', 'project/bt5ve', 'project/c5gzw', 'project/cqsu6', 'project/crnmj', 'project/cu6fk', 'project/d67se', 'project/d9bq6', 'project/dfe4c', 'project/eds2x', 'project/erp3j', 'project/et72m', 'project/eud2q', 'project/eyrn3', 'project/gw8td', 'project/htuzg', 'project/jast6', 'project/jfe94', 'project/jpr9x', 'project/jt4hc', 'project/k4b5v', 'project/k7tyf', 'project/kgq73', 'project/kscwm', 'project/kvj75', 'project/m26ej', 'project/m4z6g', 'project/mfn6r', 'project/mj8t5', 'project/nrh98', 'project/r96e5', 'project/rh6fb', 'project/rzskd', 'project/s6ydj', 'project/s8cvd', 'project/sjqau', 'project/smz65', 'project/snrwd', 'project/tdehc', 'project/tncp9', 'project/tneqa', 'project/ut7zx', 'project/v37gz', 'project/wjvqg', 'project/wsyhb', 'project/wx3c8', 'project/wz2uv', 'project/xcbzk', 'project/xvrwj', 'project/y9ckz', 'project/yd3kr', 'project/ywjk5', 'project/zb74t', 'project/znpd5']
# TODO: READ FROM TASKS FILE
def read_crawler_tasks():
    pass


# Finds missing task file elements
def ensure_all_instances(expected_list, instance_list, type):
    for element in expected_list:
        if element.replace(type, '') in instance_list:
            continue
        else:
            message = ['FIND_INSTANCES', element, 'not_found', '\n']
            failure_log.write('\t'.join(message))
            send_to_retry.append(element)


# Get absolute paths to the specific page for a type of resource.
def get_files(osf_type, page=''):
    """
    Parameter osf_type should be `project/`, `profile/`, `institution/` or `` for registrations.
    Page should be `` for dashboard or the name of folder within a osf_type instance,
        ex. 'files/' for the file page of a node.

    """
    print("Getting files for", osf_type + page)
    file_paths = []
    type_folder = mirror_path + osf_type                        # `localhost:70/project`

    if not os.path.exists(type_folder):                         # No /project folder
        message = ['FIND_TYPE', osf_type, 'not_found', '\n']
        failure_log.write('\t'.join(message))
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
