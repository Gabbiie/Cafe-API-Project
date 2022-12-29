from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
import os
from dotenv import load_dotenv

load_dotenv(".env")
API_KEY = os.getenv("KEY")

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Converts the columns and their values into a dictionary.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    """Home page"""
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    """Handles the get random cafe request."""
    # all_cafes =  db.session.query(Cafe).all()
    # random_cafe = random.choice(all_cafes)

    random_cafe = db.session.query(Cafe).order_by(func.random()).first()

    # Convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    """Handles the get all cafes request."""
    all_cafes = db.session.query(Cafe).all()
    # Convert the random_cafe data record to a dictionary of key-value pairs.
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search")
def get_cafe_at_location():
    """Handles the get cafe at a specific location request."""
    query_location = request.args.get("location")
    cafes = db.session.query(Cafe).filter_by(location=query_location).all()
    if cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/add", methods=["POST"])
def add_cafe():
    """Handles the add cafe post request."""
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilets")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("price"),
    )

    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    """Handles the update price patch request."""
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)

    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()

        return jsonify(response={"Success": "Successfully updated the price."}), 200

    else:
        # If resource is not found, return a 404 error.
        return jsonify(error={"Not found": "Sorry, a cafe with that id was not found in the database."}), 400


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    """Handles the delete cafe request."""
    api_key = request.args.get("api-key")

    if api_key == API_KEY:

        cafe = db.session.query(Cafe).get(cafe_id)

        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted a cafe from the database."}), 200
        else:
            return jsonify(error={"Not found": "Sorry, a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
