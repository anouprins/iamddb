# project-anouprins

## IAMDDB
This app is made for all people who love to watch a serie or movie now and then, but lose track of where they left off, what movies they wanted to watch and what series they already have watched. 

This app allows the user to track series and movies in personal lists, watchlists and watched lists.

It is possible to search for movies and series, and go to a serie or movie page. On these pages it is possible to add the item to a list.

There are 2 standards lists given per user: watchlist and watched list. 

It is also possible to make custom lists.

For series it is also possible to check episodes as watched.

It is possible to add a review.

This app has a feature where the popularity score of the watchlist can be calculated and showed.
<img src="/read_me/serie_page.png" style="width: 50%;">
<img src="/read_me/taste_page.png" style="width: 50%;">
<img src="/read_me/watchlist_page.png" style="width: 50%;">
 
## screencast
 
 <video controls width="250">
    <source src="/read_me/screencastIAMDDB.webm" type="video/webm"></video>

## requirements

Flask

Flask-Session

Flask-SQLAlchemy

psycopg2-binary

SQLAlchemy

## run 

### run queries directly on database

sudo su - postgres

psql postgres

\c books;

### debugger in terminal

export DATABASE_URL="postgresql://postgres:horizontal_smeller18*@localhost/iamddb"

flask --app app.py --debug run

### create database

python3 create.py

### view web application

http://127.0.0.1:5000/
