from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Render uses an environment variable for the database path, or falls back to local sqlite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200))
    edition = db.Column(db.String(100))
    publisher = db.Column(db.String(200))
    pub_year = db.Column(db.String(20))
    cover_image_url = db.Column(db.String(500)) # Changed to URL for permanent live storage
    quotes = db.relationship('Quote', backref='book', lazy=True, cascade="all, delete-orphan")

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100)) 
    personal_note = db.Column(db.Text)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    new_book = Book(
        title=request.form.get('title'),
        authors=request.form.get('authors'),
        edition=request.form.get('edition'),
        publisher=request.form.get('publisher'),
        pub_year=request.form.get('pub_year'),
        cover_image_url=request.form.get('cover_url') # Accepts URL now
    )
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/book/<int:book_id>/add_quote', methods=['POST'])
def add_quote(book_id):
    new_quote = Quote(
        content=request.form.get('content'),
        location=request.form.get('location'),
        personal_note=request.form.get('personal_note'),
        book_id=book_id
    )
    db.session.add(new_quote)
    db.session.commit()
    return redirect(url_for('book_detail', book_id=book_id))

if __name__ == '__main__':
    # Use environment port for Render
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
