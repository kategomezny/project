from flask import (Flask,  render_template, request, g, session, flash, 
                   redirect, url_for, make_response)
import sqlite3 as lite
from contextlib import closing
import urllib2
import json
import datetime
""" Final Project - Book Catalogue"""


DATABASE = 'booksapp12.db'
SECRET_KEY = '@\x96\xe4.\x1d\xe9M`\xe8C\x8e?\x17:\x1ee\xafBm^u-\xb4z'
API_GOOGLE = "https://www.googleapis.com/books/v1/volumes?q=isbn:"


app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return lite.connect(app.config['DATABASE'])


def init_db():

        with closing(connect_db()) as db:
            with app.open_resource('schema.sql',mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()


@app.before_request
def before_request():
    g.db = connect_db()
    

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
    con = lite.connect(DATABASE)
    
    
@app.route('/home')
def index():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO USERS (user_first_name, user_last_name, user_name, password) values ('" + request.form['user_first_name'] + "', '" + request.form['user_last_name'] + "', '" + request.form['user_name'] + "', '" + request.form['password'] + "')" )
        conn.commit()
        flash('New user has been create sucessfully')
        response = make_response(render_template('booklist.html', user_name=request.form['user_name']))
        response.set_cookie('CurrentSessionCookie', request.form['user_name'])
        conn.close()
        return response              
    else:
        return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT password FROM USERS WHERE user_name = '" + request.form['username'] + "'")
        current_user_password = cur.fetchone()
        conn.close()
        if current_user_password is None:            
            error= "Username does not exist.   Please enter a valid username" 
            return render_template('login.html', error=error)
        else:
            if request.form['password'] == str(current_user_password[0]):
                response = make_response(redirect(url_for('booklist')))
                response.set_cookie('CurrentSessionCookie', request.form['username'])
                return response
            else:
                error= "Invalid username or password.   Please try again" 
                return render_template('login.html', error=error)
            
    else:
        return render_template('login.html', error=error)
            

@app.route('/booklist')
def booklist():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT BOOKS.ISBN, BOOKS.title, BOOKS.page_count, BOOKS.average_rating, BOOKS.author_name,  USERS_BOOKS.Saved_date FROM BOOKS,  USERS_BOOKS  WHERE USERS_BOOKS.user_name = '" +  request.cookies.get('CurrentSessionCookie') + "' and USERS_BOOKS.ISBN=BOOKS.ISBN")
    BOOK_RESULTS= cur.fetchall()
    conn.close()
    return render_template('booklist.html', book_results=BOOK_RESULTS, user_name = request.cookies.get('CurrentSessionCookie'))


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'POST':
        search_isbn = request.form['ISBN']
        if search_isbn == "":
            flash("Please Enter an ISBN Number")
            return render_template('search.html', "'" + str(user_name=request.cookies.get('CurrentSessionCookie'))+"'")
        else:
            try:
                url = API_GOOGLE + search_isbn
                html = urllib2.urlopen(url)
                data = html.read()               
                data = json.loads(data)
                volumeinfo = data['items'][0]['volumeInfo']
                book_title = volumeinfo['title']
                book_authors = volumeinfo['authors'][0]
                page_count = volumeinfo['pageCount']
                return render_template('search.html',
                                       title=book_title, authors=book_authors,
                                       pagecount=page_count, isbn=search_isbn,
                                       user_name=str(request.cookies.get('CurrentSessionCookie')))
            except LookupError:
               flash("The ISBN didn't return any results")
               return redirect(url_for('search'))
    if request.method == 'GET':
        return render_template('search.html', title=None)
    
    
@app.route('/addbook/<string:ISBN>/<string:title>/<string:authors>/<int:pageCount>/')
def addbook(ISBN, title, authors, pageCount):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO BOOKS (ISBN, title, author_name, page_count) values('" + ISBN +"', '" + title.replace("'","''") + "', '" + authors.replace("'","''") + "', " + str(pageCount) + ")")  
        conn.commit()
        cur.execute("INSERT OR REPLACE INTO USERS_BOOKS (user_name, ISBN, Saved_Date) values('" + str(request.cookies.get('CurrentSessionCookie')) +"', '" + str(ISBN) + "','" + str(datetime.datetime.now()) + "')")
        conn.commit()
        conn.close()
        return redirect(url_for('booklist'))
    

@app.route('/deletebook/<string:ISBN>/')
def delete_book(ISBN):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM USERS_BOOKS WHERE user_name='" + str(request.cookies.get('CurrentSessionCookie')) +"' and ISBN= '" + str(ISBN) + "'")
        conn.commit()
        conn.close()
        return redirect(url_for('booklist'))
  

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You were logged out")
    response = make_response(redirect(url_for('login')))
    response.set_cookie('CurrentSessionCookie', 'No User Logged')
    return response


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
