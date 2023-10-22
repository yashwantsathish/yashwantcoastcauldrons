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
        name = new_cart.customer
        id = connection.execute(sqlalchemy.text("INSERT INTO carts (name) VALUES(:name) RETURNING id"), 
                                {
                                    "name": name
                                })
        id = id.first()[0]

    print("cart id: " + str(id))
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

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, quantity, potion_id) " \
                                           "SELECT :id, :quantity, id " \
                                           "FROM potions WHERE sku = :item_sku"),  
                    {
                        "id": cart_id,
                        "quantity": cart_item.quantity, 
                        "item_sku": item_sku
                    })

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
        # Getting potion_id, quantity, price columns for given cart items
        query = connection.execute(sqlalchemy.text("SELECT potion_id, cart_items.quantity, potions.price FROM cart_items " \
                                                   "JOIN potions ON potion_id = potions.id " \
                                                   "WHERE cart_id = :cart_id"),
                                                   {
                                                       "cart_id": cart_id
                                                   })
        # Iterating through all cart items for given cart
        for row in query:
            id = row.potion_id
            price = row.price
            print("potion id: " + str(id) + " price: " + str(price))
            quant = row.quantity
            num_bought += quant
            
            connection.execute(sqlalchemy.text("INSERT INTO pot_ledgers (potion_id, potions_changed) " \
                                               "VALUES (:id, -:quant) "),
                                               {
                                                   "id": id,
                                                   "quant": quant
                                               })
            gold_paid += price * quant
        
        # gold = gold + gold_paid
        connection.execute(sqlalchemy.text("INSERT INTO ledger (gold_change) VALUES (:gold_paid)"), 
                           {
                               "gold_paid": gold_paid
                           })

        return {"total_potions_bought": num_bought, "total_gold_paid": gold_paid}

