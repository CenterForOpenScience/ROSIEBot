# ROSIEBot
# The Robotic Open Science Indexing Engine


![rosie alt](https://cloud.githubusercontent.com/assets/15851093/16431535/109ac052-3d4f-11e6-9218-e7a457898492.png '"Eight legged wonder: 
Crawling, enduring, facing,
Despite childish fears!"  - Unknown')


##### Static mirroring utility for the [Open Science Framework](osf.io), maintained by the [Center for Open Science](cos.io).
  Visit the [COS Github](https://github.com/CenterForOpenScience/) for more innovations in the *openness*, *integrity*, and *reproducibility* of scientific research.

# [Project Overview](project_overview.md)

## Installation

This software requires Python 3.5 for the aiohttp library. If desired, create a virtualenv:

##### From scratch:

`pip install virtualenv`

`pip install virtualenvwrapper`

##### Create virtualenv 'rosie':

`mkvirtualenv rosie --python=python3.5`

##### Switch into the rosie environment for the first time: 
`workon rosie`

##### Clone the repository into your development folder:
`git clone https://github.com/zamattiac/ROSIEBOt.git`

Navigate into the new folder ( `cd ROSIEBot` )

`pip install -r requirements.txt` to install dependency libraries in the virtualenv.

##### Enter/exit the virtual environment:

`workon rosie`/`deactivate`


## ROSIEisms

##### OSF Pages by Category

| Project       | Registration | User    | Institution |
|---------------|--------------|---------|-------------|
|Dashboard      | Dashboard    | Profile | Dashboard   |
| Files         | Files        |
| Wiki          | Wiki         |
| Analytics     | Analytics    |
| Registrations |              |
| Forks         | Forks        |



##### Our Process
- Crawling: getting lists of all the URLs to visit
- Scraping: visiting all those URLs and saving their content to the mirror
- Resuming: continuing the crawl/scrape process if it stops in the middle
- Verifying: making sure all the files are present and in acceptable condition
- Compiling active: getting a list from the API about existing pages


## Using the Command Line Interface

### Running cli.py

The python file cli.py needs to be run in the command line in the rosie virtualenv. This project is optimized for Mac. 

Every command consists of the following and the flag for one mode:

```
python cli.py
```

See `python cli.py --help` for some further usage assistance.

### Mode flags:

#### `--compile_active`

Make a taskfile of all the currently active pages on the OSF. This is useful primarily for --delete, which requires such a file to remove no-longer-existant pages from the mirror.


####`--scrape`

Crawl and scrape the site. Must include date marker `--dm=<DATE>`, where `<DATE>` is the date of last scrape in the form **YYYY-MM-DDTHH:MM:SS.000**, eg. 1970-06-15T00:00:00.000

One must specify which categories to scrape:

- `--nodes` (projects)
- `--registrations`
- `--users`
- `--institutions` 

 Any or all can be added.

If the nodes flag is used, one must specify which project pages to include:

- `-d` : dashboard
- `-f` : files page
- `-w` : wiki pages
- `-a` : analytics
- `-r` : list of registrations of the project
- `-k`: list of forks of the project

#### `--resume`

Pick up where a normal process left off in case of an unfortunate halt. The normal process creates and updates a .json task file with its status, and this must be included with the flag `--tf=<FILENAME>`. The filename will be of the form **YYYYMMDDHHMM.json** and should be visible in the ROSIEBot directory. 

#### `--verify`

Verify the completeness of the mirror. See below for steps. This process also requires a .json file in the form described in the resume step, and `--rn=<INT>`, where `<INT>` is the desired number of retries. 

##### Verification Steps

1. Verify that each URL found by the crawler has a corresponding file on the mirror.


2. Compare the size of each file to the minimum possible size for a complete page.


3. Rescrape failed pages and try again.

####  `--delete`

Remove anything inside a category folder that isn't listed on the API. Requires a compile_active-produced taskfile.

`python cli.py --delete --ctf=<TASKFILE>`

#### `--index`

Creates a search engine index. 

**Note**: Do not run until the static folder is in place in the archive.

Using search: the search button on each page should be replaced with a link to /search.html

## Hosting a Mirror

Scraped pages require a static folder inside the mirror. Please get a fresh copy from the OSF repo and place directly inside archive/.

Once static is in place, run `python cli.py --index` to set up search utility. 

### Simple local server setup
This option creates a flat copy of the archive without categorical folders. Nginx configuration is required otherwise. 

Make sure whatever utilities you desire (e.g. verify, index) have been run before the copy is made.

Run ``bash scripts/host_locally.sh`` from the ROSIEBot root. [Here is your mirror.](http://localhost:8888)

### Packaging the archive

`zip -r archive.zip archive/` 
`zip -r flat-archive.zip flat-archive/`

## Authenticating your mirror

(Future)


-----------

# [How to set up prerender](prerender.md) for a local OSF

-----------


![logo alt](https://cloud.githubusercontent.com/assets/15851093/16454893/79287ad8-3de0-11e6-9080-b90ac6ea16d4.png "'Beep boop', says Rosie.")

