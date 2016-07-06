import json, codecs
from pages import ProjectDashboardPage, ProjectFilesPage, ProjectAnalyticsPage, \
    ProjectForksPage, ProjectRegistrationsPage, ProjectWikiPage, RegistrationDashboardPage, RegistrationFilesPage, \
    RegistrationAnalyticsPage, RegistrationForksPage, RegistrationWikiPage, UserProfilePage, InstitutionDashboardPage
from crawler import Crawler


# Verifier superclass
class Verifier:
    def __init__(self, min_size, pg_type, end):
        self.minimum_size = min_size
        self.page_type = pg_type
        self.url_end = end
        self.page_elements = {}
        self.pages = []
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_filename, json_list):
        """
        :param json_filename: The json file
        :param json_list: The list in the json file of found URLs
        :return: Null, but self.pages is populated.
        """
        for url in json_list:
            if self.url_end in url:
                print('rel: ', url)
                if url in json_filename['error_list']:
                    self.failed_pages.append(url)
                    print('error: ', url)
                else:
                    try:
                        obj = self.page_type(url)
                        self.pages.append(obj)
                    except FileNotFoundError:
                        self.failed_pages.append(url)
                json_list.remove(url)

    # Compare page size to page-specific minimum that any fully-scraped page should have
    def size_comparison(self):
        for page in self.pages:
            # print(page)
            # print(page.file_size)
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
        return

    # Check that specified elements are present and non-empty in each page
    # Check that specified elements or their alternates are present and non-empty in each page
    # Alternate: different elements appear if there isn't supposed to be content, so it has to check both
    # Format: Filled-in : Alternate
    def spot_check(self):
        for page in self.pages:
            soup = page.get_content()
            for element in self.page_elements:
                alt = self.page_elements[element]
                result = soup.select(element)
                # No results or empty results
                if (len(result) == 0 or len(result[0].contents) == 0) and alt != '':
                    # print("Failed: first spot_check(): ", page, element, "Retrying with alt: ", alt)
                    alt_result = soup.select(alt)

                    # Element's alternate has no or empty results
                    if len(alt_result) == 0 or len(alt_result[0].contents) == 0:
                        print("Failed: alternate spot_check(): ", page, alt, '\n')
                        self.failed_pages.append(page.url)
                        break

                elif (len(result) == 0 or len(result[0].contents) == 0) and alt == '':
                    print('Failed: spot_check(): ', page, element, "No alt.", '\n')
                    self.failed_pages.append(page.url)
                    break

        return

    def run_verifier(self, json_filename, json_list):
        self.harvest_pages(json_filename, json_list)
        self.size_comparison()
        self.spot_check()


# Verifier subclasses

class ProjectDashboardVerifier(Verifier):
    def __init__(self):
        super().__init__(410, ProjectDashboardPage, '')
        self.page_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors span.date.node-last-modified-date': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#tb-tbody': '',  # File list
            '#render-node': 'div.row > div:nth-of-type(2) > div.components.panel.panel-default > div.panel-body > p',
            # Nodes list
            '#logScope > div > div > div.panel-body > span > dl': '#logFeed > div > p'
            # Activity / "Unable to retrieve at this time"
        }


class ProjectFilesVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectFilesPage, "files/")
        self.page_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }


class ProjectWikiVerifier(Verifier):
    def __init__(self):
        super().__init__(410, ProjectWikiPage, "wiki/")
        self.page_elements = {
            'pre': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }


class ProjectAnalyticsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectAnalyticsPage, "analytics/")
        self.page_elements = {
            '#adBlock': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }


class ProjectRegistrationsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectRegistrationsPage, "registrations/")
        self.page_elements = {
            '#renderNode': '#registrations > div > div > p'  # List of nodes
        }


class ProjectForksVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectForksPage, "forks/")
        self.page_elements = {
            '#renderNode': 'div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }


class RegistrationDashboardVerifier(Verifier):
    def __init__(self):
        super().__init__(410, RegistrationDashboardPage, "")
        self.page_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors > div > p:nth-of-type(5) > span': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#tb-tbody': '',  # File list
            '#render-node': 'div.row > div:nth-of-type(2) > div.components.panel.panel-default > div.panel-body > p',
            # Nodes list
            '#logScope > div > div > div.panel-body > span > dl': '#logFeed > div > p'
            # Activity / "Unable to retrieve at this time"
        }


class RegistrationFilesVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationFilesPage, "files/")
        self.page_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }


class RegistrationWikiVerifier(Verifier):
    def __init__(self):
        super().__init__(410, RegistrationWikiPage, "wiki/")
        self.page_elements = {
            'pre': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }


class RegistrationAnalyticsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationAnalyticsPage, "analytics/")
        self.page_elements = {
            '#adBlock': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }


class RegistrationForksVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationForksPage, "forks/")
        self.page_elements = {
            '#renderNode': 'div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }


class UserProfileVerifier(Verifier):
    def __init__(self):
        super().__init__(80, UserProfilePage, "")
        self.page_elements = {
            '#projects': 'div > div:nth-of-type(1) > div > div.panel-body > div',  # Project list / "No projects"
            '#components': 'div > div:nth-of-type(2) > div > div.panel-body > div',  # Component list / "No components"
            'body h2': ''  # Activity points, project count
        }


class InstitutionDashboardVerifier(Verifier):
    def __init__(self):
        super().__init__(350, InstitutionDashboardPage, "")
        self.page_elements = {
            '#fileBrowser > div.db-infobar > div > div': '#fileBrowser > div.db-infobar > div > div',  # Project preview
            '#tb-tbody': '#fileBrowser > div.db-main > div.db-non-load-template.m-md.p-md.osf-box'  # Project browser
        }


# Called when json file had scrape_nodes = true
# Checks for all the components of a project and if they were scraped
# Verifies them and returns a list of the failed pages
def verify_nodes(verification_dictionary, list_name):
    nodes_list_verified = []
    if verification_dictionary['include_files']:
        project_files_verifier = ProjectFilesVerifier()
        project_files_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_files = project_files_verifier.failed_pages
        nodes_list_verified += project_files
    if verification_dictionary['include_wiki']:
        project_wiki_verifier = ProjectWikiVerifier()
        project_wiki_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_wiki = project_wiki_verifier.failed_pages
        nodes_list_verified += project_wiki
    if verification_dictionary['include_analytics']:
        project_analytics_verifier = ProjectAnalyticsVerifier()
        project_analytics_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_analytics = project_analytics_verifier.failed_pages
        nodes_list_verified += project_analytics
    if verification_dictionary['include_registrations']:
        project_registrations_verifier = ProjectRegistrationsVerifier()
        project_registrations_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_registrations = project_registrations_verifier.failed_pages
        nodes_list_verified += project_registrations
    if verification_dictionary['include_forks']:
        project_forks_verifier = ProjectForksVerifier()
        project_forks_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_forks = project_forks_verifier.failed_pages
        nodes_list_verified += project_forks
    if verification_dictionary['include_dashboard']:  # This must go last because its URLs don't have a specific ending.
        project_dashboards_verifier = ProjectDashboardVerifier()
        project_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
        project_dashboards = project_dashboards_verifier.failed_pages
        nodes_list_verified += project_dashboards
    return nodes_list_verified


# Called when json file had scrape_registrations = true
# Verifies the components of a registration and returns a list of the failed pages
def verify_registrations(verification_dictionary, list_name):
    # Must run all page types automatically
    registration_files_verifier = RegistrationFilesVerifier()
    registration_files_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    registration_files = registration_files_verifier.failed_pages

    registration_wiki_verifier = RegistrationWikiVerifier()
    registration_wiki_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    registration_wiki = registration_wiki_verifier.failed_pages

    registration_analytics_verifier = RegistrationAnalyticsVerifier()
    registration_analytics_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    registration_analytics = registration_analytics_verifier.failed_pages

    registration_forks_verifier = RegistrationForksVerifier()
    registration_forks_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    registration_forks = registration_forks_verifier.failed_pages

    registration_dashboards_verifier = RegistrationDashboardVerifier()
    registration_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    registration_dashboards = registration_dashboards_verifier.failed_pages

    registrations_list_verified = registration_files + registration_wiki + registration_analytics + \
        registration_forks + registration_dashboards
    return registrations_list_verified


# Called when json file had scrape_users = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_users(verification_dictionary, list_name):
    user_profiles_verifier = UserProfileVerifier()
    user_profiles_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    user_profiles = user_profiles_verifier.failed_pages
    return user_profiles


# Called when json file had scrape_institutions = true
# Verifies all user profile pages and returns a list of the failed pages
def verify_institutions(verification_dictionary, list_name):
    institution_dashboards_verifier = InstitutionDashboardVerifier()
    institution_dashboards_verifier.run_verifier(verification_dictionary, verification_dictionary[list_name])
    institution_dashboards = institution_dashboards_verifier.failed_pages
    return institution_dashboards


def call_rescrape(json_filename, verification_json_filename):
    print("Called rescrape")
    second_chance = Crawler()
    if json_filename['scrape_nodes']:
        second_chance.node_urls = verification_json_filename['node_urls_failed_verification']
        second_chance.scrape_nodes()
    if json_filename['scrape_registrations']:
        second_chance.registration_urls = verification_json_filename['registration_urls_failed_verification']
    if json_filename['scrape_users']:
        second_chance.user_urls = verification_json_filename['user_urls_failed_verification']
    if json_filename['scrape_institutions']:
        second_chance.institution_urls = verification_json_filename['institution_urls_failed_verification']


def setup_verification(json_dictionary, verification_json_dictionary, first_scrape):
    print("Check verification")
    if json_dictionary['scrape_nodes']:
        if first_scrape:
            list_name = 'node_urls'
        else:
            list_name = 'node_urls_failed_verification'
        verification_json_dictionary['node_urls_failed_verification'] = verify_nodes(json_dictionary, list_name)
    if json_dictionary['scrape_registrations']:
        if first_scrape:
            list_name = 'registration_urls'
        else:
            list_name = 'registration_urls_failed_verification'
        verification_json_dictionary['registration_urls_failed_verification'] = verify_registrations(json_dictionary,
                                                                                                     list_name)
    if json_dictionary['scrape_users']:
        if first_scrape:
            list_name = 'user_urls'
        else:
            list_name = 'user_urls_failed_verification'
        verification_json_dictionary['user_urls_failed_verification'] = \
            verify_users(json_dictionary, list_name)
    if json_dictionary['scrape_institutions']:
        if first_scrape:
            list_name = 'institution_urls'
        else:
            list_name = 'institution_urls_failed_verification'
        verification_json_dictionary['institution_urls_failed_verification'] = verify_institutions(json_dictionary,
                                                                                                   list_name)


def run_verification(json_file, num_retries):
    for i in range(num_retries):
        with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
            run_info = json.load(failure_file)
        with codecs.open(json_file, mode='r', encoding='utf-8') as failure_file:
            run_copy = json.load(failure_file)
        if i == 0:
            print("Begun 1st run")
            if run_info['scrape_finished']:
                setup_verification(run_info, run_copy, True)
                with codecs.open(json_file, mode='w', encoding='utf-8') as file:
                    json.dump(run_copy, file, indent=4)
                    print("Dumped json run_copy 1st verify")
            call_rescrape(run_info, run_copy)
        else:
            print("Begun 2nd run")
            setup_verification(run_copy, run_copy, False)
            # truncates json and dumps new lists
            with codecs.open(json_file, mode='w', encoding='utf-8') as file:
                json.dump(run_copy, file, indent=4)
            call_rescrape(run_copy, run_copy)


def main(json_filename, num_retries):
    # for testing:
    # json_filename = '201606301141.json'
    # num_retries = 2
    # call two verification/scraping methods depending on num retries
    run_verification(json_filename, num_retries)
