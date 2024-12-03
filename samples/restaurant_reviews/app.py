# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from azure.cloudmachine.ext.flask import CloudMachine


from models import Restaurant, Review


app = Flask( 
    __name__,
    template_folder='templates',
    static_folder='static'
)


cm = CloudMachine(
    app=app,
    name='restaurantreviewapp'
)


@app.route('/', methods=['GET'])
def index():
    restaurants = list(cm.data.list(Restaurant))
    return render_template('index.html', restaurants=restaurants)


@app.route('/<id>', methods=['GET'])
def details(id):
    restaurant = next(cm.data.query(Restaurant, id, '*'), None)
    if not restaurant:
        return '<h1>404</h1><p>Restaurant not found!</p><img src="https://httpcats.com/404.jpg" alt="cat in box" width=400>', 404
    reviews = list(cm.data.query(Review, '*', id))
    return render_template('details.html', restaurant=restaurant, reviews=reviews)


@app.route('/create', methods=['GET'])
def create_restaurant():
    return render_template('create_restaurant.html')


@app.route('/add', methods=['POST'])
def add_restaurant():
    name = request.values.get('restaurant_name')
    street_address = request.values.get('street_address')
    description = request.values.get('description')
    if not name or not street_address:
        error="You must include a restaurant name and address."
        return render_template('create_restaurant.html', error=error)
    else:
        restaurant = Restaurant(
            name=name,
            street_address=street_address,
            description=description
        )
        cm.data.insert(restaurant)
    return redirect(url_for('details', id=restaurant.id))


@app.route('/review/<id>', methods=['POST'])
def add_review(id):
    user_name = request.values.get('user_name')
    rating = request.values.get('rating')
    review_text = request.values.get('review_text')

    review = Review(
        restaurant=id,
        user_name=user_name,
        rating=int(rating),
        review_text=review_text,
        review_date=datetime.now()
    )
    cm.data.upsert(review)
    return redirect(url_for('details', id=id))


@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = cm.data.query(Review, '*', id)
        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}
    return dict(star_rating=star_rating)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


if __name__ == '__main__':
    app.run()
