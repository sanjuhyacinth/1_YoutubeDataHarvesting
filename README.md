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

Firstly, we need an **API Key**. For that we need to create a project within the [Google Developer Console](https://developers.google.com/youtube/v3/getting-started), enable YouTube Data API and enable credentials to get the API key. Upon storing the key in a safe place, we can close this setup and open our code editor. Reference document for [YouTube API](https://developers.google.com/youtube/v3/docs) - This documentation gives idea about the kind of data we can retrieve by using the API key.

### 1. Python - VS Code editor:
We now open our code editor, and import the important packages mainly the **googleapiclient.discovery**, **mysql.connector** among many other. Upon doing this we now have to store our api key, and setup a variable to access YouTube data. We can refer to the code from the **YouTube API Reference document** provided above, but the code that is common for extracting all the data of channels, videos and comments is as below:

```python
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyCI3baVf9LEFjnttyIbvJAi2jMKfjoJRmc"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)
```
This will be our common code to retrieve all data.

### 2. Setting up Streamlit app:
Streamlit is a simple framework which works on python interfaces with an import, mainly used by non-web developers to deploy web apps. The simplicity and collection of functions/attributes makes it a much needed module in python for fellow data learners to display their insights and analysis of data in a web based app. Click [here](https://www.datacamp.com/tutorial/streamlit) to read more about the module.
Streamlit in python provides a variety of functions that help us enhance the display and presentation of our data. Some of the attributes used here are that for **Page title, sub headers, navigation pane, buttons that act upon a click, checkbox to choose items, etc..** The code to insert a user input is given below:

```python
channelid = st.text_input("Enter the Channel ID:")
```
This code allows the user to input a Channel ID for which they want to extract information about. Once this code is executed, the web app displays this line with a box below that allows user to input a Channel ID. This code is followed by the code to **place a request with the API to youtube to extract the particular channel details**

### 3. Retrieve & Store data :
#### Extract data:
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

``` python
{'channel_id': 'UC1H1S5yLiYDZ3I0P5_pIvUg',
 'channel_name': 'Gabriel Conte',
 'channel_des': '',
 'channel_pat': '2012-08-18T04:12:52Z',
 'channel_pid': 'UU1H1S5yLiYDZ3I0P5_pIvUg',
 'channel_sub': '1740000',
 'channel_vc': '100065038'}
```

 This result above is what the function produces. This is in the form of a python dictionary. In the same way, we have the functions and specific code to extract the video and comment data of the channels selected as well. Following that, we can retrieve and store data in the form of a python dictionary. 

 ### 3. Migrating data to SQL datawarehouse:
 The next concept we are tackling is how we can **store and generate results** from the data collected. Our target is to visually display all the data we have collected onto streamlit app. And in order to organise the data we have and display them in a good manner, we first need to store the data in a data waraehouse, prefereably in a SQL data warehouse like **MySQL workbench** In order to do that, we are connecting our **MySQL workbench to our python code editor** using the package **mysql connector** available for import in python. Once imported, we can use that as a function to store our MySQL connection credentials and use it while updating data to the database. 

#### a. Creation of tables:
 The first step here is to **create the tables** in the form we need using python into our SQL database. An example of what is done in our project is given by the function below:

 ```python
def function_name(cursor):
# Connect to MySQL
    conn = mysql.connector.connect(
    host="host_name",
    user="user_name",
    password="passcode",
    database="db_name"
)
    # Create cursor object
    cursor = conn.cursor()

    create_table = """
    CREATE TABLE IF NOT EXISTS table_1 (
        id VARCHAR(255),
        text TEXT,
        author VARCHAR(255),
        published_at DATETIME
    )
    """
    cursor.execute(create_table)
    conn.commit()
    conn.close()

# calling the function:
function_name(cursor)

```
So, we define tables for the 3 tables that we need: Channels, Videos and Comments for the particular channel IDs. Once created they can be called with the function for the tables to pop up in our database. 

#### b. Insertion of data into tables:
Secondly, once the tables are created, we need to create functions for the data to be imputed to those tables. For that, we will need to **insert data** into those tables. Hence we create **insert data functions** like how we did create table fucntion in python. What we did for create tables can be applied here, but only the insert data command of SQL has to be changed. An example is shown below

```python
insert_query = """
    INSERT INTO table_1 (
        id, text, author, published_at
    ) VALUES (%s, %s, %s, %s)
    """
```

Lastly, any data transformations in between, for example properly cleaning the published_at field can also be defined and called as a function to be applied on to the relevant data fields of the tables, while inserting the data itseld. All of these transformations relevant to properly displaying the data in streamlit are done in our code file.

### 4. Data display in Streamlit:
So, the process is straight forward. From the channel ID input; we have to take the input and based on the YouTube API fetch the channel, video and comment data of the respective channel, create relevant tables in SQL to store the same, inserting data retrieved onto those created tables upon required transformations and store it there. These are all done by using multiple functions. But what we want is to create a function that can do all of this in a click within streamlit! So, upon channel ID input we want to fetch data and migrate data to SQL. Let us look at how to do them below in the click of a button using the button parameter in streamlit.

#### a. Fetch Data:
We have a requirement to **show the relevant channel details** in a click. Upon defining the function for the same, we can use the st.button feature to display those details in the click of a button. Yes! this is possible with the excellence of Streamlit. So, within the st.button() we defined the button name, and below this treating it as a function we can give how the data should be represented or displayed using st.write() parameter. The code for the same is discussed in our python file

#### b. Data migrate function:
To go further, we need to be able to display the data in our database onto the Streamlit app created. For that, we will create a **migrate to SQL function** in python that uses all the data we have collected (through functions), and execute them all as a single function. Like how we did above, we should create a function that uses all the above functions we have created to make the data transfer to SQL in a single move. 

Upon doing so, we can set up a parameter (from the plethora of display attributes Streamlit has) st.button to execute this entire migration process from python to SQL in a single click. We will place this command and the fetch data below our user_input for channel ID. So, when a channel ID in given by the user, the two buttons will be available for use and when the user clicks this the data will be transfered to the database of choice. 

### 5. Querying the database from Streamlit
We have been given a few pre-defined queries that need to be displayed in streamlit. For this too we can create a function in python that will be triggered by a streamlit parameters. For this, we are about to display the queries and their solutions in a separate sub page in streamlit using the st.sidebar parameter to create a navigation pane and st.sidebar.radio to have access between multiple pages. The code is discussed in the python file.

### 6. Custom query window:
This is an additional feature created to query the data in the database for results other than the ones from the pre defined queries. At the moment, it accepts only minimum difficulty queries for data clarity sake. 

This is the end to our project on the display of Youtube Data using the YouTube data API, Python, SQL and Streamlit of course!
