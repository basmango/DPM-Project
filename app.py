import tweepy
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from textblob import TextBlob, Word, Blobber
import pandas as pd
import numpy as np
import re #regular expressions
from flask import Flask
from flask import request
from flask import render_template
from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.embed import components
from bokeh.plotting import figure, show
from bokeh.io import output_notebook, output_file,show
# import datetime
app = Flask(__name__)

@app.route('/',methods = ['GET','POST'])
def index():
    name1 = "Virat"
    
    if request.method == 'GET':
        
        p = figure(width=700, height=400)
        p.background_fill_color = "seagreen"
        p.background_fill_alpha = 0.6
        # p = figure(x_range=(0, 1), y_range=(0, 1))
        p.image_url(url=['https://miro.medium.com/max/1200/1*PKXC0FeXQc5LVmqhJ8HnVg.png'], x=0, y=1, w=0.8, h=0.6)
        # p.hbar(y=[1, 2, 3], height=0.5, left=0,
        #         right=[1.5, 2, 3], color="seagreen")
        demo_script_code,chart_code = components(p)
        return render_template('view.html',Person_name = name1,chart_code = chart_code,demo_script_code = demo_script_code)
    elif request.method =='POST':
        print("post request made")
        name = request.form['p_name']
        print(name)
        # Date_b = request.form['begdate']
        # Date_e = request.form['enddate']
        # Period = request.form['freq']
        # Amount = request.form['amt']
        # if name == "anup":
        #     lst = ["2007-11-23", "2008-11-23","2010-11-23","2012-11-23"]
        #     temp = ["Not Prime", "Prime", "Prime", "Prime"]
        #     res = [200, 300, 250, 580]
            
        #     dict1 = {"Date": lst, "Units":temp, "Wealth":res}
        #     dict1 = pd.DataFrame(dict1)
        #     print(dict1)
        #     p = figure(width = 700, height = 500, x_axis_type = "datetime",x_axis_label = "Years", y_axis_label = "Wealth")
        #     dict1["Date"] = pd.to_datetime(dict1["Date"])
        #     p.line(dict1["Date"],dict1["Wealth"], line_width=2)
        A_Key="V2MKVagJ7FHniRjtZ6hv1nOx3"
        A_Key_Secret="Wza1nJO6oSAhUryZ68arQDMvEPh3GbhcpBn9kqPHl30uw9gRw9"
        A_Token = "1435660546930475012-fzLwcYBUzeqU4Q29T12mc9JHkn4XgS"
        A_Token_Secret = "c7Sl327JDfIZkHw8s3LENFgH77tKcutM9lcG3m59C9Cxh"

        auth = tweepy.OAuthHandler(A_Key,A_Key_Secret)
        auth.set_access_token(A_Token,A_Token_Secret)
        api = tweepy.API(auth)

        def get_tweetsdf(topic):
            tweetList = []
            userList = []
            likesList = []
            datetimeList = []
            locationList = []

            cursor = tweepy.Cursor(api.search_tweets,q = topic,lang = "en",tweet_mode = "extended",exclude="retweets").items(150)
            for t in cursor:
                tweetList.append(t.full_text)
                userList.append(t.user.name)
                likesList.append(t.favorite_count)
                locationList.append(t.user.location)
                datetimeList.append(t.created_at)
        
            df =  pd.DataFrame({"User Name":userList,"Tweets":tweetList,"Likes":likesList,
                            "Date Time":datetimeList,"Location":locationList })
            return df

        #sentiment_analysis using TextBlob
        def sentiment_analysis(df):
            def getSubjectivity(text):
                return TextBlob(text).sentiment.subjectivity #subjectivity  =1 (personal opinion) =0(factual point)
        
        #Create a function to get the polarity
            def getPolarity(text):
                return TextBlob(text).sentiment.polarity #polarity lies [-1,1]
        
        #Create two new columns ‘Subjectivity’ & ‘Polarity’
            df["Subjectivity"] =    df["Clean Tweets"].apply(getSubjectivity)
            df["Polarity"] = df["Clean Tweets"].apply(getPolarity)
            def getAnalysis(score):
                if score <= -0.1:
                    return "negative"
                elif score > -0.1 and score < 0.1:
                    return "neutral"
                else:
                    return "positive"
            df["Polarity Analysis"] = df["Polarity"].apply(getAnalysis )
            return df

        def get_polarity_dataframe(df):
        #Section 1
            tempdf = df
            x = tempdf["Tweets"]

            nltk.download('stopwords') #to remove stop words(a,an the)
        
            stop_words=stopwords.words('english') # to get stem of verb(playing->play)
            stemmer=PorterStemmer()

            cleaned_text=[]
            for i in range(len(x)):
                tweet=re.sub('[^a-zA-Z]',' ',x.iloc[i]) #substitute empty string where char is not a-zA-Z
                tweet=tweet.lower().split()

                tweet=[stemmer.stem(word) for word in tweet if (word not in stop_words)] #stemming and remove stop words
                tweet=' '.join(tweet)
                cleaned_text.append(tweet)

            tempdf["Clean Tweets"] = cleaned_text

        #Section2
            newdf = sentiment_analysis(tempdf)
            return newdf

        def get_polarity_plot(topic):
        #get dataframe from topic
            df1 = get_tweetsdf(topic=topic)

        #get dataframe with polarity columns
            newdf = get_polarity_dataframe(df1)

            posNumber = newdf[newdf["Polarity Analysis"]=="positive"].shape[0]
            negNumber = newdf[newdf["Polarity Analysis"]=="negative"].shape[0]
            neuNumber = newdf[newdf["Polarity Analysis"]=="neutral"].shape[0]

            sentiments = ["Positive","Negative","Neutral"]
            counts = [posNumber, negNumber, neuNumber]
            total = posNumber + negNumber + neuNumber
        #print(counts)

            # output_file("plot.html")

            source = ColumnDataSource(data=dict(sentiments = sentiments, counts=counts, color=Spectral6))

            p = figure( x_range = sentiments, title=f"Sentiments Plot for latest {total} tweets",
                toolbar_location=None, tools="",x_axis_label = "Sentiments", y_axis_label = "Tweets Count") #x_range=sentiments, y_range=(0,9),

            p.vbar(x='sentiments', top='counts', width=0.8, color='color',  source=source)#legend_field="sentiments",

            p.xgrid.grid_line_color = None
        # p.legend.orientation = "horizontal"
            p.title.align = "center"
        # p.legend.location = "top_center"

            # show(p)

            return p

        p1 = get_polarity_plot(str(name))
        demo_script_code,chart_code = components(p1)
        return render_template('view.html',Person_name = name1,chart_code = chart_code,demo_script_code = demo_script_code)
if __name__ == "__main__":
    app.run(debug=True)
