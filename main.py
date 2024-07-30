from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"

# Crearte Extension
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Books(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)

    # this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# Create table schema in the database. Requires application context.
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    with app.app_context():
        all_books = list(db.session.execute(db.select(Books).order_by(Books.title)).scalars())
        new_book = []
        for book in all_books:
            added_book = {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "rating": book.rating
            }
            new_book.append(added_book)
    return render_template("index.html", my_books=new_book)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # with app.app_context():
        new_book = Books(
            title=request.form["title"],
            author=request.form["author"],
            rating=request.form["rating"]
        )
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template("add.html")


@app.route("/edit_rating", methods=["GET", "POST"])
def edit_rating():
    if request.method == "POST":
        book_id = request.form["id"]
        book_detail = db.get_or_404(Books, book_id)
        book_detail.rating = request.form["new_rating"]
        db.session.commit()
        return redirect(url_for('home'))
    book_id = request.args.get('id')
    book_selected = db.get_or_404(Books, book_id)
    return render_template("edit_rating.html", book_detail=book_selected, id=book_id)


@app.route("/delete")
def delete_book():
    book_id = request.args.get('book_id')
    book_to_delete = db.get_or_404(Books, book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
