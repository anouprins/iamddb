# project-anouprins

## IAMDDB

This app allows the user to track series and movies in personal lists.
It is possible to search for movies and series, and go to a serie or movie page. On these pages it is possible to add the item to a list.
There are 2 standards lists given per user: watchlist and watched list.
It is also possible to make custom lists.
For series it is also possible to check episodes as watched.
It is possible to add a review.
This app has a feature where the popularity score of the watchlist can be calculated and showed.

## source

To retrieve movie and serie data, this apps uses the TMDB database.
When moving to serie or movie page, the app adds the relevant data to the IAMDDB database if not already there.

Source: https://developer.themoviedb.org/docs

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
