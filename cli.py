import click
import datetime
import crawler
import json
import verifier
import codecs
import verifier

@click.command()
# Specify parameters that choose between different modes
@click.option('--compile_active', is_flag=True, help="Compile a list of active nodes")
@click.option('--scrape', is_flag=True, help="Do a normal scrape, need date marker specified")
@click.option('--resume', is_flag=True, help="Resume last unfinished scrape, need to import task file")
@click.option('--verify', is_flag=True, help="Verify the existing OSF static mirror, need to import task file")
# Specify parameters for other needed values
@click.option('--dm', default=None, type=click.STRING, help="Date marker needed for normal scrape")
@click.option('--tf', default=None, type=click.STRING, help="filename of the task file")
@click.option('--rt', default=2, type=click.INT, help="Number of times to retry scraping")
# Specify areas of scraping; if none of these are included in the command, then do a full scrape
@click.option('--registrations', is_flag=True, help="Add this flag if you want to scrape for registrations")
@click.option('--users', is_flag=True, help="Add this flag if you want to scrape for users")
@click.option('--institutions', is_flag=True, help="Add this flag if you want to scrape for institutions")
@click.option('--nodes', is_flag=True, help="Add this flag if you want to scrape for nodes")
# Specify types of node pages needed to scrape, only works for scraping nodes; if none are include, scrape all types
@click.option('-d', is_flag=True, help="Add this flag if you want to include dashboard page for nodes")
@click.option('-f', is_flag=True, help="Add this flag if you want to include files page for nodes")
@click.option('-w', is_flag=True, help="Add this flag if you want to include wiki page for nodes")
@click.option('-a', is_flag=True, help="Add this flag if you want to include analytics page for nodes")
@click.option('-r', is_flag=True, help="Add this flag if you want to include registrations page for nodes")
@click.option('-k', is_flag=True, help="Add this flag if you want to include forks page for nodes")
def cli_entry_point(scrape, resume, verify, compile_active, dm, tf, rt, registrations, users, institutions, nodes, d, f, w, a, r, k):
    if scrape and resume and verify and compile_active:
        click.echo('Invalid parameters.')
        return

    if not scrape and not resume and not verify and not compile_active:
        click.echo('You have to choose a mode to run')

    if compile_active:
        now = datetime.datetime.now()
        click.echo('Starting to compile a list of active nodes as of ' + str(now))
        filename = 'activelist-' + now.strftime('%Y%m%d%H%M' + '.json')
        click.echo('Creating a active node list file named : ' + filename)
        with open(filename, 'w') as file:
            compile_active_list(file)
        return

    if scrape and dm is not None:
        click.echo('Starting normal scrape with date marker set to : ' + dm)
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d%H%M' + '.json')
        click.echo('Creating a task file named : ' + filename)
        with open(filename, 'w') as db:
            normal_scrape(dm, registrations, users, institutions, nodes, d, f, w, a, r, k, db)
        return

    if resume and tf is not None:
        click.echo('Resuming scrape with the task file : ' + tf)
        try:
            with codecs.open(tf, 'r', encoding='utf-8') as db:
                resume_scrape(db, tf)
        except FileNotFoundError:
            click.echo('File Not Found for the task.')
        return

    if verify and tf is not None:
        try:
            verify.main(tf, rt)
        except FileNotFoundError:
            click.echo('File Not Found for the task.')
        return

    return


def compile_active_list(file):
    dict = {}
    rosie = crawler.Crawler()
    rosie.crawl_nodes_api(page_limit=10)
    list_of_active_nodes = [x[0].split('/')[4] for x in rosie.node_url_tuples]
    dict['list_of_active_nodes'] = list_of_active_nodes
    rosie.crawl_users_api(page_limit=10)
    list_of_active_users = [x.split('/')[4] for x in rosie.user_profile_page_urls]
    dict['list_of_active_users'] = list_of_active_users
    rosie.crawl_registrations_api(page_limit=10)
    list_of_active_registrations = [x[0].split('/')[3] for x in rosie.registration_url_tuples]
    dict['list_of_active_registrations'] = list_of_active_registrations
    json.dump(dict, file, indent=4)


def normal_scrape(dm,
                  scrape_registrations, scrape_users, scrape_institutions, scrape_nodes,
                  include_dashboard, include_files, include_wiki, include_analytics, include_registrations,
                  include_forks, db):

    date_marker = None
    if '.' in dm:
        date_marker = datetime.datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S.%f")
    else:
        date_marker = datetime.datetime.strptime(dm, "%Y-%m-%dT%H:%M:%S")

    if date_marker is None:
        click.echo("Date marker is not specified or specified date marker cannot be parsed")
        return

    store = {}
    store['scrape_registrations'] = scrape_registrations
    store['scrape_users'] = scrape_users
    store['scrape_institutions'] = scrape_institutions
    store['scrape_nodes'] = scrape_nodes
    store['include_dashboard'] = include_dashboard
    store['include_files'] = include_files
    store['include_wiki'] = include_wiki
    store['include_analytics'] = include_analytics
    store['include_registrations'] = include_registrations
    store['include_forks'] = include_forks
    store['nodes_finished'] = False
    store['registrations_finished'] = False
    store['users_finished'] = False
    store['institutions_finished'] = False
    store['scrape_finished'] = False
    store['node_urls'] = None
    store['registration_urls'] = None
    store['user_profile_page_urls'] = None
    store['institution_urls'] = None
    store['error_list'] = None
    store['milestone'] = None

    rosie = crawler.Crawler(date_modified=date_marker, db=db, dictionary=store)

    # Crawling the respective API for this scrape
    if scrape_nodes:
        rosie.crawl_nodes_api()
        if include_dashboard and include_files and include_analytics and \
                include_forks and include_registrations and include_wiki:
            rosie.generate_node_urls(all_pages=True)
        else:
            rosie.generate_node_urls(all_pages=False,
                                     dashboard=include_dashboard,
                                     files=include_files,
                                     wiki=include_wiki,
                                     analytics=include_analytics,
                                     registrations=include_registrations,
                                     forks=include_forks)
        store['node_urls'] = rosie.node_urls

    if scrape_registrations:
        rosie.crawl_registrations_api()
        rosie.generate_registration_urls()
        store['registration_urls'] = rosie.registration_urls

    if scrape_users:
        rosie.crawl_users_api()
        store['user_profile_page_urls'] = rosie.user_profile_page_urls

    if scrape_institutions:
        rosie.crawl_institutions_api()
        store['institution_urls'] = rosie.institution_urls

    json.dump(store, db, indent=4)
    db.flush()

    # Actual Scraping of the pages
    if scrape_nodes:
        rosie.scrape_nodes(async=True)
        store['nodes_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_registrations:
        rosie.scrape_registrations(async=True)
        store['registrations_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_users:
        rosie.scrape_users()
        store['users_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_institutions:
        rosie.scrape_institutions()
        store['institutions_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    store['scrape_finished'] = True
    db.seek(0)
    db.truncate()
    json.dump(store, db, indent=4)
    db.flush()


def resume_scrape(db, tf):
    store = json.load(db)
    db.close()

    db = open(tf, 'w')
    rosie = crawler.Crawler(db=db, dictionary=store)
    # Restore variables from persistent file
    try:
        scrape_nodes = store['scrape_nodes']
        scrape_registrations = store['scrape_registrations']
        scrape_users = store['scrape_users']
        scrape_institutions = store['scrape_institutions']
        nodes_finished = store['nodes_finished']
        registrations_finished = store['registrations_finished']
        users_finished = store['users_finished']
        institutions_finished = store['institutions_finished']
        scrape_finished = store['scrape_finished']
        milestone_url = store['milestone']
        rosie.node_urls = store['node_urls']
        rosie.registration_urls = store['registration_urls']
        rosie.user_profile_page_urls = store['user_profile_page_urls']
        rosie.institution_urls = store['institution_urls']
        if store['error_list'] is not None:
            rosie.error_list = store['error_list']
    except KeyError:
        click.echo('Cannot restore variables from file')
        return

    if scrape_finished:
        click.echo("The scrape to resume was already finished")
        return

    if scrape_nodes and not nodes_finished:
        if milestone_url in rosie.node_urls:
            rosie.node_urls = rosie.node_urls[rosie.node_urls.index(milestone_url):]
        rosie.scrape_nodes(async=True)
        store['nodes_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_registrations and not registrations_finished:
        if milestone_url in rosie.registration_urls:
            rosie.registration_urls = rosie.registration_urls[rosie.registration_urls.index(milestone_url):]
        rosie.scrape_registrations(async=True)
        store['registrations_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_users and not users_finished:
        if milestone_url in rosie.user_profile_page_urls:
            rosie.user_profile_page_urls = \
                rosie.user_profile_page_urls[rosie.user_profile_page_urls.index(milestone_url):]
        rosie.scrape_users()
        store['users_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    if scrape_institutions and not institutions_finished:
        if milestone_url in rosie.institution_urls:
            rosie.institution_urls = rosie.institution_urls[rosie.institution_urls.index(milestone_url):]
        rosie.scrape_institutions()
        store['institutions_finished'] = True
        db.seek(0)
        db.truncate()
        json.dump(store, db, indent=4)
        db.flush()

    store['scrape_finished'] = True
    db.seek(0)
    db.truncate()
    json.dump(store, db, indent=4)
    db.flush()


def verify_mirror(tf, rn):
    verifier.main(tf, rn)


if __name__ == '__main__':
    cli_entry_point()
