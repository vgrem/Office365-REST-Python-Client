from settings import settings

from office365.runtime.auth.clientCredential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.search.administration.documentCrawlLog import DocumentCrawlLog

ctx = ClientContext.connect_with_credentials(settings['url'],
                                             ClientCredential(settings['client_credentials']['client_id'],
                                                              settings['client_credentials']['client_secret']))

crawl_log = DocumentCrawlLog(ctx.site)
ctx.load(crawl_log)
ctx.execute_query()
