"""
Site regional settings and timezone-aware scheduling.

Fetches the web's regional settings, prints a readable summary, then uses the
site's configured time zone to convert a local time to UTC - useful when
scheduling recurring jobs against a site in another time zone.

See https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/site-operations
"""

import argparse
from datetime import datetime

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Show a web's regional settings and convert a local time to UTC")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    args = parser.parse_args()

    client = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    settings = client.web.regional_settings.get().execute_query()
    print(f"Locale: {settings.locale_id}")
    print(f"Date separator: {settings.date_separator}   decimal: {settings.decimal_separator}")
    print(f"First day of week: {settings.first_day_of_week}   work days mask: {settings.work_days}")
    print(f"Installed languages: {len(settings.installed_languages.get().execute_query())}")

    tz = settings.time_zone.get().execute_query()
    print(f"Time zone: {tz.description} (id={tz.id})")

    local = datetime.now()  # current local site time
    result = tz.local_time_to_utc(local).execute_query()
    print(f"{local} local -> {result.value} UTC")


if __name__ == "__main__":
    main()
