# Importing necessary libraries:
from googleapiclient.discovery import build
import re
import mysql.connector
import sqlalchemy
from googleapiclient.errors import HttpError
from sqlalchemy import create_engine
import pymysql
import pandas as pd
from streamlit_option_menu import option_menu
import streamlit as st

# set up page layout for the app:
st.set_page_config(page_title="YouTube Data app", layout="wide", initial_sidebar_state="expanded")

# Creating a side navigation bar:
with st.sidebar:
    selected = option_menu("Content", ["Home","Data Collection & Migration","SQL Data Analysis","Pre-defined SQL Queries"],
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
    
# Navigation page 2: Data collection and migration tab
elif selected == "Data Collection & Migration":
    tab1,tab2 = st.tabs(["$\LARGE Collect $", "$\LARGE Move $"])
    
    # COLLECT TAB
    with tab1:
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
        
        channel_id = st.text_input('Enter the channel id here:')
        st.write(''':red[Click below to retrieve and store data.]''')
        Get_data = st.button('**Collect data**')

        # Define Session state to Get data button
        if "Get_state" not in st.session_state:
            st.session_state.Get_state = False

        if Get_data or st.session_state.Get_state:
            st.session_state.Get_state = True

            api_key="api_key"            
            youtube=build("youtube","v3",developerKey=api_key)

            #Function to get channel statisics
            try:
                def get_channel_stats(channel_id):
                    all_data=[]
                    request = youtube.channels().list(
                                    part="snippet,contentDetails,statistics",
                                    id=channel_id)
                    response = request.execute()
                    
                    for i in range(len(response['items'])):
                        data=dict(channel_name=response['items'][i]['snippet']['title'],
                            channel_id=response['items'][i]['id'],
                            subscribers=response['items'][i]['statistics']['subscriberCount'],
                            views=response['items'][i]['statistics']['viewCount'],
                            Total_videos=response['items'][i]['statistics']['videoCount'],
                            channel_description=response['items'][i]['snippet']['description'],
                            Playlist_Id=response['items'][i]['contentDetails']['relatedPlaylists']['uploads'])
                        all_data.append(data)     
                
                    return all_data
                
                get_channel_stats(channel_id)

                channel_data=pd.DataFrame(get_channel_stats(channel_id))
                
                channel_data['subscribers']=pd.to_numeric(channel_data['subscribers'])
                channel_data['views']=pd.to_numeric(channel_data['views'])
                channel_data['Total_videos']=pd.to_numeric(channel_data['Total_videos'])

            #playlist information
                def get_pl_info(youtube, channel_id):
                    next_page_token = None
                    playlist = []

                    while True:
                        request = youtube.playlists().list(
                            part='snippet,contentDetails',
                            channelId=channel_id,
                            maxResults=50)
                        response = request.execute()                       
                        
                        for i in range(len(response['items'])):
                            data=dict(pl_id=response['items'][i]['id'],
                                channel_name=response['items'][i]['snippet']['title'],
                                channel_id=response['items'][i]['snippet']['channelId'],
                                publish_at=response['items'][i]['snippet']['publishedAt'],
                                videos_count=response['items'][i]['contentDetails']['itemCount'])
                            playlist.append(data)
                        next_page_token = response.get('nextPageToken')
                        if next_page_token is None:
                            break
                    return playlist
                
                pl_data=pd.DataFrame(get_pl_info(youtube,channel_id))
        

            # Get VIDEO IDs
                def get_video_ids(channel_id):
                    
                    request = youtube.channels().list(
                                    part="snippet,contentDetails,statistics",
                                    id=channel_id,)
                    response = request.execute()
                    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                    
                    video_ids = []
                    next_page_token =None 
                
                    while True:
                        request = youtube.playlistItems().list(
                                        part='snippet',
                                        playlistId = Playlist_Id,
                                        maxResults = 50,
                                        pageToken = next_page_token)
                        response1 = request.execute()
                    
                        for i in range(len(response1['items'])):
                            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
                        next_page_token = response1.get('nextPageToken')
                        
                        if next_page_token is None:
                            break
                    return video_ids
                
                video_ids=get_video_ids(channel_id)
            

            # FUNCTION TO GET VIDEO DETAILS
                def get_video_details(video_ids):
                    video_stats = []
                    
                    for i in range(0, len(video_ids), 50):
                        response = youtube.videos().list(
                                    part="snippet,contentDetails,statistics",
                                    id=','.join(video_ids[i:i+50])).execute()
                        
                        for video in response['items']:
                            video_details = dict(Channel_name = video['snippet']['channelTitle'],
                                                Channel_id = video['snippet']['channelId'],
                                                Video_id = video['id'],
                                                Title = video['snippet']['title'],
                                                Tags = video['snippet'].get('tags'),
                                                Thumbnail = video['snippet']['thumbnails']['default']['url'],
                                                Description = video['snippet']['description'],
                                                Published_date = video['snippet'].get('publishedAt'),
                                                Duration = video['contentDetails']['duration'],
                                                Views = video['statistics']['viewCount'],
                                                Likes = video['statistics'].get('likeCount'),
                                                Comments = video['statistics'].get('commentCount'),
                                                Favorite_count = video['statistics']['favoriteCount'],
                                                Caption_status = video['contentDetails']['caption'])
                            video_stats.append(video_details)
                    
                    return video_stats
                
                v_stats=get_video_details(video_ids)
                v_stats_df=pd.DataFrame(v_stats)

                v_stats_df['Duration'] = pd.to_timedelta(v_stats_df['Duration'])

                #Convert timedelta to string format 
                v_stats_df['Duration'] = v_stats_df['Duration'].astype(str)

                #Format the string to hh:mm:ss
                v_stats_df['Duration'] = v_stats_df['Duration'].str.extract(r'(\d+:\d+:\d+)')

                v_stats_df['Published_date'] = pd.to_datetime(v_stats_df['Published_date']).dt.date
                v_stats_df['Views'] = pd.to_numeric(v_stats_df['Views'])
                v_stats_df['Likes'] = pd.to_numeric(v_stats_df['Likes'])
                v_stats_df['Comments'] = pd.to_numeric(v_stats_df['Comments'])
                v_stats_df['Tags'] = v_stats_df['Tags'].astype(str)

            # convert to datetime:
                def convert_duration(Duration):
                    regex = r'PT(\d+H)?(\d+M)?(\d+S)?'
                    match = re.match(regex,'Duration')
                    if not match:
                        return '00:00:00'
                    hours, minutes, seconds = match.groups()
                    hours = int(hours[:-1]) if hours else 0
                    minutes = int(minutes[:-1]) if minutes else 0
                    seconds = int(seconds[:-1]) if seconds else 0
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    
                    return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60),
                                                                    int(total_seconds % 60))


            # GET COMMENT INFORMATION
                def get_comment_info(video_ids):
                    Comment_data=[]

                    try:
                        for video_id in video_ids:
                            request=youtube.commentThreads().list(
                                    part="snippet",
                                    videoId=video_id,
                                    maxResults=50)
                                
                            response=request.execute()
                    
                            for item in response['items']:
                                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                                    Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                                    Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                                    Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                    Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                                
                                Comment_data.append(data)
                    except:
                        pass
                    return Comment_data
                
                comment_data=get_comment_info(video_ids)
                channel_comment=pd.DataFrame(comment_data)

            except:
                pass
            
    # MIGRATION TAB:
    with tab2:
        st.markdown('### :blue[Data Migration area :]')
        st.markdown('''
                    Going over to here from the **Fetch** tab, the data that has been extracted from the desired channel ID as given by the user
                    will have to be **Moved** to our MySQL database. ''')
        st.markdown(''' 
                    - Click on the below :blue[Migrate to MySQL] button to proceed with the migration of the fetched data to MySQL.
                    - Upon successful movement of all data to their respective tables, a :blue[Data migrated successfully] message pops indicating
                    complete and successful migration.''')
        st.markdown("Let's go!")

        Migrate = st.button('**Migrate to MySQL**')
        if 'migrate_sql' not in st.session_state:
            st.session_state_migrate_sql = False
        if Migrate or st.session_state_migrate_sql:
            st.session_state_migrate_sql = True
        
            #**Connection to SQL**

            connect=pymysql.connect(host="hostname",
                                            user="root",
                                            password="pw",
                                            database="db_name",
                                            port=port_num)
            mycursor=connect.cursor()
            mycursor.execute('CREATE DATABASE IF NOT EXISTS ydh')
            mycursor.execute('use ydh')
            mycursor.close()
            connect.close()

            engine = create_engine("mysql+pymysql://root:pw@hostname:port_num/db_name")
            connection = engine.connect()
                            
        
            channel_data.to_sql(con=engine,name='channels',if_exists='append',index=False,
                                dtype={'Channel_Name':sqlalchemy.types.VARCHAR(length=225),
                                            'Channel_Id':sqlalchemy.types.VARCHAR(length=225),
                                            'Subscribers':sqlalchemy.types.BigInteger,
                                            'Views':sqlalchemy.types.INT,
                                            'Total_Videos':sqlalchemy.types.BigInteger,
                                            'Channel_Description':sqlalchemy.types.TEXT,
                                            'Playlist_Id':sqlalchemy.types.VARCHAR(length=225)})
                                

            pl_data.to_sql(con=engine,name='playlist', if_exists='append', index=False,
                                dtype={"pl_Id": sqlalchemy.types.VARCHAR(length=225),
                                       "channel_name": sqlalchemy.types.VARCHAR(length=225),
                                       "channel_id": sqlalchemy.types.VARCHAR(length=225),
                                       "publish_at": sqlalchemy.types.String(length=50),
                                       "videos_count": sqlalchemy.types.INT})
                    
            v_stats_df.to_sql(con=engine, name='video',if_exists='append',index=False, 
                              dtype={'Channel_name':sqlalchemy.types.VARCHAR(length=225),
                                     'Channel_Id':sqlalchemy.types.VARCHAR(length=225),
                                     'Video_id':sqlalchemy.types.VARCHAR(length=225),
                                     'Title':sqlalchemy.types.VARCHAR(length=225),
                                     'Tags':sqlalchemy.types.VARCHAR(length=2000),
                                     'Thumbnail':sqlalchemy.types.VARCHAR(length=225),
                                     'Description':sqlalchemy.types.VARCHAR(length=8000),
                                     'Published_date':sqlalchemy.types.String(length=50),
                                     'Duration':sqlalchemy.types.VARCHAR(length=1024),
                                     'Views':sqlalchemy.types.BigInteger,
                                     'Likes':sqlalchemy.types.BigInteger,
                                     'Comments':sqlalchemy.types.INT,
                                     'Favorite_count':sqlalchemy.types.INT, 
                                     'Caption_status':sqlalchemy.types.VARCHAR(length=225)})
            
            channel_comment.to_sql(con=engine, name='comments', if_exists='append', index=False,
                                   dtype={'Video_Id': sqlalchemy.types.VARCHAR(length=225),
                                          'Comment_Id': sqlalchemy.types.VARCHAR(length=225),
                                          'Comment_Text': sqlalchemy.types.TEXT,
                                          'Comment_Author': sqlalchemy.types.VARCHAR(length=225),
                                          'Comment_Published': sqlalchemy.types.String(length=50)})
            
            Migrate=st.success('**:green[Data migrated successfully]**')
                
# Navigation page 3: SQL Data Analysis tab:            
elif selected == "SQL Data Analysis":
    st.header(':blue[Channel Data Analysis area]')
    st.write(
        '''Now that we have our data pertaining to each channel moved to our MySQL database, 
        we can move to the next phase of making it ready for our analysis. Let us first check if the channels for which we have data extracted are uploaded to the channel table.''')
    
    # Check available channel data
    Check_channel = st.toggle(':blue[Toggle to see the available channels]')

    if Check_channel:
        # Create database connection
        engine = create_engine("mysql+pymysql://root:Sanc3098@localhost:3306/ydh")
            # Execute SQL query to retrieve channel names
        query = "SELECT channel_name FROM channels;"
        results = pd.read_sql(query,engine)
            # Get channel names as a list
        channel_names_fromsql = list(results['channel_name'])
            # Create a DataFrame from the list and reset the index to start from 1
        df_at_sql = pd.DataFrame(channel_names_fromsql,columns=['Channels in SQL table']).reset_index(drop=True)
            # Reset index to start from 1 instead of 0
        df_at_sql.drop_duplicates(inplace=True)
        df_at_sql.index += 1
            # Show dataframe
        st.dataframe(df_at_sql)

# Navigation page 4: Pre-defined SQL Queries tab:
elif selected == "Pre-defined SQL Queries":
    st.header(':blue[Queries and Results ]')
    st.write('''In this page, we have the results to the queries that have been asked of us based on the channel data we have collected and migrated to SQL ''')
    st.write(''' Like how we created and inserted extracted data into tables to MySQL using a python-mysql connection,
             likewise, we are using :blue[python to query our MySQL database] for their pre-defined queries and :blue[display them onto
             our streamlit app].''')
    
    # Selectbox creation
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

    # Create a connection to SQL
    connect_for_question = pymysql.connect(host='hostname', user='root', password='pw',port= port_num, db='db_name')
    cursor = connect_for_question.cursor()
    engine = create_engine("mysql+pymysql://root:pw@hostname:port_num/db_name")

    # Results for the queries:
    # Q1
    if question_tosql == '1. What are the names of all the videos and their corresponding channels?':
        cursor.execute('''SELECT video.Channel_name,video.Title FROM video ''')
        result_1 = cursor.fetchall()
        df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
        df1.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df1)

    # Q2
    elif question_tosql == '2. Which channels have the most number of videos, and how many videos do they have?':
        cursor.execute('''SELECT channels.channel_name, channels.Total_videos FROM channels ORDER BY Total_videos DESC''')
        result_2 = cursor.fetchall()
        df2 = pd.DataFrame(result_2, columns=['Channel Name', 'Video Count']).reset_index(drop=True)
        df2.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df2)

    # Q3
    elif question_tosql == '3. What are the top 10 most viewed videos and their respective channels?':
        cursor.execute('''SELECT video.Title, video.Views, video.Channel_name FROM video ORDER BY video.Views DESC LIMIT 10''')
        result_3 = cursor.fetchall()
        df3 = pd.DataFrame(result_3, columns= ['Video Name', 'View count','Channel Name']).reset_index(drop=True)
        df3.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df3)

    # Q4
    elif question_tosql == '4. How many comments were made on each video, and what are their corresponding video names?':
        cursor.execute('''SELECT video.Title, video.Comments FROM video''')
        result_4 = cursor.fetchall()
        df4 = pd.DataFrame(result_4, columns=['Video Name', 'Comment count']).reset_index(drop=True)
        df4.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df4)

    # Q5
    elif question_tosql == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        cursor.execute('''SELECT video.Channel_name, video.Title, video.Likes FROM video ORDER BY video.Likes DESC''')
        result_5 = cursor.fetchall()
        df5 = pd.DataFrame(result_5, columns=['Channel Name', 'Video Name', 'Like count']).reset_index(drop=True)
        df5.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df5)

    # Q6
    elif question_tosql == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        st.write('**Note:- In November 2021, YouTube removed the public dislike count from all of its videos.**')
        cursor.execute('''SELECT video.Channel_name, video.Title, video.Likes FROM video ORDER BY video.Likes DESC''')
        result_6 = cursor.fetchall()
        df6 = pd.DataFrame(result_6, columns=['Channel Name', 'Video Name', 'Like count', ]).reset_index(drop=True)
        df6.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df6)

    # Q7
    elif question_tosql == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        cursor.execute("SELECT channel_name,views FROM channels ORDER BY views DESC;")
        result_7 = cursor.fetchall()
        df7 = pd.DataFrame(result_7, columns=['Channel Name', 'Total number of views']).reset_index(drop=True)
        df7.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df7)

    # Q8
    elif question_tosql == '8. What are the names of all the channels that have published videos in the year 2022?':
        cursor.execute('''SELECT video.channel_name, video.Published_date FROM video WHERE EXTRACT(YEAR FROM Published_date) = 2022''')
        result_8 = cursor.fetchall()
        df8 = pd.DataFrame(result_8, columns=['Channel Name', 'Year 2022 only']).reset_index(drop=True)
        df8.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df8)

    # Q9
    elif question_tosql == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        cursor.execute('''SELECT video.Channel_name, TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(video.Duration)))), '%H:%i:%s') AS Duration  
                       FROM video GROUP by Channel_name ORDER BY Duration DESC ''')
        result_9 = cursor.fetchall()
        df9 = pd.DataFrame(result_9, columns=['Channel Name', 'Average duration of videos (HH:MM:SS)']).reset_index(drop=True)
        df9.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df9)

    # # Q10
    elif question_tosql == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        cursor.execute('''SELECT video.Channel_name, video.Title, video.Comments FROM video ORDER BY video.Comments DESC''')
        result_10 = cursor.fetchall()
        df10 = pd.DataFrame(result_10, columns=['Channel Name', 'Video Name', 'Number of comments']).reset_index(drop=True)
        df10.index += 1
        st.write(" :red[Query solution :]")
        st.dataframe(df10)

# SQL DB connection close
    connect_for_question.close()
