from fastapi import FastAPI, HTTPException, Depends, Body
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from sqlalchemy.orm import declarative_base

Base = declarative_base()
app = FastAPI()

class Customer(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class Order(BaseModel):
    id: int
    customer_id: int
    is_approved: bool
    is_fulfilled: bool


DATABASE_URL = "mysql://root:password@localhost:3306/furniturecompany"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CustomerModel(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True)
    is_active = Column(Boolean, default=True)

class OrderModel(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, index=True)
    is_approved = Column(Boolean, default=False)
    is_fulfilled = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

@app.post("/admin/login")
def admin_login(username: str, password: str):
    if username == "admin" and password == "password":
        return {"message": "Logged in successfully"}
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

@app.post("/admin/create_customer")
def create_customer(customer: Customer):
    db = SessionLocal()
    db_customer = CustomerModel(username=customer.username, email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return {"message": "Customer created successfully", "customer_id": db_customer.id}

@app.post("/admin/edit_customer/{customer_id}")
def edit_customer(customer_id: int, customer: Customer):
    db = SessionLocal()
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer:
        db_customer.username = customer.username
        db_customer.email = customer.email
        db.commit()
        return {"message": "Customer updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")


@app.post("/admin/deactivate_customer/{customer_id}")
def deactivate_customer(customer_id: int):
    db = SessionLocal()
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer:
        db_customer.is_active = False
        db.commit()
        return {"message": "Customer deactivated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Customer not found")

@app.post("/admin/approve_order/{order_id}")
def approve_order(order_id: int):
    db = SessionLocal()
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order:
        db_order.is_approved = True
        db.commit()
        return {"message": "Order approved successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")


@app.post("/admin/approve_order/{order_id}")
def approve_order(order_id: int):
    db = SessionLocal()
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order:
        db_order.is_approved = True
        db.commit()
        return {"message": "Order approved successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")

@app.post("/admin/mark_fulfilled/{order_id}")
def mark_fulfilled(order_id: int):
    db = SessionLocal()
    db_order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if db_order:
        db_order.is_fulfilled = True
        db.commit()
        return {"message": "Order marked as fulfilled successfully"}
    else:
        raise HTTPException(status_code=404, detail="Order not found")