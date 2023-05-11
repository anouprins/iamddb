# project-anouprins


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
