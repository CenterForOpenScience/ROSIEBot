# Validation Testing and Retry Suite


## Execution
run.py (through IDE or CLI)

OPTIONS
- Identify trouble (see PROCESS below)
- Identify and correct trouble (see STEP 4 below)


## Terminology

Most to least specific:

| Term              |                                                                   |
|-------------------|-------------------------------------------------------------------|
| Type              | An area on the OSF (see below)				                    |
| Type Instance     | A specific member of that type (e.g. the Reproducibility Project) |
| Page              | One of the pages associated with a type (see below)               |
| File              | A page instance                                                   |

-----

##### Types

- Project
- Registration
- User
- Institution

##### Pages for each type

| Project       | Registration | User    | Institution |
|---------------|--------------|---------|-------------|
|Dashboard      | Dashboard    | Profile | Profile     |
| Files         | Files        |
| Wiki          | Wiki         |
| Analytics     | Analytics    |
| Registrations |              |
| Forks         | Forks        |

For projects and registration types, the catchy acronym `FWARF` (Files, wiki, analytics, registrations, forks) lists the correct page order.


## Validation Process

Any negative test result will act to retry scrape for files within the result's scope.

### STEP 1:     initialize_list.py

ACTIONS
- Check that there is a subdirectory for a type.
- Check for all type instances given in the crawler's task file are present.
- Check that an instance's page file and directory, if not the dashboard page, are present.

OUPUT
- List of the pages for each instance

LOGS
- `FIND_TYPE [not_found]`
- `FIND_INSTANCES [instance_missing]`
- `FIND_FOLDER [not_found]`
- `FIND_FILE [not_found]`


### STEP 2:     size_comparison.py

INPUT
- All files in the step 1 output.

ACTIONS
- Compare each page instance to the size of a blank but fully-prerendered page instance to see if it is non-fully prerendered.

OUPUT
- Additions to the retry list (failed to meet minimum size)
- List of files to spot check (meets minimum size)

LOGS
- `SIZE_CHECK [insufficient/sufficient + size]`

### STEP 3:     spot_check.py

ACTIONS
- Check for the presence and non-emptiness of several important components of a page (such as title!).

OUTPUT
- Additions to the retry list (elements in a file are missing)

LOGS
- `SPOT_CHECK [not_found/empty/ok]`

### STEP 4:     retry_scrape.py

ACTIONS
- Reissue asynchronous get requests for specified files.
- Tries a set number of times before giving up on a file.

LOGS
- `TODO`

## CLI
- Not ready, but it will be.
- TODO


## Notes

- This suite is modular to every type/page possibility.
- reset_logs.py is a friend for testing/general housekeeping.
- Basically everything needs to be refactored for Ember remodels (HTML templates and elements to spot check)
- Analytics spot-checking is on hold due to the inability to scrape the page in the first place (HTTP 504).