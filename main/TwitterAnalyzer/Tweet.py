class Tweet:
    def __init__(self, text="", post_id="",user_name="",postDate="", hashtags=[],mentions=[],favourite_count=0,retweet_count=0,is_retweet="false"):
        self.text = text
        self.post_id = post_id
        self.user_name = user_name
        self.post_date = postDate
        self.hashtags = hashtags
        self.mentions = mentions
        self.retweet_count = retweet_count
        self.favourite_count = favourite_count
        self.is_retweet = is_retweet

