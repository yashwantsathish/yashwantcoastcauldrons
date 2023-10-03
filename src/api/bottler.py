from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    ml_needed = 0
    potions_needed = 0

    with db.engine.begin() as connection:
        ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))

    ml = ml.first()[0]
    potions = potions.first()[0]

    for pot in potions_delivered:
        ml_needed = ml_needed + pot.quantity * 100
        potions_needed = potions_needed + pot.quantity

    ml = ml - ml_needed
    potions = potions + potions_needed

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = " + str(ml)))
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(potions)))
    
    print(ml_needed)

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.

    with db.engine.begin() as connection:
        ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))

    ml = ml.first()[0]
    num_potions = ml // 100

    print("ml: " + str(ml))

    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": num_potions,
            }
        ]

