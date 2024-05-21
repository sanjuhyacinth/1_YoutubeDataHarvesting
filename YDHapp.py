
# essential library installations
import streamlit as st
from streamlit_option_menu import option_menu
import googleapiclient.discovery
import mysql.connector
from datetime import datetime
import pandas as pd

# set up page layout for the app:
st.set_page_config(page_title="YouTube Data app", layout="wide", initial_sidebar_state="expanded")

# Creating a side navigation bar:
with st.sidebar:
    selected = option_menu("Content", ["Home","Data Collection & Migration","Pre-defined SQL Queries","Custom SQL Queries"],
                           default_index=0,
                           orientation="vertical")

# Home - landing page contents:
if selected == "Home":
    # Title
    st.title(':blue[YouTube Data Harvesting and Warehousing using SQL and STREAMLIT]')
    st.markdown("### :white_check_mark: Domain :") 
    st.write('This project falls under the Social Media domain')
    st.markdown("### :white_check_mark: Project overview :")
    st.markdown(''' This project aims for us to create a simple **Streamlit app** using Python to display 
                channel, video, playlist and comments data retrieved from YouTube with the help of the YouTube API, 
                stored in MySQL and then displayed on the streamlit app. The app also needs to provision for SQL database
                querying and displays results so as to give inferences on the channels chosen. ''')
    st.markdown("### :white_check_mark: Skills take away From This Project :") 
    st.markdown("API integration, Python, MySQL, Streamlit")
    st.markdown("### :pencil2: Developed by :") 
    st.markdown("Sanju Hyacinth")
    st.subheader(':envelope_with_arrow: Contact:')
    st.markdown('##### Linkedin: www.linkedin.com/in/sanju-hyacinth/')
    st.markdown('##### GitHub : https://github.com/sanjuhyacinth')

elif selected == "Data Collection & Migration":
    st.markdown('### :blue[Data extraction area :]')
    st.markdown(''' In this space, we are going to be **collecting the specific channel, playlist, video and comment data**
                of the channels that the user provides as input and migrate them to our dedicated MySQL database. 
                We can obtain this by going to the channel on Youtube, click the :blue[About section], click the :blue[Share Channel] 
                and select :blue[Copy channel ID].''')
    st.markdown('''
                - Step 1: **Input Channel ID :** Insert the channel ID of the desired channel in the text box below. 
                - Step 2: **Extract :** Click on the **Fetch data** button below the box for the data extraction from YouTube for the channel.
                ''')
    st.markdown("Let's go!")

    # api details:
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "api_key"
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)


    # Text input for YouTube channel ID
    channelid = st.text_input("Enter the Channel ID:") 

    # Getting Channel details:
    # Defining a function to take all the above details for all the channel IDs passed.
    def fetch_channel_details(channelid):
        if channelid:
            request = youtube.channels().list(
            part="snippet, contentDetails, statistics",  
            id= channelid
            )
            response_ch = request.execute()
            details = {"channel_id" : response_ch['items'][0]['id'],
                    "channel_name": response_ch['items'][0]['snippet']['title'],
                    "channel_des": response_ch['items'][0]['snippet']['description'],
                    "channel_pat" :response_ch['items'][0]['snippet']['publishedAt'],
                    "channel_pid": response_ch['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
                    "channel_sub": response_ch['items'][0]['statistics']['subscriberCount'],
                    "channel_vc": response_ch['items'][0]['statistics']['viewCount']
            }
            return details
        if not channelid:
            st.warning("Please enter a valid YouTube Channel ID before proceeding.")

    channel_data = fetch_channel_details(channelid)
    ##############################################################################################################

    # Getting video IDs from Channel ID:

    # Getting all the video IDs from a channel:
    # define a function with channel ID as input and return value as all video IDs for ease.
    def extract_vids(channelid):
        if channelid:
            # Process to get the playlist ID we extracted from the channel details:
            request = youtube.channels().list(
            part="contentDetails",
            id= channelid
            )
            response = request.execute()
            PlaylistID = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            # We will have cases where the video counts get more than 50. 
            # In that case we have a parameter called pageToken that can fetch IDs from all pages in the channel.
            #let's execute a while loop to execute the above process until false.

            # video ID empty list to store:
            vIDS = []
            # by default the value is None for videos that are not more than 50
            next_page_token = None 
            # here we add our parameter in the while loop:
            while True:
                request_v = youtube.playlistItems().list(part="snippet",
                                                        maxResults=50,
                                                        playlistId=PlaylistID,
                                                        pageToken=next_page_token)
                response_v = request_v.execute()

                # listing all the video IDs in a separate list by creating a for loop
                # ids value changes with each video and the loop iterates through all.
                for ids in range(len(response_v['items'])):
                    vIDS.append(response_v['items'][ids]['snippet']['resourceId']['videoId'])
                
                # once the loop completes 1 page of 50 videos and if more, 
                # the next page token value is changed as below for the code to run again from while
                next_page_token=response_v.get('nextPageToken')

                # once again when no more videos are there, the next page token automatically becomes None
                # when that happens, the if command runs below and the while loop turns false and process ends.
                if next_page_token is None:
                    break
            return vIDS

    ##############################################################################################################
    # Now let's print the result of the above function by inputing the channel ID
    videosIDS=extract_vids(channelid)
    # len(videosIDS)

    # Video details from Video IDS:
    # Nested for loop: for each video ID we need a few details, and for that we use a loop within a loop

    # define a function to get details of every video id mentioned:
    def fetch_video_details(video_ids):
        if video_ids:
            # empty list to store all values like the previous code:
            video_details = []

            for vid in video_ids:
                request_vd = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=vid
                )
                response_vd = request_vd.execute()

                # for loop for video details of each video ID
                for i in response_vd['items']:
                    details = {"channel_id" : i['snippet']['channelId'],
                            "channel_name" : i['snippet']['channelTitle'],
                            "video_id" : i['id'],
                            "video_name" : i['snippet']['title'],
                            "video_desc" : i['snippet']['description'],
                            "video_pat" : i['snippet']['publishedAt'],
                            "video_duration" : i['contentDetails']['duration'],
                            "view_count" : i['statistics'].get('viewCount'),
                            "like_count" : i['statistics'].get('likeCount'),
                            "favorite_count" : i['statistics']['favoriteCount'],
                            "comments_count" : i['statistics'].get('commentCount'),
                            "thumbnail" : i['snippet']['thumbnails']['default']['url']
                            }
                    video_details.append(details)
            return video_details

        # now pass the videosIDS we have in the function defined above:
        video_data = fetch_video_details(videosIDS)

    ##############################################################################################################

    # getting the comment details from video IDS:
    # we follow the same pattern as the previous code blocks:
    # here, initially there was an error since some videos had comments section disabled. so we have included a try:except block
    # defining a function for extracting comments from all videos:

    def fetch_comment_details(video_ids):
        if video_ids:
            comments_info = []
            try:
                for video_id in video_ids:
                    request_co = youtube.commentThreads().list(
                        part="snippet",
                        videoId=video_id,
                        maxResults=50
                    )
                    response_co = request_co.execute()

                    # to sequencially display all the information of the comment, we will create a for loop inside for each video ID:
                    for cmts in response_co['items']:
                        cmts_data = {"channel_ID" : cmts['snippet']['channelId'],
                                    "video_id" : cmts['snippet']['videoId'],
                                    "comment_id" : cmts['snippet']['topLevelComment']['id'],#using top level comment for this
                                    "comment_text" : cmts['snippet']['topLevelComment']['snippet']['textDisplay'],
                                    "comment_author" : cmts['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                    "comment_pat" : cmts['snippet']['topLevelComment']['snippet']['publishedAt']
                                    }
                        comments_info.append(cmts_data)
            except:
                pass
            return comments_info

        # Comment details:
        comment_data = fetch_comment_details(videosIDS)

##############################################################################################################

    # Function to create table
    def create_table(cursor):

        # Connect to MySQL
        conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db"
    )
        # Create cursor object
        cursor = conn.cursor()

        create_table_channel = """
        CREATE TABLE IF NOT EXISTS channels (
            channel_id VARCHAR(255) PRIMARY KEY,
            channel_name VARCHAR(255),
            channel_des TEXT,
            channel_pat DATETIME,
            channel_pid VARCHAR(255),
            channel_sub INT,
            channel_vc BIGINT
        )
        """

        create_table_video = """
        CREATE TABLE IF NOT EXISTS videos (
            channel_id VARCHAR(255),
            channel_name VARCHAR(255),
            video_id VARCHAR(255) PRIMARY KEY,
            video_name VARCHAR(255),
            video_desc TEXT,
            video_pat VARCHAR(255),
            video_duration INT,
            view_count INT,
            like_count INT,
            favorite_count INT,
            comments_count INT,
            thumbnail VARCHAR(255)
        )
        """

        create_table_comment = """
        CREATE TABLE IF NOT EXISTS comments (
            comment_id VARCHAR(255),
            channel_ID VARCHAR(255),
            video_id VARCHAR(255),
            comment_text TEXT,
            comment_author VARCHAR(255),
            comment_pat DATETIME
        )
        """

        cursor.execute(create_table_channel)
        cursor.execute(create_table_video)
        cursor.execute(create_table_comment)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    # create_table function executes all three table creations.
    ##############################################################################################################

    # Defining the convert to datetime function:
    # Function to convert date string to datetime object:

    def convert_to_datetime(date_string):
        try:
            # Attempt to parse the date string with format '%Y-%m-%dT%H:%M:%S.%fZ'
            date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:
            try:
                # Attempt to parse the date string with format '%Y-%m-%dT%H:%M:%SZ'
                date_object = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                # If both formats fail, return None
                return None
        return date_object

    ##############################################################################################################

    # Function to convert duration string to seconds
    def duration_to_seconds(duration_str):
        # Check if the duration string starts with 'PT'
        if duration_str.startswith('PT'):
            # Check if 'H', 'M', or 'S' are present in the duration string
            if 'H' in duration_str:
                # Extract hours, minutes, and seconds parts
                hours, rest = duration_str[2:].split('H')
                if 'M' in rest:
                    minutes, seconds = rest.split('M')
                    minutes = int(minutes) if minutes else 0
                else:
                    minutes = 0
                    seconds = rest[:-1]
                # Convert hours, minutes, and seconds parts to integers
                hours = int(hours) if hours else 0
                seconds = int(seconds[:-1]) if seconds else 0
                # Calculate total duration in seconds
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds
            elif 'M' in duration_str:
                # Extract minutes and seconds parts
                minutes, seconds = duration_str[2:].split('M')
                # Convert minutes and seconds parts to integers
                minutes = int(minutes) if minutes else 0
                seconds = int(seconds[:-1]) if seconds else 0
                # Calculate total duration in seconds
                total_seconds = minutes * 60 + seconds
                return total_seconds
            elif 'S' in duration_str:
                # Extract seconds part
                seconds = duration_str[2:-1]
                # Convert seconds part to integer
                total_seconds = int(seconds) if seconds else 0
                return total_seconds
        return None  # Return None if the format is invalid

    ##############################################################################################################

    # Defining the insert functions for all 3 tables:
    # Function to insert data into MySQL database
    #__________________________________________________________________________________________________________#
    # Channel data:
    def insert_channel_data(data_list):
        # Connect to MySQL
        conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db"
    )
        # Create cursor object
        cursor = conn.cursor()

        insert_data = """
            INSERT INTO channels 
            (channel_id, channel_name, channel_des, channel_pat, channel_pid, channel_sub, channel_vc) 
            VALUES 
            (%(channel_id)s, %(channel_name)s, %(channel_des)s, %(channel_pat)s, %(channel_pid)s, %(channel_sub)s, %(channel_vc)s)
            """
        # Convert channel_pat to datetime object
        for data in data_list:
            data['channel_pat'] = convert_to_datetime(data['channel_pat'])

        # Insert data into MySQL table
        cursor.executemany(insert_data, data_list)

        # Commit changes and close connection
        conn.commit()
        conn.close()
        
    # Example data list of dictionaries
    # Convert the single dictionary to a list containing that dictionary
    channel_data_insert = [channel_data]

    # calling the fucntion:
    # insert_channel_data(channel_data_insert)
    #__________________________________________________________________________________________________________#
    # Video data:
    def insert_video_data(cursor, data):
        # Connect to MySQL
        conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db"
    )
        # Create cursor object
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO videos (
            channel_id, channel_name, video_id, video_name, 
            video_desc, video_pat, video_duration, view_count, like_count, 
            favorite_count, comments_count, thumbnail
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for entry in data:
            # Convert video_pat to MySQL datetime format
            video_pat_datetime = datetime.strptime(entry['video_pat'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
            
            # Convert video_duration to seconds
            video_duration = duration_to_seconds(entry['video_duration'])
            
            # Check if comments_count is None and handle it
            if entry['comments_count'] is None:
                entry['comments_count'] = 0
            if entry['view_count'] is None:
                entry['view_count'] = 0
            if entry['like_count'] is None:
                entry['like_count'] = 0

            values = (
                entry['channel_id'], entry['channel_name'], entry['video_id'], 
                entry['video_name'], entry['video_desc'],
                video_pat_datetime, video_duration, int(entry['view_count']),
                int(entry['like_count']), int(entry['favorite_count']),
                int(entry['comments_count']), entry['thumbnail']
            )
            cursor.execute(insert_query, values)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()

    # Calling the function:       
    #insert_video_data(video_data)
    #__________________________________________________________________________________________________________#
    # Comment data:

    def insert_comment_data(cursor, comment_data):
        # Connect to MySQL
        conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db"
    )
        # Create cursor object
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO comments (
            comment_id, channel_ID, video_id, comment_text, comment_author, comment_pat
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        for comment in comment_data:
            # Convert comment_pat to MySQL datetime format
            comment_pat_datetime = datetime.strptime(comment['comment_pat'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d %H:%M:%S')
            
            # Attempt to insert the comment
            values = (
                comment['comment_id'], comment['channel_ID'], comment['video_id'],
                comment['comment_text'], comment['comment_author'], comment_pat_datetime
            )
            cursor.execute(insert_query, values)

        # Commit changes and close connection
        conn.commit()
        conn.close()

    # calling the function:
    #insert_comment_data(comment_data)

    ##############################################################################################################

    # Function to check if data already exists in MySQL
    def check_data_exists(channelid):
        # Placeholder function to check if data already exists in MySQL
        return False

    ##############################################################################################################

    # Function to migrate data to MySQL

    def migrate_to_mysql(channelid):
        # Establish connection to MySQL database
        conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db")

        # Create cursor object
        cursor = conn.cursor()

        if check_data_exists(channelid):
            st.error("Data already present in MySQL.")
        else:
            # Create tables in MySQL
            create_table(cursor)
            
            # Fetch data from YouTube API
            channel_data = fetch_channel_details(channelid)
            videosIDS = extract_vids(channelid)
            video_data = fetch_video_details(videosIDS)
            comment_data = fetch_comment_details(videosIDS)
            
            # Insert data into MySQL
            insert_channel_data(channel_data_insert)
            insert_video_data(cursor, video_data)
            insert_comment_data(cursor, comment_data)
            
            st.success("Transfer successful.")
    
    # Check if a channel ID is provided
    if channelid:
        if st.button("Fetch Channel Details"):
            channel_data = fetch_channel_details(channelid)
            if channel_data:
                st.write(f"Title of Channel: {channel_data['channel_name']}")
                st.write(f"Published date and time: {channel_data['channel_pat']}")
                st.write(f"Channel Description: {channel_data['channel_des']}")
                st.write(f"Playlist ID with video uploads: {channel_data['channel_pid']}")
                st.write(f"Channel Viewcount: {channel_data['channel_vc']}")
                st.write(f"Channel SubscriberCount: {channel_data['channel_sub']}")
            else:
                st.error("Channel details not found.")
        
        if st.button("Migrate to MySQL"):
            migrate_to_mysql(channelid)

# PRE-DEFINED SQL QUERIES Page:
elif selected == "Pre-defined SQL Queries":
    st.header(':blue[Queries and Results ]')
    st.write('''In this page, we have the results to the queries that have been asked of us based on the channel data we have collected and migrated to SQL ''')
    st.write(''' Like how we created and inserted extracted data into tables to MySQL using a python-mysql connection,
             likewise, we are using :blue[python to query our MySQL database] for their pre-defined queries and :blue[display them onto
             our streamlit app].''')
    
    # Establish MySQL connection
    
    conn = mysql.connector.connect(
        host="host",
        user="root",
        password="pw",
        database="db"
    )
    cursor = conn.cursor()

    # Function to display pre-defined SQL queries and their solutions
    def predefined_queries():
        st.title("Pre-defined SQL queries")
        
        # Pre-defined SQL queries and their descriptions
        question_tosql = st.selectbox('Select your Question from dropdown :',
                                  ('1. What are the names of all the videos and their corresponding channels?',
                                   '2. Which channels have the most number of videos, and how many videos do they have?',
                                   '3. What are the top 10 most viewed videos and their respective channels?',
                                   '4. How many comments were made on each video, and what are their corresponding video names?',
                                   '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                   '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                   '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                   '8. What are the names of all the channels that have published videos in the year 2022?',
                                   '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                   '10. Which videos have the highest number of comments, and what are their corresponding channel names?'),
                                  key='collection_question')

        # Results for the queries:
        # Q1
        if question_tosql == '1. What are the names of all the videos and their corresponding channels?':
            cursor.execute('''SELECT channel_name, video_name FROM migratedb.videos ORDER BY channel_name;''')
            result_1 = cursor.fetchall()
            df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
            df1.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df1)

        # Q2
        elif question_tosql == '2. Which channels have the most number of videos, and how many videos do they have?':
            cursor.execute('''SELECT channel_name, count(video_id) as video_count FROM migratedb.videos group by channel_name order by count(video_id) desc;''')
            result_2 = cursor.fetchall()
            df2 = pd.DataFrame(result_2, columns=['Channel Name', 'Video Count']).reset_index(drop=True)
            df2.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df2)

        # Q3
        elif question_tosql == '3. What are the top 10 most viewed videos and their respective channels?':
            cursor.execute('''SELECT video_id, video_name, view_count, channel_name FROM migratedb.videos ORDER BY view_count DESC LIMIT 10;''')
            result_3 = cursor.fetchall()
            df3 = pd.DataFrame(result_3, columns= ['Video_ID','Video Name', 'View count','Channel Name']).reset_index(drop=True)
            df3.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df3)

        # Q4
        elif question_tosql == '4. How many comments were made on each video, and what are their corresponding video names?':
            cursor.execute('''SELECT video_id, video_name, comments_count FROM migratedb.videos ORDER BY comments_count desc;''')
            result_4 = cursor.fetchall()
            df4 = pd.DataFrame(result_4, columns=['Video ID','Video Name', 'Comment count']).reset_index(drop=True)
            df4.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df4)

        # Q5
        elif question_tosql == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
            cursor.execute('''SELECT video_id, video_name, like_count, channel_name FROM migratedb.videos ORDER BY like_count desc;''')
            result_5 = cursor.fetchall()
            df5 = pd.DataFrame(result_5, columns=['Video ID','Video Name', 'Like count','Channel Name']).reset_index(drop=True)
            df5.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df5)

        # Q6
        elif question_tosql == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
            st.write('**Note:- In November 2021, YouTube removed the public dislike count from all of its videos.**')
            cursor.execute('''SELECT video_id, video_name, like_count FROM migratedb.videos ORDER BY like_count desc;"''')
            result_6 = cursor.fetchall()
            df6 = pd.DataFrame(result_6, columns=['Video ID','Video Name','Like count']).reset_index(drop=True)
            df6.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df6)

        # Q7
        elif question_tosql == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
            cursor.execute("SELECT channel_id, channel_name, channel_vc FROM migratedb.channels ORDER BY channel_vc desc;")
            result_7 = cursor.fetchall()
            df7 = pd.DataFrame(result_7, columns=['Channel ID', 'Channel Name','Total number of views']).reset_index(drop=True)
            df7.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df7)

        # Q8
        elif question_tosql == '8. What are the names of all the channels that have published videos in the year 2022?':
            cursor.execute('''SELECT distinct(channel_name), YEAR(video_pat) FROM migratedb.videos WHERE YEAR(video_pat) = 2022 ORDER BY channel_name;''')
            result_8 = cursor.fetchall()
            df8 = pd.DataFrame(result_8, columns=['Channel Name', 'Video Published Year']).reset_index(drop=True)
            df8.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df8)

        # Q9
        elif question_tosql == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
            cursor.execute('''SELECT channel_id, channel_name, ROUND(AVG(video_duration/60), 2) AS avg_duration_minutes
                            FROM migratedb.videos GROUP BY channel_id, channel_name ORDER BY ROUND(AVG(video_duration/60), 2) DESC;''')
            result_9 = cursor.fetchall()
            df9 = pd.DataFrame(result_9, columns=['Channel ID','Channel Name', 'Average duration of videos (in minutes)']).reset_index(drop=True)
            df9.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df9) 

        # # Q10
        elif question_tosql == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
            cursor.execute('''SELECT channel_name, video_name, comments_count FROM migratedb.videos ORDER BY comments_count DESC;''')
            result_10 = cursor.fetchall()
            df10 = pd.DataFrame(result_10, columns=['Channel Name', 'Video Name', 'Number of Comments']).reset_index(drop=True)
            df10.index += 1
            st.write(" :red[Query solution :]")
            st.dataframe(df10)

        conn.close()
    predefined_queries()

# CUSTOM SQL QUERIES Page:
elif selected == "Custom SQL Queries":
    # establish MySQL connection
    def connect_to_mysql():
        conn = mysql.connector.connect(
            host="host",
            user="root",
            password="pw",
            database="db"
        )
        return conn

    # Function to execute SQL queries and fetch results
    def execute_query(conn, query):
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    # Function to allow users to insert custom SQL queries
    def custom_query():
        st.title("Custom SQL Query")

        # Text input for custom SQL query
        user_query = st.text_area("Enter your SQL query here")

        # Button to execute custom SQL query
        if st.button("Execute Query"):
            conn = connect_to_mysql()
            cursor = conn.cursor()
            result = execute_query(conn, user_query)
            
            if result:
                # Display result in tabular format
                try:
                    st.write("Query Solution:")
                    st.dataframe(result)
                except TypeError as e:
                    st.error(f"Error displaying table: {e}")
            else:
                st.write("No results found.")

    custom_query()

