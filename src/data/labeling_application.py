"""
A small command line tool to make the labeling of relevancy of a a video for a certain topic easier.
TODO print introduction or something
"""

import psycopg2
from random import shuffle

from src.visualization import console

if __name__ == "__main__":
    conn = psycopg2.connect(database="thesis", user="postgres")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS labeled_hosts (
                  hostname TEXT,
                  youtube_relevant INTEGER,
                  twitter_relevant INTEGER,
                  facebook_relevant INTEGER)''')
    conn.commit()

    # Create a cursor for every host that hasn't been labeled yet.
    c.execute(
        '''SELECT hosts.hostname FROM hosts LEFT JOIN labeled_hosts  ON labeled_hosts.hostname = hosts.hostname WHERE labeled_hosts.hostname IS NULL''')
    hostnames = c.fetchall()
    shuffle(hostnames)

    for hostname in hostnames:
        hostname = hostname[0]
        c.execute('''SELECT found_videos.website_url, found_videos.platform FROM found_videos WHERE hostname=%s''',
                  [hostname])
        found_videos = c.fetchall()
        articles = dict()
        found_platforms = set()
        for url, platform in found_videos:
            if url not in articles:
                articles[url] = {"twitter": 0, "facebook": 0, "youtube": 0}
            articles[url][platform] += 1
            found_platforms.add(platform)

        table_printer = console.TablePrinter(["twitter", "facebook", "youtube", "URL"])
        for url in articles.keys():
            counts = articles[url]
            table_printer.print_row([counts["twitter"], counts["facebook"], counts["youtube"], url])

        print()
        twitter_relevance = input(
            "Are the host's TWITTER tweets relevant? (1: yes, 2: No (e.g. in sidebar), 3: No (user-created)) ") if "twitter" in found_platforms else -1
        facebook_relevance = input(
            "Are the host's FACEBOOK videos relevant? (1: yes, 2: No (e.g. in sidebar), 3: No (user-created)) ") if "facebook" in found_platforms else -1
        youtube_relevance = input(
            "Are the host's YOUTUBE videos relevant? (1: yes, 2: No (e.g. in sidebar), 3: No (user-created)) ") if "youtube" in found_platforms else -1

        c.execute(
            '''INSERT INTO labeled_hosts (hostname, youtube_relevant, twitter_relevant, facebook_relevant) VALUES (%s, %s, %s, %s)''',
            [hostname, youtube_relevance, twitter_relevance, facebook_relevance])
        conn.commit()
        print()
