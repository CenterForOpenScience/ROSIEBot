import json
import codecs
from pages import ProjectDashboardPage, ProjectFilesPage, ProjectAnalyticsPage, \
    ProjectForksPage, ProjectRegistrationsPage, ProjectWikiPage, RegistrationDashboardPage, RegistrationFilesPage, \
    RegistrationAnalyticsPage, RegistrationForksPage, RegistrationWikiPage, UserProfilePage, InstitutionDashboardPage
from crawler import Crawler
import bs4


# Verifier superclass
class Verifier:
    def __init__(self, min_size, pg_type, end):
        """
        :param min_size: File size minimum for a page. Anything below this couldn't possibly be a complete file.
        :param pg_type: The class to instantiate page objects with.
        :param end: Indentifier in the URL, e.g. 'files/', 'end' is a misnomer ('wiki/' in the middle of a URL)
        """
        self.minimum_size = min_size
        self.page_type = pg_type
        self.url_end = end

        # Certain elements will be absent if there's no content for them to display, so we check if there is a loading
        # bar in its place. This means the element should exist, but it doesn't.
        self.loading_elements = {}

        # Other elements will be replaced by a message if there's no content for them (e.g. "This user has no projects")
        # We check for the elements and their alternates if the original isn't found.
        self.alternate_elements = {}

        self.pages = []  # All the page objects
        self.failed_pages = []

    # Populate self.pages with the relevant files
    def harvest_pages(self, json_dictionary, json_list):
        """
        :param json_dictionary: The dictionary created from the json file
        :param json_list: The list in the json file of found URLs
        :return: Null, but self.pages is populated.
        """
        for url in json_list[:]:
            if self.url_end in url:
                print('rel: ', url)
                if url in json_dictionary['error_list']:
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
        for page in self.pages[:]:
            # print(page)
            # print(page.file_size)
            if not page.file_size > self.minimum_size:
                print('Failed: size_comparison(): ', page, ' has size: ', page.file_size)
                self.failed_pages.append(page.url)
                self.pages.remove(page)
        return

    # Check that specified elements are supposed to exist and a loading bar isn't present instead
    # Check that specified elements or their alternates are present and non-empty in each page
    # Alternate: different elements appear if there isn't supposed to be content, so it has to check both
    # Format: Filled-in : Alternate
    def spot_check(self):
        for page in self.pages[:]:
            soup = page.get_content()
            # Existential crisis:
            for element in self.loading_elements:
                final_element = self.loading_elements[element]  # What is supposed to be there
                loading_bar_result = soup.select(element)  # Is a loading bar present?
                if len(loading_bar_result) > 0:  # A loading bar exists (so content does not exist completely)
                    print("Failed: existential spot_check() ", page, final_element, " doesn't exist, loader ", element, " present.")
                    self.failed_pages.append(page.url)
                    self.pages.remove(page)
                    break

            # Alternate checker:
            for element in self.alternate_elements:
                alt = self.alternate_elements[element]
                result = soup.select(element)
                # No results or empty results, with alternate
                if (len(result) == 0 or len(result[0].contents) == 0) and alt != '':
                    alt_result = soup.select(alt)

                    # Element's alternate has no or empty results
                    if len(alt_result) == 0 or len(alt_result[0].contents) == 0:
                        print("Failed: alternate spot_check(): ", page, alt, '\n')
                        self.failed_pages.append(page.url)
                        self.pages.remove(page)
                        break

                # Element has no alternate and no results or empty results
                elif (len(result) == 0 or len(result[0].contents) == 0) and alt == '':
                    print('Failed: spot_check(): ', page, element, "No alt.", '\n')
                    self.failed_pages.append(page.url)
                    self.pages.remove(page)
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
        self.loading_elements = {
            "#treeGrid > div > p": '#tb-tbody',  # Files list
            "#containment": "#render-node",  # Exists if there are supposed to be components / Is it filled?
        }
        self.alternate_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors span.date.node-last-modified-date': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#tb-tbody': '',  # File list
            '#logScope > div > div > div.panel-body > span > dl': '#logFeed > div > p'
            # Activity / "Unable to retrieve at this time"
        }

    # Override: the loader for loading_elements is still supposed to exist
    # Check that specified elements are supposed to exist and a loading bar isn't present instead
    # Check that specified elements or their alternates are present and non-empty in each page
    # Alternate: different elements appear if there isn't supposed to be content, so it has to check both
    # Format: Filled-in : Alternate
    def spot_check(self):
        for page in self.pages[:]:
            soup = page.get_content()
            # Existential crisis:
            for element in self.loading_elements:
                final_element = self.loading_elements[element]  # What is supposed to be there
                loading_bar_result = soup.select(element)
                if len(loading_bar_result) > 0:  # Container div is present
                    final_result = soup.select(final_element)
                    if len(final_result) == 0:  # Final element isn't in place
                        print("Failed: existential spot_check() ", page, final_element, " doesn't exist, loader ", element,
                              " present.")
                        self.failed_pages.append(page.url)
                        self.pages.remove(page)
                        break

            # Alternate checker:
            for element in self.alternate_elements:
                alt = self.alternate_elements[element]
                result = soup.select(element)
                # No results or empty results, with alternate
                if (len(result) == 0 or len(result[0].contents) == 0) and alt != '':
                    alt_result = soup.select(alt)

                    # Element's alternate has no or empty results
                    if len(alt_result) == 0 or len(alt_result[0].contents) == 0:
                        print("Failed: alternate spot_check(): ", page, alt, '\n')
                        self.failed_pages.append(page.url)
                        self.pages.remove(page)
                        break

                # Element has no alternate and no results or empty results
                elif (len(result) == 0 or len(result[0].contents) == 0) and alt == '':
                    print('Failed: spot_check(): ', page, element, "No alt.", '\n')
                    self.failed_pages.append(page.url)
                    self.pages.remove(page)
                    break
        return


class ProjectFilesVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectFilesPage, "files/")
        self.alternate_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }


class ProjectWikiVerifier(Verifier):
    def __init__(self):
        super().__init__(410, ProjectWikiPage, "wiki/")
        self.alternate_elements = {
            '#wikiViewRender': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }


class ProjectAnalyticsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectAnalyticsPage, "analytics/")
        self.alternate_elements = {
            '#adBlock': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }


class ProjectRegistrationsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectRegistrationsPage, "registrations/")
        self.alternate_elements = {
            '#renderNode': '#registrations > div > div > p'  # List of nodes
        }


class ProjectForksVerifier(Verifier):
    def __init__(self):
        super().__init__(380, ProjectForksPage, "forks/")
        self.alternate_elements = {
            '#renderNode': 'div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }


class RegistrationDashboardVerifier(Verifier):
    def __init__(self):
        super().__init__(410, RegistrationDashboardPage, "")
        self.loading_elements = {
            "#treeGrid > div > p": '#tb-tbody',  # Files list
            "#containment": "#render-node",  # Exists if there are supposed to be components / Is it filled?
        }
        self.alternate_elements = {
            '#nodeTitleEditable': '',  # Title
            '#contributors > div > p:nth-of-type(5) > span': '',  # Last modified
            '#contributorsList > ol': '',  # Contributor list
            '#logScope > div > div > div.panel-body > span > dl': '#logFeed > div > p'
            # Activity / "Unable to retrieve at this time"
        }

    # Override: the loader for loading_elements is still supposed to exist
    # Check that specified elements are supposed to exist and a loading bar isn't present instead
    # Check that specified elements or their alternates are present and non-empty in each page
    # Alternate: different elements appear if there isn't supposed to be content, so it has to check both
    # Format: Filled-in : Alternate
    def spot_check(self):
        for page in self.pages[:]:
            soup = page.get_content()
            # Existential crisis:
            for element in self.loading_elements:
                final_element = self.loading_elements[element]  # What is supposed to be there
                loading_bar_result = soup.select(element)
                if len(loading_bar_result) > 0:  # Container div is present
                    final_result = soup.select(final_element)
                    if len(final_result) == 0:  # Final element isn't in place
                        print("Failed: existential spot_check() ", page, final_element, " doesn't exist, loader ", element,
                              " present.")
                        self.failed_pages.append(page.url)
                        self.pages.remove(page)
                        break

            # Alternate checker:
            for element in self.alternate_elements:
                alt = self.alternate_elements[element]
                result = soup.select(element)
                # No results or empty results, with alternate
                if (len(result) == 0 or len(result[0].contents) == 0) and alt != '':
                    alt_result = soup.select(alt)

                    # Element's alternate has no or empty results
                    if len(alt_result) == 0 or len(alt_result[0].contents) == 0:
                        print("Failed: alternate spot_check(): ", page, alt, '\n')
                        self.failed_pages.append(page.url)
                        self.pages.remove(page)
                        break

                # Element has no alternate and no results or empty results
                elif (len(result) == 0 or len(result[0].contents) == 0) and alt == '':
                    print('Failed: spot_check(): ', page, element, "No alt.", '\n')
                    self.failed_pages.append(page.url)
                    self.pages.remove(page)
                    break
        return


class RegistrationFilesVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationFilesPage, "files/")
        self.alternate_elements = {
            '.fg-file-links': '',  # Links to files (names them)
        }


class RegistrationWikiVerifier(Verifier):
    def __init__(self):
        super().__init__(410, RegistrationWikiPage, "wiki/")
        self.alternate_elements = {
            '#wikiViewRender': '#wikiViewRender > p > em',  # Wiki content / `No wiki content`
            '#viewVersionSelect option': '',  # Current version date modified
            '.fg-file-links': ''  # Links to other pages (names them)
        }


class RegistrationAnalyticsVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationAnalyticsPage, "analytics/")
        self.alternate_elements = {
            '#adBlock': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # Warning about AdBlock
            'iframe': 'div.watermarked > div > div.m-b-md.p-md.osf-box-lt.box-round.text-center',
            # External frame for analytics
        }


class RegistrationForksVerifier(Verifier):
    def __init__(self):
        super().__init__(380, RegistrationForksPage, "forks/")
        self.alternate_elements = {
            '#renderNode': 'div.watermarked > div > div.row > div.col-xs-9.col-sm-8 > p'  # List
        }


class UserProfileVerifier(Verifier):
    def __init__(self):
        super().__init__(80, UserProfilePage, "")
        self.alternate_elements = {
            '#projects': 'div > div:nth-of-type(1) > div > div.panel-body > div',  # Project list / "No projects"
            '#components': 'div > div:nth-of-type(2) > div > div.panel-body > div',  # Component list / "No components"
            'body h2': ''  # Activity points, project count
        }


class InstitutionDashboardVerifier(Verifier):
    def __init__(self):
        super().__init__(350, InstitutionDashboardPage, "")
        self.loading_elements = {
            '#fileBrowser > div.db-main > div.line-loader > div.load-message': '.fg-file-links'  # "loading" / Project browser
        }
        self.alternate_elements = {
            '#fileBrowser > div.db-infobar > div > div': '#fileBrowser > div.db-infobar > div > div'  # Project preview / "Select a project"
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
    print("Called rescrape.")
    second_chance = Crawler()
    if json_filename['scrape_nodes']:
        second_chance.node_urls = verification_json_filename['node_urls_failed_verification']
        second_chance.scrape_nodes()
    if json_filename['scrape_registrations']:
        second_chance.registration_urls = verification_json_filename['registration_urls_failed_verification']
        second_chance.scrape_registrations()
    if json_filename['scrape_users']:
        second_chance.user_profile_page_urls = verification_json_filename['user_profile_page_urls_failed_verification']
        second_chance.scrape_users()
    if json_filename['scrape_institutions']:
        second_chance.institution_urls = verification_json_filename['institution_urls_failed_verification']
        second_chance.scrape_institutions()


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
            list_name = 'user_profile_page_urls'
        else:
            list_name = 'user_profile_page_urls_failed_verification'
        verification_json_dictionary['user_profile_page_urls_failed_verification'] = \
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
            print("Begun next run")
            setup_verification(run_copy, run_copy, False)
            # truncates json and dumps new lists
            with codecs.open(json_file, mode='w', encoding='utf-8') as file:
                json.dump(run_copy, file, indent=4)
            call_rescrape(run_copy, run_copy)


def main(json_filename, num_retries):
    # For testing:
    # num_retries = 2
    # call two verification/scraping methods depending on num retries
    run_verification(json_filename, num_retries)
