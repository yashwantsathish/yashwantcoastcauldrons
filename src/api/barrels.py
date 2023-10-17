import random
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

import datetime

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
    with db.engine.begin() as connection:
        print("barrel post")

        cost = 0
        num_ml = 0

        print(barrels_delivered)
        barrel = barrels_delivered[0]

        #Only if enough gold
        if barrel.sku == "MINI_GREEN_BARREL":
            print("barrel: green")
            num_ml = barrel.ml_per_barrel * barrel.quantity
            print("green: " + str(num_ml))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + " + str(num_ml)))

        elif barrel.sku == "MINI_RED_BARREL":
            print("barrel: red")
            num_ml = barrel.ml_per_barrel * barrel.quantity
            print("red: " + str(num_ml))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + " + str(num_ml)))
        else:
            print("barrel: blue")
            num_ml = barrel.ml_per_barrel * barrel.quantity
            print("blue: " + str(num_ml))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + " + str(num_ml)))

        #Retrieving values from Database
       
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))

        # Getting retrieved value from tuple
        num_green_ml = num_green_ml.first()[0]
        num_red_ml = num_red_ml.first()[0]
        num_blue_ml = num_blue_ml.first()[0]

        print("green (should be 200): " + str(num_green_ml))
        print("red (should be 200): " + str(num_red_ml))
        print("blue (should be 200): " + str(num_blue_ml))

        gold = gold.first()[0]
        print(gold)

        cost = cost + barrel.price 
        print("barrel post cost: " + str(cost))
        
        updated_gold = gold - cost
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = " + str(updated_gold)))

        return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("barrel plan")
    print(wholesale_catalog)

    ret_list = []
    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        money = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))

    num_red_potions = num_red_potions.first()[0]
    money = money.first()[0]
    num_green_potions = num_green_potions.first()[0]
    num_blue_potions = num_blue_potions.first()[0]

    num_potions = num_red_potions + num_blue_potions + num_green_potions
   
    print("current gold:" + str(money))
    #Get current hour
    # current_datetime = datetime.datetime.now()
    # hour = current_datetime.hour   
    # print("hour: " + str(hour)) 

    index = random.randint(0, 2)
    
    for barrel in wholesale_catalog:
        if money < 60:
            return ret_list
        if barrel.sku == "MINI_RED_BARREL" and (index >= 0):
            print("buying mini red barrel")
            money = money - 60
            ret_list.append(
                {
                    "sku": "MINI_RED_BARREL",
                    "quantity": 1,
                }
            )
        elif barrel.sku == "MINI_GREEN_BARREL" and (index >= 0):
            print("buying mini green barrel")
            money = money - 60
            ret_list.append(
                {
                    "sku": "MINI_GREEN_BARREL",
                    "quantity": 1,
                }
            )      
        elif barrel.sku == "MINI_BLUE_BARREL" and (index < 0):
            print("buying mini blue barrel")
            which_barrel = 0
            return [
                {
                    "sku": "MINI_BLUE_BARREL",
                    "quantity": 1,
                }
            ]
    
