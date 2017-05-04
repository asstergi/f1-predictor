# -*- coding: utf-8 -*-
"""
Created on Thu Jan 13 15:25:01 2017

@author: asterios
"""

from twitter.stream import TwitterStream, Timeout, HeartbeatTimeout, Hangup
from twitter.oauth import OAuth
from twitter.util import printNicely

import time
import pandas as pd
import os
import datetime
from retrying import retry
import ConfigParser
import logging

EXPORT_PATH = '/home/ec2-user/f1twitter/'

def get_auth():
    config_file_name = EXPORT_PATH + 'credentials - f1.ini'
    Config = ConfigParser.ConfigParser()
    Config.read(config_file_name)

    print Config.get("credentials", "consumer_key")

    auth = OAuth(
        consumer_key = Config.get("credentials", "consumer_key"),
        consumer_secret = Config.get("credentials", "consumer_secret"),
        token = Config.get("credentials", "token"),
        token_secret = Config.get("credentials", "token_secret")
    )

    return auth

def ConnectAndGetStream(stream_args, query_args, logger):

    print "Connecting to Twitter Streaming API..."
    logger.debug("Connecting to Twitter Streaming API...")
    auth = get_auth()
    twitter_stream = TwitterStream(auth=auth)
    try:
        tweet_iter = twitter_stream.statuses.filter(**query_args)
        print "Connected..."
        logger.debug("Connected...")
    except Exception as e:
        print "Error: " + str(e)[20:23]
        logger.debug("Error: " + str(e)[20:23])

    return tweet_iter

def saveTweets(tweet_lst, filename):
    #If file exists, open it, append new data and save again
    print "Saving tweets to " + filename + "..."
    logger.debug("Saving tweets to " + filename + "...")
    if os.path.exists(filename):
        print "File exists..."
        logger.debug("File exists...")
        try:
            existing = pd.read_csv(filename, encoding='utf-8')
        except:
            existing = pd.read_csv(filename, encoding='utf-8', engine='python')
        print existing.shape
        tweet_pd = pd.DataFrame.from_dict(tweet_lst)
        tweet_pd = pd.concat([existing, tweet_pd])
        tweet_pd.to_csv(filename, index=False, encoding='utf-8')
        print tweet_pd.shape
    else:
        print "File does not exist..."
        logger.debug("File does not exist...")
        tweet_pd = pd.DataFrame.from_dict(tweet_lst)
        tweet_pd.to_csv(filename, index=False, encoding='utf-8')


def StopIfLate(stop_at, case='', logger=''):
    now = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
    then = datetime.datetime.strptime(stop_at, "%Y-%m-%d %H:%M:%S")
    diff = now - then
    diff_minutes = (diff.days * 24 * 60) + (diff.seconds/60)

    if diff_minutes>=0:
        if case=='':
            print "Collection time has finished. Stopping collecting tweets."
            logger.debug("Collection time has finished. Stopping collecting tweets.")
        else:
            print "Time has ended. Stopping trying to collect tweets."
            logger.debug("Time has ended. Stopping trying to collect tweets.")
        return True
    else:
        return False

def getStream(tweet_iter, filename, stop_at, logger):

    print "Will stop collecting data at " + stop_at
    logger.debug("Will stop collecting data at " + stop_at)

    count = 0
    count_all = 0
    tweet_lst = []
    # Iterate over the stream
    for tweet in tweet_iter:
        tweet_dict={}

        if tweet is None:
            if count>0:
                saveTweets(tweet_lst, filename=filename)
            print "-- None --"
            logger.debug("-- None --")
            raise Exception("-- None --")
        elif tweet is Timeout:
            if count>0:
                saveTweets(tweet_lst, filename=filename)
            print "-- Timeout --"
            logger.debug("-- Timeout --")
            raise Exception("-- Timeout --")
        elif tweet is HeartbeatTimeout:
            if count>0:
                saveTweets(tweet_lst, filename=filename)
            print "-- Heartbeat Timeout --"
            logger.debug("-- Heartbeat Timeout --")
            raise Exception("-- Heartbeat Timeout --")
        elif tweet is Hangup:
            if count>0:
                saveTweets(tweet_lst, filename=filename)
            print "-- Hangup --"
            logger.debug("-- Hangup --")
            raise Exception("-- Hangup --")
        elif tweet.get('text'):
            count += 1
            count_all += 1

            tweet_dict['text'] = tweet['text'].encode('utf8')
            tweet_dict['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(tweet['timestamp_ms'])/1000))
            tweet_dict['created_at'] = tweet['created_at']
            tweet_dict['lang'] = tweet['lang']

            tweet_dict['followers_count'] = tweet['user']['followers_count']
            tweet_dict['friends_count'] = tweet['user']['friends_count']
            tweet_dict['location'] = tweet['user']['location']
            tweet_dict['name'] = tweet['user']['name']
            tweet_dict['retweeted'] = tweet['retweeted']

            tweet_lst.append(tweet_dict)
        else:
            if count>0:
                saveTweets(tweet_lst, filename=filename)
            printNicely("-- Some data: " + str(tweet))
            logger.debug("-- Some data: " + str(tweet))
            raise Exception("-- Some data --")

        if count==20:
            print count_all
            logger.debug(count_all)
            saveTweets(tweet_lst, filename=filename)
            count = 0
            tweet_lst = []

        if StopIfLate(stop_at = stop_at):
            print count_all
            saveTweets(tweet_lst, filename=filename)
            return False

@retry(wait_exponential_multiplier=1000, wait_exponential_max=600000)
def runPipeline(tracked_hashtags, stop_at, logger):

    print "Started tracking: " + tracked_hashtags
    logger.debug("Started tracking: " + tracked_hashtags)

    stream_args = dict(
            timeout=90,
            heartbeat_timeout=90)

    query_args = dict()
    query_args['track'] = tracked_hashtags

    #Code to stop process when cannot connect to API and keeps trying forever
    if StopIfLate(stop_at = stop_at, case='error', logger=logger):
        return

    today = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
    weekNum = datetime.datetime.strftime(today,'%W')
    year = datetime.datetime.strftime(today,'%Y')
    filename = EXPORT_PATH + 'F1_tweets_W' + weekNum + '_' + year + '_sched.csv'

    tweet_iter = ConnectAndGetStream(stream_args, query_args, logger=logger)
    cond = getStream(tweet_iter, filename, stop_at = stop_at, logger=logger)

    if cond==False:
        return


if __name__ == "__main__":
    #=================================
    #======Create Logger==============
    #=================================
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    handler = logging.FileHandler(EXPORT_PATH + 'logfile.log')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter.converter = time.gmtime
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    tracked_hashtags = '#f1, #formula1, @lewishamilton, @valtteribottas, @danielricciardo, @max33verstappen, @schecoperez, @oconesteban, @massafelipe19, @lance_stroll, @alo_oficial, @svandoorne, @dany_kvyat, @Carlossainz55, @rgrosjean, @kevinmagnussen, @nicohulkenberg, @jolyonpalmer, @ericsson_marcus, @pwehrlein, @mercedesamgf1, @redbullracing, @scuderiaferrari, @forceindiaf1, @williamsracing, @mclarenf1, @tororossospy, @haasf1team, @renaultsportf1, @sauberf1team'
    logger.debug(tracked_hashtags)

    print str(datetime.datetime.fromtimestamp(time.mktime(time.gmtime())))

    #Stop tomorrow at 04:00 AM GMT
    stop_at = datetime.datetime.fromtimestamp(time.mktime(time.gmtime())) + datetime.timedelta(days=1)
    stop_at = stop_at.replace(hour=04, minute=00, second=0)
    stop_at = stop_at.strftime("%Y-%m-%d %H:%M:%S")

    runPipeline(tracked_hashtags = tracked_hashtags, stop_at = stop_at, logger=logger) #'#f1, f1'

    logger.debug("##########################")
    logger.removeHandler(handler)
    handler.close()
    logging.shutdown()