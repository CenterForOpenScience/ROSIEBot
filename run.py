#
# # Execution of crawler
#
from crawler import Crawler
from settings import limit

rosie = Crawler()
#
# # Get URLs from API and add them to the async tasks
rosie.crawl_nodes_api(page_limit=5)
rosie.crawl_wiki()
rosie.generate_node_urls(all_pages=True)
rosie.scrape_nodes(async=True)

rosie.crawl_registrations_api(page_limit=limit)

rosie.crawl_users_api(page_limit=limit)
rosie.crawl_institutions_api(page_limit=limit)

#
# # Scrape the URLs found by crawling mechanisms
#
rosie.scrape_nodes()

print("Mirror complete. \nOptional:\tRun verification testing suite.")
