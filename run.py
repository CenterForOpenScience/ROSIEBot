#
# # Execution of crawler
#
from crawler import Crawler

rosie = Crawler()
#
# # Get URLs from API and add them to the async tasks
# rosie.scrape_diff()
rosie.crawl_nodes_api(page_limit=5)
rosie.crawl_node_wiki()
rosie.generate_node_urls(all_pages=True)
rosie.scrape_nodes(async=True)

rosie.crawl_registrations_api(page_limit=5)

rosie.crawl_users_api(page_limit=5)
rosie.crawl_institutions_api(page_limit=5)

#
# # Scrape the URLs found by crawling mechanisms
#
rosie.scrape_nodes()
rosie.scrape_institutions()
rosie.scrape_users()
rosie.scrape_registrations()

print("Mirror complete. \nOptional:\tRun verification testing suite.")
