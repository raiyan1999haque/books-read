from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- CLOUDINARY CONFIGURATION ---
cloudinary.config( 
  cloud_name = "YOUR_CLOUD_NAME", 
  api_key = "YOUR_API_KEY", 
  api_secret = "YOUR_API_SECRET" 
)

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
    cover_url = db.Column(db.String(500)) 
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
    file = request.files.get('cover_file')
    image_url = ""
    
    if file:
        # Uploads your local file directly to the cloud
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']
    
    new_book = Book(
        title=request.form.get('title'),
        authors=request.form.get('authors'),
        edition=request.form.get('edition'),
        publisher=request.form.get('publisher'),
        pub_year=request.form.get('pub_year'),
        cover_url=image_url
    )
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
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
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
