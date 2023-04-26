from tkinter import *
import tkinter as tk
from PIL import ImageTk, Image
import praw
import pandas as pd
from datetime import datetime
import mysql.connector
import MySQLdb
from sqlalchemy import create_engine, select, MetaData, Table, and_
from Tools.scripts.dutree import display
import pyodbc
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
import pymysql
import os.path

nltk.download('punkt')
nltk.download('stopwords')

# globals
subRedditPosts = []
subRedditComments = []  # comments under each post
postContent = []
postTitles = []
postTimes = []

# database credentials
host = "localhost"
# u = "root"
# p = "yourpassword"
# s = "reddit"
# originally u,p,s were hardcoded and used to automatically signin to the program
# now they are set within the signin function
# they are still here in case for testing
auth_plugin = 'mysql_native_password'

# default number of posts and comments
postNum = 10
commentNum = 10

def signInReddit():
    global clientId # these are the credentials for the reddit api
    global clientSecret
    global userAgent
    bgColor = "navy"
    fontColor = "white"
    font = "courier"

    # all this is just TKInter GUI setups
    signInRED = tk.Tk()
    signInRED.title("Sign In")
    signInRED.geometry('500x300')
    signInRED.configure(bg=bgColor)
    signinLabel = tk.Label(text="Enter your credentials for the Reddit API", font=font, bg=bgColor, fg=fontColor)
    signinLabel.grid(row=0, column=0, columnspan=2)
    clientIDLabel = tk.Label(text="Client ID: ", font=font, bg=bgColor, fg=fontColor)
    clientIDLabel.grid(row=1, column=0)
    clientIDInput = tk.Text(signInRED, height=1, width=25)
    clientIDInput.grid(row=1, column=1)
    clientSecretLabel = tk.Label(text="Client Secret: ", font=font, bg=bgColor, fg=fontColor)
    clientSecretLabel.grid(row=2, column=0)
    clientSecretInput = tk.Text(signInRED, height=1, width=25)
    clientSecretInput.grid(row=2, column=1)
    userAgentLabel = tk.Label(text="User Agent: ", font=font, bg=bgColor, fg=fontColor)
    userAgentLabel.grid(row=3, column=0)
    userAgentInput = tk.Text(signInRED, height=1, width=25)
    userAgentInput.grid(row=3, column=1)
    clientId = clientIDInput.get("1.0", "end-1c")
    clientSecret = clientSecretInput.get("1.0", "end-1c")
    userAgent = userAgentInput.get("1.0", "end-1c")

    #this sign in button calls the function to make sure the user's reddit credentials are correct
    signInBtn = tk.Button(signInRED, text="Sign In", command=lambda: checkRedditCredentials(clientIDInput.get("1.0", "end-1c"),
                                                                                            clientSecretInput.get("1.0", "end-1c"),
                                                                                            userAgentInput.get("1.0", "end-1c"), signInRED))
    signInBtn.grid(row=4, column=0, columnspan=2)
    signInRED.mainloop()
    #return clientId, clientSecret, userAgent

def signInFunc():
    bgColor = "navy"
    fontColor = "white"
    font = "courier"

    # TKInter gui calls
    signIn = tk.Tk()
    signIn.title("Sign In")
    signIn.geometry('500x300')
    signIn.configure(bg=bgColor)
    signinLabel = tk.Label(text="Enter your credentials for MySQL", font=font, bg=bgColor, fg=fontColor)
    signinLabel.grid(row=0, column=0, columnspan=2)
    userNameLabel = tk.Label(text = "User Name: ", font=font, bg=bgColor, fg=fontColor)
    userNameLabel.grid(row=1, column=0)
    userNameInput = tk.Text(signIn, height=1, width=25)
    userNameInput.grid(row=1, column=1)
    passWordLabel = tk.Label(text="Password: ", font=font, bg=bgColor, fg=fontColor)
    passWordLabel.grid(row=2, column=0)
    passInput = Entry(signIn, show="*", width=33)
    passInput.grid(row=2, column=1)
    schemaLabel = tk.Label(text="Schema: ", font=font, bg=bgColor, fg=fontColor)
    schemaLabel.grid(row=3, column=0)
    schemaName = tk.Text(signIn, height=1, width=25)
    schemaName.grid(row=3, column=1)
    u = userNameInput.get("1.0", "end-1c")
    p = passInput.get()
    s = schemaName.get("1.0", "end-1c")
    # print("user: " + u + "\npass: " + p + "\nschema: " + s)

    # this button sends the user to the main window if the sign in credentials are correct
    signInBtn = tk.Button(signIn, text="Sign In", command=lambda: mainWindowFunc(userNameInput.get("1.0", "end-1c"),
                                                                                 passInput.get(),
                                                                                 schemaName.get("1.0", "end-1c"),
                                                                                 signIn))
    signInBtn.grid(row=4, column=0, columnspan=2)
    signIn.mainloop()
    return userNameInput, passInput, schemaName


def checkRedditCredentials(clientId, clientSecret, userAgent, w):
        # if the user's credentials are correct then the main window is opened, if they are incorrect, the sign in window is opened again
        w.destroy()  # automatically closes the signin window
        try:
            reddit_read_only = praw.Reddit(client_id=clientId,  # your client id
                                           client_secret=clientSecret,  # your client secret
                                           user_agent=userAgent)  # your user agent

            subreddit = reddit_read_only.subreddit('news')
            for post in subreddit.hot(limit=4):
                print('Testing Credentials')

            redditInfo = open("Reddit_Credentials.txt", "w")
            L = [clientId + "\n", clientSecret + "\n", userAgent + "\n"]
            redditInfo.writelines(L)
            redditInfo.close()

        except:
            signInReddit()

def mainWindowFunc(us, pa, sc, w):
    w.destroy()
    user = us
    passW = pa
    schema = sc

    if(testDbConnection(user, passW, schema)):
        dbInfo = open("Db_Credentials.txt", "w")
        L = [user + "\n", passW + "\n", schema + "\n"]
        dbInfo.writelines(L)
        dbInfo.close()

    else:
        signInFunc()
        exit() #will be needed for failed sign in attempts to prevent program from launching bad main windows


    def createDropdownMenu():  # creates the drop down menu of tables
        dbConnection = mysql.connector.connect(
            host=host,
            user=user,
            password=passW,
            database=schema,
            auth_plugin=auth_plugin
        )

        tables = pd.read_sql("SHOW TABLES;", con=dbConnection)
        atables = tables.iloc[:, 0].to_numpy()

        # df = pd.read_sql("select * from " + str(atables[len(atables) - 1]) + ";", con=db_connection)
        # print(df)

        try:
            variable.set(atables[len(atables) - 1])  # default value

        except:
            variable.set('')
            atables = ['EMPTY DATABASE!']

        dropDownMenu = OptionMenu(mainWindow, variable, *atables)

        return dropDownMenu

    # gui globals
    font = "courier"
    bgColor = "navy"
    txtColor = 'white'
    # create window frame
    mainWindow = tk.Tk()
    mainWindow.title("Social Media Detection")
    mainWindow.geometry('1050x700')
    mainWindow.configure(bg=bgColor)
    # input label
    inputLabel = tk.Label(text="Enter the subreddit you would like to poll from:", font=font, fg=txtColor, bg=bgColor)
    inputLabel.grid(row=0, column=0, columnspan=2, sticky='W')
    # text field for subreddit input
    inputField = tk.Text(mainWindow, height=1, width=25)
    # inputField = Entry(mainWindow, show="*", width=25)
    inputField.grid(row=0, column=2, sticky='W')
    # create button for polling data, passes data from inputField
    pollBtn = tk.Button(mainWindow, text="Poll Subreddit",
                        command=lambda: pollRedditData(inputField.get("1.0", "end-1c"), user, passW, schema))
    pollBtn.grid(row=0, column=3)

    postNumLabel = tk.Label(text="Enter # of Posts to Poll (increases loading times)", font=font, fg=txtColor, bg=bgColor)
    postNumLabel.grid(row=1, column=0, columnspan=2, sticky='W')
    postNumField = tk.Text(mainWindow, height=1, width=25)
    postNumField.insert(tk.END, postNum)
    postNumField.grid(row=1, column=2)

    commentNumLabel = tk.Label(text="Enter # of Comments (heavily increases loading times)", font=font, fg=txtColor, bg=bgColor)
    commentNumLabel.grid(row=2, column=0, columnspan=2, sticky='W')
    commentNumField = tk.Text(mainWindow, height=1, width=25)
    commentNumField.insert(tk.END, commentNum)
    commentNumField.grid(row=2, column=2)

    # output label
    outputLabel = tk.Label(text="Search Results", font=font, fg=txtColor, bg=bgColor)
    outputLabel.grid(row=3, column=0, columnspan=4)
    # output field
    outputField = tk.Text(mainWindow, height=20, width=120)
    outputField.grid(row=4, column=0, rowspan=3, columnspan=4)
    # jolly label
    instructionsLabel = tk.Label(text="Select table to search \nfor most common words", font=font, fg=txtColor, background=bgColor)
    instructionsLabel.grid(row=7, column=0)
    variable = StringVar(mainWindow)  # needed for drop down menu
    dropDownMenu = createDropdownMenu()
    dropDownMenu.grid(row=7, column=1, columnspan=2, sticky='W')
    freqBtn = tk.Button(mainWindow, text="Search Frequent Words", command=lambda: frequency(user, passW, schema))
    freqBtn.grid(row=7, column=3)

    contentBtn = tk.Button(mainWindow, text="Show Content", command=lambda: showContent(user, passW, schema))
    contentBtn.grid(row=8, column=1)

    teamFrame = tk.Frame(mainWindow, borderwidth=1, relief='sunken', bg=bgColor)
    teamLabel = tk.Label(teamFrame, text='Jolly Jaguars', font='Courier 20', fg=txtColor, bg=bgColor)
    teamLabel.pack()
    johnnyLabel = tk.Label(teamFrame, text='Johnny Nguyen', font=font, fg=txtColor, bg=bgColor)
    johnnyLabel.pack()
    jacobLabel = tk.Label(teamFrame, text='Jacob Johnson', font=font, fg=txtColor, bg=bgColor)
    jacobLabel.pack()
    inaLabel = tk.Label(teamFrame, text='Ina Edstrom', font=font, fg=txtColor, bg=bgColor)
    inaLabel.pack()
    leoLabel = tk.Label(teamFrame, text='Leo Deane', font=font, fg=txtColor, bg=bgColor)
    leoLabel.pack()
    teamFrame.grid(row=8, column=0)

    try: # this part checks for the jaguar image and places it in the GUI
        usaLogo = ImageTk.PhotoImage(file='usaLogo.png')
        logoLabel = Label(mainWindow, image=usaLogo, bg=bgColor)

    except:
        logoLabel = Label(mainWindow, text="Unable to open \nimage file", font=font, bg=bgColor, fg=txtColor)

    logoLabel.grid(row=8, column=3)

    print(mainWindow.grid_size())  # used for testing, prints the grid size to the console

    def updateDropdownMenu(u, p, s):  # used to automatically update the dropdown menu after polling a subreddit
        dbConnection = mysql.connector.connect(
            host=host,
            user=user,
            password=passW,
            database=schema,
            auth_plugin=auth_plugin
        )

        tables = pd.read_sql("SHOW TABLES;", con=dbConnection)
        atables = tables.iloc[:, 0].to_numpy()

        variable.set(atables[len(atables) - 1])  # default value

        dropDownMenu['menu'].delete(0, 'end')

        for tableName in atables:
            dropDownMenu['menu'].add_command(label=tableName, command=tk._setit(variable, tableName))

    def saveSubRedditComments(comment, post):  # this function retrieves the comments and stores them to MySQL db
        time = comment.created
        goodTime = datetime.fromtimestamp(time)
        date_time = goodTime.strftime("%m/%d/%Y, %H:%M:%S")

        now = datetime.now()
        timePolled = now.strftime("%m/%d/%Y, %H:%M:%S")

        # adds to global array, utf-8 to ensure safe characters
        subRedditComments.append([timePolled, comment.body.encode("utf-8"), post.title, comment.score, date_time])

    def pollRedditData(subRedditTitle, u, p, s):  # this function retrieves the reddit posts and stores them in MySQL db
        # outputField.delete("1.0", "end")
        # communicating to the API, where you will need to enter your credentials
        reddit_read_only = praw.Reddit(client_id=clientId,  # your client id
                                       client_secret=clientSecret,  # your client secret
                                       user_agent=userAgent)  # your user agent

        subreddit = reddit_read_only.subreddit(subRedditTitle)

        # Display the name of the Subreddit
        print("Display Name:", subreddit.display_name)

        # error catching
        try:
            postNum = int(postNumField.get("1.0", "end-1c"))
        except:
            outputField.insert(tk.END, "Post number must be a number")

        try:
            commentNum = int(commentNumField.get("1.0", "end-1c"))
        except:
            outputField.insert(tk.END, "Comment number must be a number")

        try:
            for post in subreddit.hot(limit=4):
                print("Testing valid subreddit")
        except:
            outputField.insert(tk.END, "Invalid Subreddit\n")
            return

        for post in subreddit.hot(limit=postNum):  # this loop polls the subreddit and builds the tables
            if not post.stickied:  # we dont want to pull stickied posts

                time = post.created
                goodTime = datetime.fromtimestamp(time)
                date_time = goodTime.strftime("%m/%d/%Y, %H:%M:%S")
                postTimes.append(date_time)

                now = datetime.now()
                timePolled = now.strftime("%m/%d/%Y, %H:%M:%S")

                subRedditPosts.append(
                    [timePolled, post.title, post.score, post.num_comments, post.selftext, post.link_flair_text,
                     date_time])  # theres more features that can be pulled but this is what we used

                postTitles.append(post.title)
                postContent.append(post.selftext)

                # code for getting comments-----------------------------------------------------------
                try:
                    print('Loading, Please Wait...\n')
                    submission = reddit_read_only.submission(post.id)

                    submission.comments.replace_more(limit=commentNum)
                    for comment in submission.comments.list():
                        saveSubRedditComments(comment, post)

                except:
                    print("Error fetching comments \n\n")

        # this section builds dataframes to easily manipulate the data
        posts = pd.DataFrame(subRedditPosts,
                             columns=['time_polled', 'title', 'score', 'num_comments', 'body', 'flair', 'time_posted'])
        # print(posts.to_string())

        comments = pd.DataFrame(subRedditComments,
                                columns=['time_polled', 'body', 'post_title', 'score', 'time_posted'])
        # print(comments.to_string())

        # inserting posts into mySQL
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                               .format(user=user,
                                       pw=passW,
                                       db=schema))

        time = timePolled.replace(',', '')
        time = time.replace(' ', '_')
        time = time.replace(':', '_')
        time = time.replace('/', '_')
        posts.to_sql(con=engine, name=str(subreddit) + '_' + time, if_exists='replace')
        comments.to_sql(con=engine, name=str(subreddit) + '_comments_' + time, if_exists='replace')

        # this part sends the reddit data to the GUI
        index = 0
        for post in postTitles:
            content = postContent[index]
            time = postTimes[index]
            index = index + 1
            outputField.insert(tk.END, post + "\n" + time + "\n" + content + "\n\n")

        updateDropdownMenu(u, p, s)  # updates dropdown menu
        subRedditPosts.clear()  # clears the lists of data for future use
        subRedditComments.clear()

    def showContent(u,p,s):  # this function builds the show content button, displays the post or comment data to the GUI
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passW,
            database=schema,
            auth_plugin=auth_plugin
        )
        print("value is:" + variable.get())
        df = pd.read_sql("select * from " + str(variable.get()) + ";", con=db_connection)
        if '_comments_' in str(variable.get()):  # since the comment and post tables are built different, its necessary to determine which one youre accessing
            content = df.values[:,[2, 3, 5]]
            outputCon = pd.DataFrame(content)
            conCSV = outputCon.to_csv(sep='\n',index=True, header=False)
            outputField.insert(tk.END, conCSV)  # this is the best way i (leo) could get the data displayed, im sure there are better ways
        else:
            content = df.values[:,[2, 3, 5, 7]]
            outputCon = pd.DataFrame(content)
            conCSV = outputCon.to_csv(sep='\n', index=True, header=False)
            outputField.insert(tk.END, conCSV+"\n--------------------------------------------------\n")


    def frequency(u, p, s):  # this function builds the search frequent words button, displays a table of most frequent words with their frequency
        db_connection = mysql.connector.connect(
            host=host,
            user=user,
            password=passW,
            database=schema,
            auth_plugin=auth_plugin
        )
        print("value is:" + variable.get())  # used for testing, prints name of db table to the console
        df = pd.read_sql("select * from " + str(variable.get()) + ";", con=db_connection)  # this grabs all the data from the table and puts it in a dataframe





        def tokenize(text):  # this part breaks the string data into pieces and pre processes them to be analyzed
            text = text.lower()
            text = text.translate(str.maketrans('', '', string.punctuation))
            tokens = nltk.word_tokenize(text)
            stop_words = set(stopwords.words('english'))  # stop word list that was imported earlier
            stop_words.add("’")  # there were a few words and punctuation that needed to be added to the stoplist
            stop_words.add("‘")
            stop_words.add("like")
            words = [token for token in tokens if not token in stop_words]
            return words

        word_freq = {}

        #  goes thru the list of tokenized wordds and counts them
        for index, row in df.iterrows():
            words = tokenize(row[2])

            for word in words:
                if word not in word_freq:
                    word_freq[word] = 1
                else:
                    word_freq[word] += 1

        df_word_freq = pd.DataFrame(list(word_freq.items()), columns=['word', 'frequency'])
        df_word_freq = df_word_freq.sort_values(by=['frequency'], ascending=False)
        topTen = (df_word_freq.head(10))  # creates the table and displays it to GUI, also could be changed to more or less than top 10
        outputField.insert(tk.END, topTen.to_string(index=False))
        outputField.insert(tk.END, "\n\n")

    mainWindow.mainloop()

def testDbConnection(u, p, s):  # tests the database connection
    try:
        dbConnection = mysql.connector.connect(
            host=host,
            user=u,
            password=p,
            database=s,
            auth_plugin=auth_plugin
        )
        return True

    except:
        return False



# -----------------------------------------------PROGRAM-STARTS-HERE-------------------------------------------------------------------

#test for file with db credentials, have sign again if file doesn't exist or credentials are wrong
if(os.path.isfile("Reddit_Credentials.txt")):
    redditInfo = open("Reddit_Credentials.txt")
    redditList = redditInfo.readlines()
    clientId = redditList[0].strip()
    clientSecret = redditList[1].strip()
    userAgent = redditList[2].strip()
    redditInfo.close()
    checkRedditCredentials(clientId, clientSecret, userAgent, tk.Tk())

else:
    signInReddit()

#should be written by this point
redditInfo = open("Reddit_Credentials.txt")
redditList = redditInfo.readlines()
clientId = redditList[0].strip()
clientSecret = redditList[1].strip()
userAgent = redditList[2].strip()
redditInfo.close()

#test for file with db credentials, have sign again if file doesn't exist or credentials are wrong
if(os.path.isfile("Db_Credentials.txt")):
    dbInfo = open("Db_Credentials.txt")
    redditList = dbInfo.readlines()
    u = redditList[0].strip()
    p = redditList[1].strip()
    s = redditList[2].strip()
    dbInfo.close()

    if(testDbConnection(u, p, s)):
        mainWindowFunc(u, p, s, tk.Tk())

    else:
        u, p, s = signInFunc()

else:
    u, p, s = signInFunc()