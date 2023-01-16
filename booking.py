from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from passlib.context import CryptContext
import mysql.connector

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float

class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    id: int

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    if not user:
        return False
    if not verify_password(password, user[2]):
        return False
    return user

def create_user(db, user: User):
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (user.username, user.email, user.password))
    db.commit()

@app.post("/signup")
def signup(user: User):
    db = mysql.connector.connect(
        host='localhost',
        database='furniturecompany',
        user='root',
        password='Dell14@'
    )
    user.password = get_password_hash(user.password)
    create_user(db, user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: User):
    db = mysql.connector.connect(
        host='localhost',
        database='furniturecompany',
        user='root',
        password='Dell14@'
    )
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"message": "Logged in successfully"}

@app.get("/catalog")
def catalog():
    db = mysql.connector.connect(
        host='localhost',
        database='furniturecompany',
        user='root',
        password='Dell14@'
    )
    cursor = db.cursor()
    cursor.execute('SELECT id, name, description, price FROM items')
    items = cursor.fetchall()
    return items

@app.route('/place_order', methods=['POST'])
def place_order():
    user_id = request.json['user_id']
    items = request.json['items']
    total_price = request.json['total_price']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO orders (user_id, items, total_price, order_date, status) VALUES (%s, %s, %s, %s, 'pending')", (user_id, items, total_price, datetime.now()))
    mysql.connection.commit()
    cur.close()

    return jsonify({"message": "Order placed successfully."}), 200

@app.route('/cancel_order/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE id=%s", (order_id,))
    order = cur.fetchone()

    if order:
        if order[5] == 'approved':
            return jsonify({"message": "Order cannot be cancelled, it has already been approved."}), 400
        else:
            cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
            mysql.connection.commit()
            cur.close()
            return jsonify({"message": "Order cancelled successfully."}), 200
    else:
        return jsonify({"message": "Order not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
