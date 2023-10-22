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

        print(barrels_delivered)

        for barrel in barrels_delivered:
            #Only if enough gold
            if barrel.sku == "MINI_GREEN_BARREL":
                print("barrel: green")
                num_ml = barrel.ml_per_barrel * barrel.quantity
                print("green: " + str(num_ml))
                connection.execute(sqlalchemy.text("INSERT INTO ledger (green_ml_change) VALUES (:num_ml)"),
                                {
                                    "num_ml": num_ml
                                })

            elif barrel.sku == "MINI_RED_BARREL":
                print("barrel: red")
                num_ml = barrel.ml_per_barrel * barrel.quantity
                print("red: " + str(num_ml))
                connection.execute(sqlalchemy.text("INSERT INTO ledger (red_ml_change) VALUES (:num_ml)"),
                                {
                                    "num_ml": num_ml
                                })
                
            elif barrel.sku == "MINI_BLUE_BARREL":
                print("barrel: blue")
                num_ml = barrel.ml_per_barrel * barrel.quantity
                print("blue: " + str(num_ml))
                connection.execute(sqlalchemy.text("INSERT INTO ledger (blue_ml_change) VALUES (:num_ml)"),
                                {
                                    "num_ml": num_ml
                                })
                
            #Retrieving values from Database
            cost = 0
            cost += barrel.price 
            print("barrel post cost: " + str(cost))
            
            connection.execute(sqlalchemy.text("INSERT INTO ledger (gold_change) VALUES (-:cost)"),
                                {
                                    "cost": cost
                                })
        
        gold = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM ledger"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT SUM(green_ml_change) FROM ledger"))
        num_red_ml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_change) FROM ledger"))
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT SUM(blue_ml_change) FROM ledger"))

        # Getting retrieved value from tuple
        num_green_ml = num_green_ml.first()[0]
        num_red_ml = num_red_ml.first()[0]
        num_blue_ml = num_blue_ml.first()[0]

        print("green (should be 200): " + str(num_green_ml))
        print("red (should be 200): " + str(num_red_ml))
        print("blue (should be 200): " + str(num_blue_ml))

        gold = gold.first()[0]
        print(gold)    

        return "OK"


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print("barrel plan")
    print(wholesale_catalog)

    ret_list = []

    with db.engine.begin() as connection:
          money = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM ledger"))
    
    money = money.first()[0]

    print("current gold:" + str(money))
    
    for barrel in wholesale_catalog:
        print(money)
        if money < 60:
            return ret_list
        if barrel.sku == "MINI_RED_BARREL":
            print("buying mini red barrel")
            money = money - 60
            ret_list.append(
                {
                    "sku": "MINI_RED_BARREL",
                    "quantity": 1,
                }
            )

        elif barrel.sku == "MINI_GREEN_BARREL":
            print("buying mini green barrel")
            money = money - 60
            ret_list.append(
                {
                    "sku": "MINI_GREEN_BARREL",
                    "quantity": 1,
                }
            )    
              
        elif barrel.sku == "MINI_BLUE_BARREL":
            print("buying mini blue barrel")
            money = money - 60
            ret_list.append(
                {
                    "sku": "MINI_BLUE_BARREL",
                    "quantity": 1,
                }
            )
    
    return ret_list
    
