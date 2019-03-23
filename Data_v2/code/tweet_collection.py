import json
import logging
from multiprocessing.pool import Pool

from Data_v2.code.util.TwythonConnector import TwythonConnector
from Data_v2.code.util.util import create_dir, Config, multiprocess_data_collection
from tqdm import tqdm


class Tweet:

    def __init__(self, tweet_id, news_id, news_source, label):
        self.tweet_id = tweet_id
        self.news_id = news_id
        self.news_source = news_source
        self.label = label


def dump_tweet_information(tweet: Tweet, config: Config, twython_connector: TwythonConnector):
    try:
        tweet_object = twython_connector.get_twython_connection(Constants.GET_TWEET).show_status(id=tweet.tweet_id)

        if tweet_object:
            dump_dir = "{}/{}/{}/{}".format(config.dump_location, tweet.news_source, tweet.label, tweet.news_id)
            tweet_dir = "{}/tweets".format(dump_dir)
            create_dir(dump_dir)
            create_dir(tweet_dir)

            json.dump(tweet_object, open("{}/{}.json".format(tweet_dir, tweet.tweet_id), "w"))

    except TwythonRateLimitError:
        logging.exception("Twython API rate limit exception")

    except:
        logging.exception("exception in collecting tweet objects")

    return None


def collect_tweets(news_list, news_source, label, config: Config):
    create_dir(config.dump_location)
    create_dir("{}/{}".format(config.dump_location, news_source))
    create_dir("{}/{}/{}".format(config.dump_location, news_source, label))

    save_dir = "{}/{}/{}".format(config.dump_location, news_source, label)

    twython_connector = None
    tweet_id_list = []

    for news in news_list:
        for tweet_id in news.tweet_ids:
            tweet_id_list.append(Tweet(tweet_id, news.news_id, news_source, label))

    multiprocess_data_collection(dump_tweet_information, tweet_id_list, (config, twython_connector), config)
