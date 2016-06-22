import click
import shelve
import datetime
import crawler

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

    if normal and dm is not None:
        click.echo('Starting normal scrape with date marker set to : ' + dm)
        filename = "task-" + str(datetime.datetime.now()) + ".task"
        click.echo('Creating a task file named : ' + filename)
        with shelve.open(filename, writeback=True) as db:
            normal_scrape(dm, registrations, users, institutions, nodes, d, f, w, a, r, fr, db)

        return

    if resume and tf is not None:
        # resume_scrape(tf)
        return

    if verify and tf is not None:
        # verify_mirror(tf)
        return

    return


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

    # Store variables into persistent file
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

    rosie = crawler.Crawler(date_modified=date_marker, db=db)
    if scrape_nodes:
        rosie.crawl_nodes_api()
        rosie.truncate_node_url_tuples()
        db['node_url_tuples'] = rosie.node_url_tuples
        if include_dashboard and include_files and include_analytics and \
                include_forks and include_registrations and include_wiki:
            rosie.generate_node_urls(all_pages=True)
        else:
            rosie.generate_node_urls(dashboard=include_dashboard, files=include_files, wiki=include_wiki,
                                     analytics=include_analytics, registrations=include_registrations,
                                     forks=include_forks)
        rosie.scrape_nodes(async=False)
        db['nodes_finished'] = True

    if scrape_registrations:
        pass

    if scrape_users:
        pass

    if scrape_institutions:
        pass

if __name__ == '__main__':
    cli_entry_point()
