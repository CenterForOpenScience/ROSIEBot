#
# # Access point for identifying problems and correcting them
# # It is possible to only log issues, not correct them.
#

# This import clears the logs prior to relogging
import Verification.Logs.reset_logs
import Verification.spot_check as identify
import Verification.retry_scrape as correct

# # Identify problems
# This area uses internal, memory-persistent lists of files passed between
# This area uses an external, memory-persistent list of failed files to pass into the retry mechanism
# Process chain: initialize_list -> size_comparison -> spot_check

project_dashboard = identify.ProjectDashboard()
project_files = identify.ProjectFiles()
project_wiki = identify.ProjectWiki()
# project_analytics = identify.ProjectAnalytics()
project_registrations = identify.ProjectRegistrations()
project_forks = identify.ProjectForks()

registration_dashboard = identify.RegistrationDashboard()
registration_files = identify.RegistrationFiles()
registration_wiki = identify.RegistrationWiki()
# registration_analytics = identify.RegistrationAnalytics()
registration_forks = identify.RegistrationForks()

user_profile = identify.UserProfile()
institution_profile = identify.InstitutionProfile()

# # Correct problems
# This area is passed the memory-persistent list of failed files from the final step of identify (spot_check)
# Process chain: retry_scrape
new_rosie = correct.Rescraper()
new_rosie.scrape()
