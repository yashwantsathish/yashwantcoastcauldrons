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
    print("bottler post")
    print(potions_delivered)

    if not potions_delivered:
        return "OK"

    with db.engine.begin() as connection:
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))

        red_ml = red_ml.first()[0]
        blue_ml = blue_ml.first()[0]   
        green_ml = green_ml.first()[0]

        print("bottler post green: " + str(green_ml))
        print("bottler post red: " + str(red_ml))

        to_make_red_ml = potions_delivered[0].potion_type[0]
        to_make_green_ml = potions_delivered[0].potion_type[1]
        to_make_blue_ml = potions_delivered[0].potion_type[2]

        print("to make green ml: " + str(to_make_green_ml))
        print("to make red ml: " + str(to_make_red_ml))

        connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + 1 WHERE " \
                                           "num_red = :to_make_red_ml and num_green = :to_make_green_ml " \
                                           "and num_blue = :to_make_blue_ml"), 
                                           {    
                                                "to_make_red_ml": to_make_red_ml,
                                                "to_make_green_ml": to_make_green_ml,
                                                "to_make_blue_ml": to_make_blue_ml
                                           }
                        )
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory " \
                                           "SET num_red_ml = num_red_ml - :to_make_red_ml," \
                                           "num_green_ml = num_green_ml - :to_make_green_ml," \
                                           "num_blue_ml = num_blue_ml - :to_make_blue_ml"), 
                                           {    
                                                "to_make_red_ml": to_make_red_ml,
                                                "to_make_green_ml": to_make_green_ml,
                                                "to_make_blue_ml": to_make_blue_ml
                                           }
                        )   

    # #print(type(ml))
    # for pot in potions_delivered:
    #     if pot.potion_type[0] > 0:
    #         print("red")
    #         red_ml = pot.quantity * 100 
    #         red_potions = red_potions + pot.quantity
    #         with db.engine.begin() as connection:
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - " + str(red_ml)))
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = " + str(red_potions)))
    #     elif pot.potion_type[1] > 0:
    #         print("green")
    #         green_ml = green_ml - pot.quantity * 100 
    #         green_potions = green_potions + pot.quantity
    #         with db.engine.begin() as connection:
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = " + str(green_ml)))
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = " + str(green_potions))) 
    #     elif pot.potion_type[2] > 0:
    #         print("blue")
    #         blue_ml = blue_ml - pot.quantity * 100 
    #         blue_potions = blue_potions + pot.quantity
    #         with db.engine.begin() as connection:
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = " + str(blue_ml)))
    #             connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = " + str(blue_potions)))
        

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        print("bottler plan")
        # Each bottle has a quantity of what proportion of red, blue, and
        # green potion to add.
        # Expressed in integers from 1 to 100 that must sum up to 100.

        # Initial logic: bottle all barrels into red potions.
 
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))

        red_ml = red_ml.first()[0]
        blue_ml = blue_ml.first()[0]
        green_ml = green_ml.first()[0]

        print("bottler- green ml: " + str(green_ml) + ", red ml: " + str(red_ml) + ", blue ml: " + str(blue_ml))
        # num_green_potions = connection.execute(sqlalchemy.text(
        #     "SELECT quantity FROM potions WHERE sku = 'green'"
        #     ))

        # print(num_green_potions)

        query = connection.execute(sqlalchemy.text("SELECT sku FROM potions ORDER BY quantity LIMIT 1"))
        query = query.first()[0]
        
        # red_ml = red_ml.first()[0]
        # blue_ml = blue_ml.first()[0]
        # green_ml = green_ml.first()[0]


        # print("bottler- green ml: " + green_ml)
        # num_red_potions = red_ml // 100
        # num_blue_potions = blue_ml // 100
        # num_green_potions = green_ml // 100

        # print("ml: " + str(ml))

        if red_ml >= 50 and green_ml >= 50:
            return [
                    {
                        "potion_type": [100 , 50, 0, 0],
                        "quantity": 1,
                    }
                ]
        elif green_ml >= 50:
            return [
                    {
                        "potion_type": [0, 100, 0, 0],
                        "quantity": 1,
                    }
            ]
        else:
            return []


