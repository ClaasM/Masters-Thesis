"""
Computes the features used to classify whether or not the videos on a hosts website are relevant.
The columns for whether the host's videos from a specific platform are deemed relevant are created but filled at a later point.

Features per host and per platform (facebook, twitter, youtube):
- std_dev: Standard deviation in the number of videos per article
- count: Number of articles with 1+ video
- sum: Total number of videos across all articles
- sum_distinct: Total number of distinct videos across all articles

Features per host:
- article_count: The number of articles from that host, including those that don't contain videos

Features that can easily be computed from these features, thus are not calculated yet:
- Average: Average number of videos per article, including articles without videos
- Average distinct videos per article
- Distinct videos to total videos
- ...

See the Host Classifier Notebook for plots of these features and to see how the model is built.

"""
import numpy as np
import psycopg2
from itertools import groupby
from src.data.postgres import postgres_helper
from src.visualization.console import StatusVisualization


def run():
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    c.execute("SELECT * FROM sources LIMIT 1")
    # We're only interested in hosts that had any video etc. in them
    c.execute('SELECT source_name FROM sources')
    sources = c.fetchall()

    progress = StatusVisualization(total_count=len(sources), update_every=1000)
    for source in sources:
        source = source[0]
        features = dict()
        # article_count is already computed in when the db is populated

        for platform in ["twitter", "youtube", "facebook"]:
            # Get all videos from that source, of that platform:
            c.execute('SELECT video_url FROM article_videos WHERE source_name=%s AND platform=%s', [source, platform])
            videos = c.fetchall()

            # Get the count of each article
            c.execute('SELECT Count(1) FROM article_videos WHERE source_name=%s AND platform=%s GROUP BY source_url',
                      [source, platform])
            video_counts = c.fetchall()

            features[platform + "_std_dev"] = np.std(video_counts) if len(video_counts) > 0 else -1
            features[platform + "_count"] = len(video_counts)
            features[platform + "_sum"] = len(videos)
            features[platform + "_sum_distinct"] = len(set(videos))

        query = "UPDATE sources SET %s WHERE source_name=\'%s\'" % (postgres_helper.dict_set_string(features), source)
        c.execute(query)
        conn.commit()
        progress.inc()


if __name__ == "__main__":
    run()
