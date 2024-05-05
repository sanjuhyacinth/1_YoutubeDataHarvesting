# GUVI
This repository is specifically created for the purpose of showcasing my Data Science Capstone Projects done during my course at GUVI

# Project 1 - Youtube  Data Harvesting and Warehousing using SQL and Streamlit
## What is the project about?
This particular social media project is about retreiving the data of specific YouTube channels that we want using the **Youtube API**. 

## Problem Statement:
The problem statement involves users to be able to retrieve data from YouTube, analyse them and store them in databases and dislpay them using the **streamlit** application.
For this project the softwares used include python, SQL database, streamlit web app.

In order to execute the project well, we have to be
- Able to extract the channel, video and comment data of users using the Youtube API in python code editor.
- Able to collect the relevant details from the data that's retrievable.
- Able to migrate and store the data in a systematic way in a SQL database.
- Able to query the stored data in the streamlit app created with the streamlit package in python.

## Project Approach:
In the next few lines we will discuss the approach used in the project.

### 1. Data retrieval:
We can enable this Youtube API from the [Google developer console](https://developers.google.com/youtube/v3/getting-started). We have to create a project and enable the Youtube API to get the **API Key** for connecting Youtube to our code editor, whcih is python in this case. Upon storing the key in a safe place, we can close this setup and open our code editor.

Reference document for [YouTube API](https://developers.google.com/youtube/v3/docs) - This documentation gives idea about the kind of data we can retrieve by using the API key.

### 2. Python - VS Code editor:
We now open our code editor, and import the important packages mainly the **googleapiclient.discovery**, **mysql.connector** among many other. Upon doing this we now have to store our api key, and setup a variable to access YouTube data. We can refer to the code from the **YouTube API Reference document** provided above, but the code that is common for extracting all the data of channels, videos and comments is as below:

```python
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyCI3baVf9LEFjnttyIbvJAi2jMKfjoJRmc"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
```
This will be our common code to retrieve all data.

#### Extracting data of channels:
In the documentation, in the left panel, we have a channels section below which as a sub category we have lists. This page will allow us to access the API explorer portion having the parameters and filters that we can manipulate to getting the data. There are languages to choose from to get the code in that langauage. Our code is in python and hence our code block to **request** and get **response** in python is as follows:

```python
request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id="channel_id"
)
response_ch = request.execute()
```
In the above code, the **part** is the parameter that allows us to choose from the various data points that can be retrived. For us, the snippet part gives us data on the channel name, ID, etc.. and so on for the other parts. We are getting the data based on the id filter which the channel ID we get from Youtube. This will make a request to Youtube to retrieve the asked data pieces for the particular channel ID we mention and store that in the variable response. Now the response variable has the data of the channel in a json format which has to be sliced to store particular information.

#### Storing Channel, video and comment data:
To store only the required data, we need to define funtions that allow us to access them all and store them efficiently. The codes for the same are mentioned inthe code file. For example the code to store the channel data is given below:

```python
# Defining a function to take all the above details for all the channel IDs passed.
def channel_data(c_id):
    request = youtube.channels().list(
    part="snippet, contentDetails, statistics", 
    id= c_id
    )
    response_ch = request.execute()
    data = {"channel_id" : response_ch['items'][0]['id'],
            "channel_name": response_ch['items'][0]['snippet']['title'],
            "channel_des": response_ch['items'][0]['snippet']['description'],
            "channel_pat" :response_ch['items'][0]['snippet']['publishedAt'],
            "channel_pid": response_ch['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
            "channel_sub": response_ch['items'][0]['statistics']['subscriberCount'],
            "channel_vc": response_ch['items'][0]['statistics']['viewCount']
    }
    return data
```
This will store all the data in the function channel_data. By giving a channel ID to the function, we can retrieve the data of that channel in this above format.

{'channel_id': 'UC1H1S5yLiYDZ3I0P5_pIvUg',
 'channel_name': 'Gabriel Conte',
 'channel_des': '',
 'channel_pat': '2012-08-18T04:12:52Z',
 'channel_pid': 'UU1H1S5yLiYDZ3I0P5_pIvUg',
 'channel_sub': '1740000',
 'channel_vc': '100065038'}

 This result above is what the function produces. This is in the form of a python dictionary.

 ### 3. Data Storage:
