How to use the program:

-Before starting the program you will need to create a MySQL schema that will be dedicated to the use of this program (tables will be created automatically by RedTED). Be sure to remember your MySQL sign-in info and the name of the schema you created.

-First, you will need to enter your Reddit API information from your
 reddit account. Link to get started using PRAW (Python Reddit API Wrapper): https://praw.readthedocs.io/en/stable/getting_started/quick_start.html

-Second, you will need to enter your MySQL username, password, and
 the name of the schema you will be reading/writing to.

-You can enter the name of the subreddit you wish to save data from, the
 number of posts you want to save, and the level of comments you want to
 save. Then you click you the "Poll subreddit" button. This will create 
 two new tables in your db that will save top-level posts and comments 
 below them, respectively

-A drop down menu will contain all of the tables names stored in your 
 database. When you select the table, you can perform most common word
 analysis with the "Search frequent words" button

-You can also display the post and comments saved to the table with the
 "Show Content" button
