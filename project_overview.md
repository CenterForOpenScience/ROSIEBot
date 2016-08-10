## Introduction
This document serves to provide a large picture of the entire Mirroring project. The mirroring project focuses on creating a static mirror of all the public facing content of the Open Science Framework while preserving UI parity (to a certain extent). Thus, the major obstacle lies with the fact that modern day web technology is AJAX-heavy. A traditional crawler/scraper that only downloads the html of each webpage does not preserve the information retrieved through AJAX calls.

To solve the problem, a customized crawler/scraper is implemented to **call the public-facing API V2 of the OSF, get the urls of pages to scrape**, and then scrape those respective pages. 

Working in conjunction with the crawler/scraper is the **Prerender** service running on the OSF server. Prerender is an SEO tool based on PhantomJS. After receiving a request initiated by the crawler/scraper, Prerender would execute the Javascript, then return the HTML page after AJAX calls. 

The crawler/scraper would then **save the html page** to local file system.

After saving the pages, a **verification** process will go through the html files saved and find blank pages (a possible result due to server error) and pages that are not retrieved due to server timeout (504s), and will **retry** those pages until all are retrieved correctly.

The process of **updating** can add, modify, or delete local files based on content in the API. Through two different processes, deletion removes what no longer exists online and new scrapes look for new or modified pages.

To implement **search functionality**, lunr.js, a client-side JS search engine, is used with a custom indexer. The indexer will comb through all the project dashboard, registration dashboard and user profile pages and index necessary information. The outputted index (in json format) will be used by lunr.js as a search engine index.


## What We Have Done

### Crawler/scraper:
- The crawler scraper can scrape specific page types or all public facing pages of OSF. 
- Each scrape is considered as a “task” and a task file in json format will be created. It contains all relevant information about the scrape. 
- In cash of a crash, the crawler/scraper is able to resume the task with information stored in the task file.
### Verifier: 
- Combs through the task file for a list of pages
- Verifies that the local copy is present and not blank
- Re-scrapes any noncompliant pages.
### Deleter: 
- With the compile_active utility, parses through the current archive
- Deletes local files which are no longer present on the OSF.
### Indexer: 
- Indexes the stored pages and outputs an index file in json format.
- A search page uses the file and lunr.js for a static engine.

### Changes to the OSF
- Make sure prerender would not return a page that is not fully rendered. [[OSF 6735]](https://openscience.atlassian.net/browse/OSF-6735)

- Take care of logs with absolute urls. [[OSF 6691]](https://openscience.atlassian.net/browse/OSF-6691)

- Add date_modified field to User and Institutions. [[OSF 6642]](https://openscience.atlassian.net/browse/OSF-6642)

- *Pending:* Allow filtering registrations by date_modified and updating the value upon retraction [[OSF 6686]](https://openscience.atlassian.net/browse/OSF-6686)

## Possible Future Steps

#####The biggest problem with the current static pages is that most UI interactions does not work because they need Javascript and AJAX calls. 

If we want to make the mirror fully static while preserving those UI functionalities, the only plausible way is to archive API responses into json files so that JS files can make AJAX calls to those “endpoints” and get a json file in response. 

There are several solutions:

The first solution is very NGiNX-heavy. The core concept is to implement lots of routing rules within nginx configuration file to make sure each call is routed to the correct static json file. This approach needs the archived API responsed to be stored under the directory in a format that is similar to the path of the api calls endpoint to reduce the amount of work in configuration for routing. Overall, this approach requires the least change to existing JS files.

The second solutions it to rewrite all the jS files and change their endpoints. Or we could find a way to intercept all API calls (on the client side) and route them to the “correct” endpoint on a host server.

The third is a combination of a) and b).
Since the current OSF still uses both API V1 and API V2, it would be best to wait till the deprecation of API V1 before we implement solutions to the corner cases. We are currently planning to do a proof-of-concept implementation for the rest of the week.

##### Currently the search engine uses a json file as the index. 
The index contains not enough information for full text search since a full-text index would be too big to be used as a static asset. We can come up with ways to compress the size of the index (through NGiNX configs) but the size would always be a concern if we go with the client-side search engine solution. 

However, a static mirror does not mean we have to use a client-side search solution. As OSF grows, we could set up a centralized elasticsearch/solr search server with restful APIs. In which case the mirror would be able to query the endpoints. The downside to this solution is that COS has to maintain one more service and promise to keep that service always in good condition.

On the other hand, since SHARE V2 is already collecting lots of data on public-facing content of OSF, we can use the data SHARE collected as indexes.

##### The transition to Ember is the next step. 
It seems that Ember and Prerender works well together and with Ember FastBoot, we will be able to generate fully rendered pages on the server-side using the client-side JS scripts. (Isomorphic Javascript) And since Ember would be fully dependent on API v2, the archiving of API responses will become more useful when we transition to Ember fully.

##### Since we are making a mirror of the OSF, **content integrity** is very important. 

In other words, we have to make sure the mirror we produce and distribute is not corrupted or tampered with when it is hosted on another server. 

An authentication service could be implemented so that the md5 (or any other hashes) of the html body is computed and stored when we produce the mirror. Later a JS file could be used to compare the hash of the hosted version with that of ours, thus ensuring the integrity of the content.
We also have to select a handful of hosts and mark them as trustworthy mirror hosts. For those hosts, we can add them to a multi-domain SSL certificate. Or we can consolidate access to mirrors to the a domain that COS controls (e.g. mirrors.osf.io) and then redirect users to different mirror hosts depending on location/usage/etc.

Finally, if we have a fully functional mirror on trustworthy hosts, we may add them as a backup to the dynamic OSF as CDNs,
