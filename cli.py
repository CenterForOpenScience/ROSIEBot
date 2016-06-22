import click
import shelve
import datetime
import crawler
import urllib

@click.command()
# Specify parameters that choose between different modes
@click.option('--normal', is_flag=True, help="Do a normal scrape, need date marker specified")
@click.option('--resume', is_flag=True, help="Resume last unfinished scrape, need to import task file")
@click.option('--verify', is_flag=True, help="Verify the existing OSF static mirror, need to import task file")
# Specify parameters for other needed values
@click.option('--dm', default=None, type=click.STRING, help="Date marker needed for normal scrape")
@click.option('--tf', default=None, type=click.STRING, help="filename of the task file")
# Specify areas of scraping; if none of these are included in the command, then do a full scrape
@click.option('--registrations', is_flag=True, help="Add this flag if you want to scrape for registrations")
@click.option('--users', is_flag=True, help="Add this flag if you want to scrape for users")
@click.option('--institutions', is_flag=True, help="Add this flag if you want to scrape for institutions")
@click.option('--nodes', is_flag=True, help="Add this flag if you want to scrape for nodes")
# Specify types of node pages needed to scrape, only works for scraping nodes; if none are include, scrape all types
@click.option('--d', is_flag=True, help="Add this flag if you want to include dashboard page for nodes")
@click.option('--f', is_flag=True, help="Add this flag if you want to include files page for nodes")
@click.option('--w', is_flag=True, help="Add this flag if you want to include wiki page for nodes")
@click.option('--a', is_flag=True, help="Add this flag if you want to include analytics page for nodes")
@click.option('--r', is_flag=True, help="Add this flag if you want to include registrations page for nodes")
@click.option('--fr', is_flag=True, help="Add this flag if you want to include forks page for nodes")
def cli_entry_point(normal, resume, verify, dm, tf, registrations, users, institutions, nodes, d, f, w, a, r, fr):
    if normal and resume and verify:
        click.echo('Invalid parameters.')
        return

    if not normal and not resume and not verify:
        click.echo('You have to choose a mode to run')

    if normal and dm is not None:
        try:
            test_connectivity()
        except:
            click.echo('Cannot connect to destinations')
            return

        click.echo('Starting normal scrape with date marker set to : ' + dm)
        now = datetime.datetime.now()
        filename = now.strftime('%Y%m%d%H%M' + '.task')
        click.echo('Creating a task file named : ' + filename)
        with shelve.open(filename, writeback=True, flag='n') as db:
            normal_scrape(dm, registrations, users, institutions, nodes, d, f, w, a, r, fr, db)
        return

    if resume and tf is not None:
        try:
            test_connectivity()
        except:
            click.echo('Cannot connect to destinations')
            return

        click.echo('Resuming scrape withe the task file : ' + tf)
        try:
            with shelve.open(tf, writeback=False, flag='w') as db:
                resume_scrape(db)
        except FileNotFoundError:
            click.echo('File Not Found for the task.')
        return

    if verify and tf is not None:
        # verify_mirror(tf)
        return

    return

def test_connectivity():
    response = urllib.urlopen(crawler.base_urls[0], timeout=1)
    response2 = urllib.urlopen(crawler.base_urls[1], timeout=1)


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

    # Store/initialize variables into persistent file
    db['scrape_registrations'] = scrape_registrations
    db['scrape_users'] = scrape_users
    db['scrape_institutions'] = scrape_institutions
    db['scrape_nodes'] = scrape_nodes
    db['include_dashboard'] = include_dashboard
    db['include_files'] = include_files
    db['include_wiki'] = include_wiki
    db['include_analytics'] = include_analytics
    db['include_registrations'] = include_registrations
    db['include_forks'] = include_forks
    db['nodes_finished'] = False
    db['registrations_finished'] = False
    db['users_finished'] = False
    db['institutions_finished'] = False
    db['scrape_finished'] = False
    db['node_urls'] = None
    db['node_url_tuples'] = None
    db['registration_urls'] = None
    db['registration_url_tuples'] = None
    db['user_profile_page_urls'] = None
    db['institution_urls'] = None

    rosie = crawler.Crawler(date_modified=date_marker, db=db)

    _scrape_api(rosie, db, scrape_nodes, scrape_registrations, scrape_users, scrape_institutions)

    if scrape_nodes:
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
        db['nodes_url'] = rosie.node_urls
        rosie.scrape_nodes(async=False)
        db['nodes_finished'] = True

    if scrape_registrations:
        rosie.generate_registration_urls()
        db['registration_urls'] = rosie.registration_urls
        rosie.scrape_registrations(async=False)
        db['registrations_finished'] = True

    if scrape_users:
        rosie.scrape_users()
        db['users_finished'] = True

    if scrape_institutions:
        rosie.scrape_institutions()
        db['institutions_finished'] = True

    db['scrape_finished'] = True


def _scrape_api(cr, db, scrape_nodes, scrape_registrations, scrape_users, scrape_institutions):
    if scrape_nodes:
        cr.crawl_nodes_api()
        db['node_url_tuples'] = cr.node_url_tuples

    if scrape_registrations:
        cr.crawl_registrations_api()
        db['registration_url_tuples'] = cr.registration_url_tuples

    if scrape_users:
        cr.crawl_users_api()
        db['user_profile_page_urls'] = cr.user_profile_page_urls

    if scrape_institutions:
        cr.crawl_institutions_api()
        db['institution_urls'] = cr.institution_urls


def resume_scrape(db):
    rosie = crawler.Crawler(db=db)
    # Restore variables from persistent file
    try:
        scrape_nodes = db['scrape_nodes']
        scrape_registrations = db['scrape_registrations']
        scrape_users = db['scrape_users']
        scrape_institutions = db['scrape_institutions']
        include_dashboard = db['include_dashboard']
        include_files = db['include_files']
        include_wiki = db['include_wiki']
        include_analytics = db['include_analytics']
        include_registrations = db['include_registrations']
        include_forks = db['include_forks']
        nodes_finished = db['nodes_finished']
        registrations_finished = db['registrations_finished']
        users_finished = db['users_finished']
        institutions_finished = db['institutions_finished']
        scrape_finished = db['scrape_finished']
        milestone_url = db['milestone']
        rosie.node_url_tuples = db['node_url_tuples']
        rosie.node_urls = db['node_urls']
        rosie.registration_url_tuples = db['registration_url_tuples']
        rosie.registration_urls = db['registration_urls']
        rosie.user_profile_page_urls = db['user_profile_page_urls']
        rosie.institution_urls = db['institution_urls']
    except KeyError:
        click.echo('Cannot restore variables from file')
        return

    if scrape_finished:
        click.echo("The scrape to resume was already finished")
        return

    if scrape_nodes and not nodes_finished:
        if rosie.node_urls is None:
            rosie.node_urls = []
            rosie.generate_node_urls(all_pages=False,
                                     dashboard=include_dashboard,
                                     files=include_files,
                                     wiki=include_wiki,
                                     analytics=include_analytics,
                                     registrations=include_registrations,
                                     forks=include_forks)
        if milestone_url in rosie.node_urls:
            rosie.node_urls = rosie.node_urls[rosie.node_urls.index(milestone_url):]
        rosie.scrape_nodes(async=True)
        db['nodes_finished'] = True

    if scrape_registrations and not registrations_finished:
        if rosie.registration_urls is None:
            rosie.registration_urls = []
            rosie.generate_registration_urls()
        if milestone_url in rosie.registration_urls:
            rosie.registration_urls = rosie.registration_urls[rosie.registration_urls.index(milestone_url):]
        rosie.scrape_registrations(async=True)
        db['registrations_finished'] = True

    if scrape_users and not users_finished:
        if milestone_url in rosie.user_profile_page_urls:
            rosie.user_profile_page_urls = rosie.user_profile_page_urls[rosie.user_profile_page_urls.index(milestone_url):]
        rosie.scrape_users()
        db['users_finished'] = True

    if scrape_institutions and not institutions_finished:
        if milestone_url in rosie.institution_urls:
            rosie.institution_urls = rosie.institution_urls[rosie.institution_urls.index(milestone_url):]
        rosie.scrape_institutions()
        db['institutions_finished'] = True

    db['scrape_finished'] = True

if __name__ == '__main__':
    cli_entry_point()
