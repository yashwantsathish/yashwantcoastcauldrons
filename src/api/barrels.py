from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    ml_needed = 0
    cost = 0

    #Retrieving values from Database
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    # Getting retrieved value from tuple
    num_red_ml = num_red_ml.first()[0]
    gold = gold.first()[0]

    for barrel in barrels_delivered:
        ml_needed += barrel.ml_per_barrel * barrel.quantity
        cost += barrel.price * barrel.quantity
    
    updated_ml = num_red_ml - ml_needed
    updated_gold = gold - cost
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = " + str(updated_ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(updated_gold)))

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    ml = 0
    potion_type = 0
    price = 0
    num_barrels = 0

    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        money = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    num_red_potions = num_red_potions.first()[0]
    money = money.first()[0]

    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_RED_BARREL":
            ml = barrel.ml_per_barrel
            potion_type = barrel.potion_type
            price = barrel.price

    if num_red_potions < 10:
        num_barrels = 1

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "ml_per_barrel": ml,
            "potion_type": potion_type,
            "price": price,
            "quantity": num_barrels, 
        }
    ]
