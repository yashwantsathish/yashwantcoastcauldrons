from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """    
    print("create cart")
    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """     
    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("set item quantity")
    print (str(cart_id) + ": " + item_sku)
    print(cart_item)
    cart_item.quantity = 1
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("checkout")
    gold = 0 

    num_bought = 0
    gold_paid = 0


    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))

    gold = gold.first()[0]
    num_red_potions = num_red_potions.first()[0]
    num_green_potions = num_green_potions.first()[0]
    num_blue_potions = num_blue_potions.first()[0]

    if num_red_potions >= 1:
        print("red bought")
        num_bought = num_bought + 1
        gold_paid = gold_paid + 50
        num_red_potions = num_red_potions - 1

    if num_green_potions >= 1:
        print("green bought")
        num_bought = num_bought + 1
        gold_paid = gold_paid + 50
        num_green_potions = num_green_potions - 1

    if num_blue_potions >= 1:
        print("blue bought")
        num_bought = num_bought + 1
        gold_paid = gold_paid + 50
        num_blue_potions = num_blue_potions - 1

    gold = gold + gold_paid

    if num_bought > 0:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(gold)))
            num_red_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(num_red_potions)))
            num_green_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + str(num_green_potions)))
            num_blue_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = " + str(num_blue_potions)))

    print(str(num_bought) + ", " + str(gold_paid))

    return {"total_potions_bought": num_bought, "total_gold_paid": gold_paid}
