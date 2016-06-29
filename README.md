# ROSIEBot:
# The Robotic Open Science Indexing Engine


![rosie alt](https://cloud.githubusercontent.com/assets/15851093/16431535/109ac052-3d4f-11e6-9218-e7a457898492.png '"Eight legged wonder: 
Crawling, enduring, facing,
Despite childish fears!"  - Unknown')


- ##### Static mirroring utility for the [Open Science Framework](osf.io), maintained by     the [Center for Open Science](cos.io).
  Visit the [COS Github](https://github.com/CenterForOpenScience/) for more innovations in   the *openness*, *integrity*, and *reproducibility* of scientific research.



## ROSIEisms

##### Site Hierarchy
|                   |                                                                   |
|-------------------|-------------------------------------------------------------------|
| Type              | An type of content hosted on the OSF, with its own GUID.          |
| Page              | One of the pages associated with a type (see below)               |
| File              | A page instance / specific URL                                    |


##### OSF Content Types

- Projects
- Registrations
- Users
- Institutions

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

##### Our Process
- Crawling: getting lists of all the URLs to visit


- Scraping: visiting all those URLs and saving their content to the mirror


- Resuming: continuing the crawl/scrape process if it stops in the middle


- Verifying: making sure all the files are present and in acceptable condition


## Using the Command Line Interface

There are various options for what areas of the OSF are preserved in a mirror. All or any content types can be included in the mirror, and all or any project pages can be included. Specifying pages of registrations is not available.

### Running cli.py

The python file cli.py needs to be run in the command line. This project was developed on Mac, so Terminal on OS X is preferred. 

```bash
python3 cli.py
```

Flags:

**`--scrape`**

Crawl and scrape the site. Must include date marker `--dm=<DATE>`, where `<DATE>` is the date of last scrape in the form **YYYY-MM-DDTHH:MM:SS.000**, ex. 1970-06-15T00:00:00.000

This is where specifying `--nodes` (projects), `--registrations`, `--users`, `--institutions` is possible. If none are specified, all are included by default.

When projects are included, whether explicitly or by default, the following flags may be used to include project pages:

- `-d` : dashboard
- `-f` : files page
- `-w` : wiki pages
- `-a` : analytics
- `-r` : list of registrations of the project
- `-k`: list of forks of the project

**`--resume`**

Pick up where a normal process left off in case of an unfortunate halt. The normal process creates and updates a .json task file with its status, and this must be included with the flag `--tf=<FILENAME>`. The filename will be of the form **YYYYMMDDHHMM.json** and should be visible in the ROSIEBot directory. 

**`--verify`**

Verify the completeness of the mirror. See below for steps. This process also requires the .json file described for the resume process.


## Verification Steps

1. Verify that each URL found by the crawler has a corresponding file on the mirror.


2. Compare the size of each file to the minimum possible size for a complete page.


3. Check that certain spots in each file that contain important information are present.


4. Rescrape failed pages and try again.

## Hosting a Mirror (Future)
- Mirror search tools
- Nginx configurations

## Authenticating your mirror
- The mirror warns users that they are on a static copy of the OSF.
- Sign up with the Center for Open Science to be an official mirror (Future)
- -
- -
- -
-

-----------

### Acknowledgements:

Chris Seto ( @chrisseto ) , Nan Chen ( @chennan47 ), Matt Frazier ( @mfraezz ), 

and the COS Product Team.

-----------


![logo alt](https://cloud.githubusercontent.com/assets/15851093/16454893/79287ad8-3de0-11e6-9080-b90ac6ea16d4.png "'Beep boop', says Rosie.")

