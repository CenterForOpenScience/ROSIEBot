# ROSIEBot: 
# The Robotic Open Science Indexing Engine
![alt tag](https://cloud.githubusercontent.com/assets/15851093/16431535/109ac052-3d4f-11e6-9218-e7a457898492.png)

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


## Producing a Mirror

There are various options for what areas of the OSF are preserved in a mirror. All or any content types can be included in the mirror, and all or any project pages can be included. Specifying pages of registrations is not available.

### Running cli.py

The python file cli.py needs to be run in the command line. This project was developed on Mac, so Terminal on OS X is preferred. 

```bash
python3 cli.py
```

Flags:

**`--normal`**

Crawl and scrape the site. Must include date marker `--dm=<DATE>`, where `<DATE>` is the date of last scrape in the form **YYYY-MM-DDTHH:MM:SS.000**, ex. 1970-06-15T00:00:00.000

This is where specifying `--nodes` (projects), `--registrations`, `--users`, `--institutions` is possible. If none are specified, all are included by default.

When projects are included, whether explicitly or by default, the following flags may be used to include project pages:

- `--d` : dashboard
- `--f` : files page
- `--w` : wiki pages
- `--a` : analytics
- `--r` : list of registrations of the project
- `--fr`: list of forks of the project

**`--resume`**

Pick up where a normal process left off in case of an unfortunate halt. The normal process creates and updates a .json task file with its status, and this must be included with the flag `--tf=<FILENAME>`. The filename will be of the form **YYYYMMDDHHMM.json** and should be visible in the ROSIEBot directory. 

**`--verify`**

Verify the completeness of the mirror. See below for steps. This process also requires the .json file described for the resume process.


## Verification Steps

1. Does the file exist for each URL in the task file?
2. 

## Hosting a Mirror
- search
- nginx

## Authentication your mirror (Future)
- All mirrored pages have a warning at the bottom that they are a mirror
- Sign up with the Center for Open Science to be an official mirror

-----------

![logo alt](https://cloud.githubusercontent.com/assets/15851093/16454893/79287ad8-3de0-11e6-9080-b90ac6ea16d4.png "'Beep boop', says Rosie.")

