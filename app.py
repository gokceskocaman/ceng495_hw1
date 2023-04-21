from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from bson.objectid import ObjectId
import db
app = Flask(__name__)
app.secret_key = 'soSecret'

login_manager = LoginManager()
login_manager.init_app(app)

class rating():
    def __init__(self, productId, rateValue, userId):
        self.productId = productId
        self.rateValue = rateValue
        self.userId = userId

class review():
    def __init__(self, productId, reviewText, userId, username):
        self.productId = productId
        self.reviewText = reviewText
        self.userId = userId
        self.username = username

class shopProduct():
    def __init__(self, type = None, name= None, desc= None, price= None,
                 seller= None, image= None, size= None,
                 colour= None, spec= None):
        self.type = type
        self.name = name
        self.desc = desc
        self.price = price
        self.seller = seller
        self.image = image
        self.size = size
        self.colour = colour
        self.spec = spec
        self.avarageRating = 0
        self.numRating = 0

class shopUser(UserMixin):
    def __init__(self, id, username, password, isAdmin):
        self.id = id
        self.username = username
        self.password = password
        self.isAdmin = isAdmin

    
@login_manager.user_loader
def load_user(user_id):
    user = db.db.users.find_one({'_id': ObjectId(user_id)})
    return shopUser(user['_id'], user['username'], user['password'], user['isAdmin'])

def get_products(productType = None):
    if type is None:
        products = db.db.products.find()
    else:
        products = db.db.products.find({'type': productType})
    return products

@app.route('/')
def home():
    isLoggedIn = current_user.is_authenticated
    products = get_products()
    return render_template('home.html', products= products, isLoggedIn= isLoggedIn)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out.')
    return redirect(url_for('home'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

    user = db.db.users.find_one({'username': username, 'password': password})

    if user is None:
        flash('Invalid Login.')
    else:
        user = shopUser(user['_id'], user['username'], user['password'], user['isAdmin'])
        login_user(user)
        flash('You are logged in.')

    return redirect(url_for('home'))

@app.route("/rateProduct/<productId>", methods=['POST', 'GET'])
@login_required
def rateProduct(productId):
    if request.method == "POST":
        rateVal = request.form.get("rate")

    userId = current_user.id

    db.db.ratings.insert_one({'productId': ObjectId(productId), 'rateValue':rateVal, 'userId':ObjectId(userId)})

    return redirect(url_for('productDisplay', productId=productId))
    

@app.route("/reviewProduct/<productId>", methods=['POST', 'GET'])
@login_required
def reviewProduct(productId):
    if request.method == "POST":
        reviewText = request.form.get("review")
    
    userId = current_user.id
    userName = current_user.username
    
    db.db.reviews.insert_one({'productId': ObjectId(productId), 'reviewText': reviewText, 'userId':ObjectId(userId), 'userName': userName})
    return redirect(url_for('productDisplay', productId=productId))

@app.route("/productDisplay/<productId>", methods=['POST', 'GET'])
def productDisplay(productId):
    product = db.db.products.find_one({'_id': ObjectId(productId)})
    reviews = db.db.reviews.find({"productId": ObjectId(productId)})
    ratings = db.db.ratings.find({"productId": ObjectId(productId)})

    cnt = 0
    avgRating = 0.0
    for rating in ratings:
        avgRating += float(rating['rateValue'])
        cnt += 1
    avgRating /= cnt if cnt != 0 else 1

    return render_template('productDisplay.html', isLoggedIn=current_user.is_authenticated, product=product, reviews=reviews, avgRating=avgRating)

@app.route('/seeUser', methods=['POST'])
def seeUser():
    user = db.db.users.find_one({'username': 'admin', 'password': 'admin'})
    
    id = user['_id']
    username = user['username']
    password = user['password']
    isAdmin = user['isAdmin']

    user = shopUser(id,username,password,isAdmin)
    userList = [user]

    return render_template('addUser.html', user=user, userList=userList)

@app.route('/addProduct')
def addProduct():
    db.db.products.insert_one({"name": 'Nintendo', "desc": 'It is a fully functional linux computer that can do most things a full system can (games, web stuff, videos, music etc). You can also output the video to an external monitor, transforming it into a desktop-ish computer. ', "price": 150.50, 
                              "seller": 'Kerim', "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSXroRDVVa4McfpCaIgSnE_KDaL2zjP7j0yU2nd7y8JHxiJqGkQ5bDvFHg5PUuZ8gxrmCU&usqp=CAU",
                              "colour": 'black'})
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(port=8000)