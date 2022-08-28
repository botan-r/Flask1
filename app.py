from flask import Flask, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic',cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Author[{self.id}]: {self.name}"
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def __repr__(self):
        return f"Quote[{self.id}]: {self.author_id} {self.text}"

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "text": self.text
        }


# Сериализация: lis[quotes] --> list[dict] --> str(JSON)
@app.route("/quotes")
def get_all_quotes():
    quotes = QuoteModel.query.all()
    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


@app.route("/quotes/<int:id>")
def get_quote(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        return {"error": f"Quote with id={id} not found"}, 404
    return quote.to_dict(), 200


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    if author is None:
        return {"error": f"Author with id={id} not found"}, 404
    new_quote = request.json
    q = QuoteModel(author, new_quote["text"])
    db.session.add(q)
    db.session.commit()
    return q.to_dict(), 201


@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    quote_data = request.json
    quote = QuoteModel.query.get(id)
    if quote is None:
        return {"error": f"Quote with id={id} not found"}, 404
    # if quote_data.get("text"):
    #     quote.text = quote_data['text']
    # if quote_data.get("author"):
    #     quote.author = quote_data['author']
    for key, value in quote_data.items():
        setattr(quote, key, value)
    db.session.commit()
    return quote.to_dict(), 200


@app.route("/quotes/filter")
def get_quotes_filter():
    args = request.args
    print(args)
    # TODO: закончить реализацию
    return {}


@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete(id):
    quote = QuoteModel.query.get(id)
    if quote is None:
        return {"error": f"Quote with id={id} not found"}, 404
    db.session.delete(quote)
    db.session.commit()
    return {"message": f"Quote with id={id} deleted"}, 200


@app.route("/authors")
def get_all_authors():
    authors = AuthorModel.query.all()
    authors_dict = []
    for author in authors:
        authors_dict.append(author.to_dict())
    return authors_dict

@app.route("/authors", methods=['POST'])
def create_author():
    author_data = request.json
    author = AuthorModel(author_data["name"])
    db.session.add(author)
    db.session.commit()
    return author.to_dict()

@app.route("/authors/<int:id>", methods=['PUT'])
def edit_author(id):
    author_data = request.json
    author = AuthorModel.query.get(id)
    if author is None:
        return {"error": f"Author with id={id} not found"}, 404
    for key, value in author_data.items():
        if key == 'id':
            continue
        setattr(author, key, value)
    db.session.commit()
    return author.to_dict(), 200


@app.route("/author/<int:id>", methods=['DELETE'])
def delete_author(id):
    author = AuthorModel.query.get(id)
    if author is None:
        return {"error": f"Author with id={id} not found"}, 404
    db.session.delete(author)
    db.session.commit()
    return {"message": f"Author with id={id} deleted"}, 200

if __name__ == "__main__":
    app.run(debug=True)