import random
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

ids = set()
carts_dict = {}

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
    
    with db.engine.begin() as connection:
        id = connection.execute(sqlalchemy.text("INSERT INTO carts DEFAULT VALUES RETURNING id"))
        id = id.first()[0]
        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id) VALUES (" + str(id) + ")"))

    print("cart id: " + id)
    return {"cart_id": id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """     
    return carts_dict[cart_id]

class CartItem(BaseModel):
    quantity: int

   
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("set item quantity")
    print (str(cart_id) + ": " + item_sku + ", " + str(cart_item.quantity))
    print(cart_item)

    cart_item.quantity = 1

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE cart_items SET quantity = quantity + 1 " \
                                           "WHERE cart_id = :cart_id"),
                                           {
                                               "cart_id": cart_id
                                           }
                                           )
        
        connection.execute(sqlalchemy.text("UPDATE cart_items SET potion_id = potions.id " \
                                            "FROM potions " \
                                            "WHERE sku = :item_sku"), 
                                            {
                                                "item_sku": item_sku
                                            })
                                           
    #carts_dict[cart_id] = cart_item

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
        query = connection.execute(sqlalchemy.text("SELECT potion_id, quantity FROM cart_items " \
                                                   "WHERE cart_id = :cart_id"),
                                                   {
                                                       "cart_id":cart_id
                                                   })
        
        gold = connection.execute(sqlalchemy.text("SELECT gold from global_inventory"))
        gold = gold.first()[0]

        for row in query:
            id = row.potion_id
            print("potion id: " + str(id))
            quant = row.quantity
            num_bought += quant
            connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity - :quant " \
                                               "WHERE id = :id"),
                                               {
                                                   "quant": quant,
                                                   "id": id
                                               })
            gold_paid += 50*quant
        
        gold = gold + gold_paid
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :gold"),
                           {
                               "gold": gold
                           })

        return {"total_potions_bought": num_bought, "total_gold_paid": gold_paid}

