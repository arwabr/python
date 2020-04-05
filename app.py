import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import matplotlib.pyplot as plt
import string
import folium
from geopy.geocoders import Nominatim

def get_tweets(fetched_tweets) :
    '''
    Main function to fetch tweets and parse them.
    '''
    # empty list to store parsed tweets
    tweets = []
# try
    try :
        # parsing tweets one by one
        for tweet in fetched_tweets :
            # empty dictionary to store required params of a tweet
            parsed_tweet = {}

            # saving text of tweet
            parsed_tweet['text'] = tweet.text
            # saving sentiment of tweet
            parsed_tweet['sentiment'] = get_tweet_sentiment(tweet.text)
            # saving location of the tweet
            parsed_tweet['location'] = tweet.author.location
            # saving the author name of the tweet
            parsed_tweet['authorName'] = tweet.author.name
            #  time when this Tweet was created
            parsed_tweet['dateCreation'] = tweet.created_at
            # polarity of tweet
            analysis = TextBlob(clean_tweet(tweet.text))
            parsed_tweet['polarity'] = analysis.sentiment.polarity


            # appending parsed tweet to tweets list
            if tweet.retweet_count > 0 :
                # if tweet has retweets, ensure that it is appended only once
                if parsed_tweet not in tweets :
                    tweets.append(parsed_tweet)
            else :
                tweets.append(parsed_tweet)

        # return parsed tweets
        return tweets

    except tweepy.TweepError as e :
        # print error (if any)
        print("Error : " + str(e))

def clean_tweet(tweet) :
    '''
    Remove unncessary things from the tweet
    like mentions, hashtags, URL links, punctuations
    '''
    # remove old style retweet text "RT"
    tweet = re.sub(r'^RT[\s]+', '', tweet)

    # remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)

    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r'#', '', tweet)

    # remove mentions
    tweet = re.sub(r'@[A-Za-z0-9]+', '', tweet)

    # remove punctuations like quote, exclamation sign, etc.
    # we replace them with a space
    tweet = re.sub(r'[' + string.punctuation + ']+', ' ', tweet)

    return tweet


def get_tweet_sentiment(tweet) :
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0 :
        return 'positive'
    elif analysis.sentiment.polarity == 0 :
        return 'neutral'
    else :
        return 'negative'




def score_tweets(tweets):
    '''
    Utility function to score the polarity of
    each category of tweets(positive , negative and neutral)
    '''
    total_p = 0
    for tweet in tweets:
        total_p = total_p + tweet['polarity']

    score = total_p/len(tweets)

    return abs(score)



def main() :
    # keys and tokens from the Twitter Dev Console
    consumer_key = '02HsaGIkRUvn0xvfrqjGdk6CH'
    consumer_secret = 'KweHAsasQnYEVGsbKKHlqTtGvji41vjB9GuAxy2bZMHCAJcrIM'
    access_token = '1059882917193760768-3aXnQr2C6GrHQIhBij5Fr8yBRkqR4G'
    access_secret = 'K725xoVjTGDTWOam7SG5xRJs6AI79neIE1ztog9Fy88hr'

    # attempt authentication
    try :
        # create OAuthHandler object
        auth = OAuthHandler(consumer_key, consumer_secret)
        # set access token and secret
        auth.set_access_token(access_token, access_secret)
        # create tweepy API object to fetch tweets
        api = tweepy.API(auth)
    except :
        print("Error: Authentication Failed")

    # call twitter api to fetch tweets

    fetched_tweets = tweepy.Cursor(api.search, q='HudaBeauty').items(100)
    # calling function to get tweets with attributes like text and the sentiment and the author name
    tweets = get_tweets(fetched_tweets)

    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    # percentage of positive tweets
    positive = (100 * len(ptweets) / len(tweets))

    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    # percentage of negative tweets
    negative = (100 * len(ntweets) / len(tweets))

    # picking neutral tweets from tweets
    netweets = [tweet for tweet in tweets if tweet['sentiment'] == 'neutral']
    # percentage of neutral tweets
    neutral = (100 * len(netweets) / len(tweets))
    print(neutral)

    totalPOS = 0
    totalNEG = 0
    totalNEU = 0

    # printing positive tweets
    print("\n\nPositive tweets:")
    for tweet in ptweets:
        totalPOS = totalPOS + 1
        print("")
        print(tweet['dateCreation'])
        print(tweet['location'])
        print(tweet['authorName'])
        print(tweet['text'])

    # printing negative tweets
    print("\n\nNegative tweets:")
    for tweet in ntweets:
        totalNEG = totalNEG + 1
        print("")
        print(tweet['dateCreation'])
        print(tweet['location'])
        print(tweet['authorName'])
        print(tweet['text'])

    # printing Neutral tweets
    print("\n\nNeutral tweets:")
    for tweet in netweets:
        totalNEU = totalNEU + 1
        print("")
        print(tweet['dateCreation'])
        print(tweet['location'])
        print(tweet['authorName'])
        print(tweet['text'])

    score_pos= score_tweets(ptweets)
    print("score des tweets positives : ",score_pos)
    score_neg = score_tweets(ntweets)
    print("score des tweets negatives : ", score_neg)

    # print graphe
    labels = 'negative', 'positive', 'neutral'
    sizes = [negative, positive, neutral]
    colors = ['red', 'green', 'blue']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')
    plt.savefig('championsL.png')
    plt.show()

    # print the map
    m = folium.Map()
    onmap = 0
    for tweet in tweets :
        try :
            adress = tweet['location']
            geolocator = Nominatim()
            locationn = geolocator.geocode(adress)
            lat = locationn.latitude
            lon = locationn.longitude
            print(lat,lon)
            if (tweet['sentiment'] == 'positive') :
                folium.Marker(
                    location=[lat, lon],
                    popup=str(tweet['polarity']),
                    icon=folium.Icon(color='green')
                ).add_to(m)
                onmap = onmap + 1
            if (tweet['sentiment'] == 'negative') :
                folium.Marker(
                    location=[lat, lon],
                    popup=str(tweet['polarity']),
                    icon=folium.Icon(color='red')
                ).add_to(m)
                onmap = onmap + 1
            if (tweet['sentiment'] == 'neutral') :
                folium.Marker(
                    location=[lat, lon],
                    popup=str(tweet['polarity']),
                    icon=folium.Icon(color='blue')
                ).add_to(m)
                onmap = onmap + 1
        except :
            print("No location found")
    m.save('map.html')


    print("total des tweets positive =", totalPOS)
    print("total des tweets negative =", totalNEG)
    print("total des tweets neutre =", totalNEU)
    print("tweets on map =", onmap)


if __name__ == "__main__" :
    # calling main function
    main()
