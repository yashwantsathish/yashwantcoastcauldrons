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
        red_ml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_change) FROM ledger"))
        green_ml = connection.execute(sqlalchemy.text("SELECT SUM(green_ml_change) FROM ledger"))
        blue_ml = connection.execute(sqlalchemy.text("SELECT SUM(blue_ml_change) FROM ledger"))

        red_ml = red_ml.first()[0]
        blue_ml = blue_ml.first()[0]   
        green_ml = green_ml.first()[0]

        print("bottler post red: " + str(red_ml))
        print("bottler post green: " + str(green_ml))
        print("bottler post blue: " + str(blue_ml))

        to_make_red_ml = potions_delivered[0].potion_type[0]
        to_make_green_ml = potions_delivered[0].potion_type[1]
        to_make_blue_ml = potions_delivered[0].potion_type[2]

        print("to make green ml: " + str(to_make_green_ml))
        print("to make red ml: " + str(to_make_red_ml))

        quant = potions_delivered[0].quantity

        # Reflecting potion # change in potion ledger
        connection.execute(sqlalchemy.text("INSERT INTO pot_ledgers (potion_id, potions_changed) " \
                                   "SELECT id, :quant " \
                                   "FROM potions " \
                                   "WHERE num_red = :to_make_red_ml "  \
                                   "AND num_green = :to_make_green_ml " \
                                   "AND num_blue = :to_make_blue_ml"), 
                                   {
                                       "quant": quant,
                                       "to_make_red_ml": to_make_red_ml,
                                       "to_make_green_ml": to_make_green_ml,
                                       "to_make_blue_ml": to_make_blue_ml
                                   })
        
        red_ml_change = to_make_red_ml * quant
        green_ml_change = to_make_green_ml * quant 
        blue_ml_change = to_make_blue_ml * quant

        # Reflecting the use of ml to make the potions (changing ml values)
        connection.execute(sqlalchemy.text("INSERT INTO ledger (red_ml_change, green_ml_change, blue_ml_change) " \
                                           "VALUES (-:red_ml_change, -:green_ml_change, -:blue_ml_change)" \
                                            ), 
                                            {
                                                "red_ml_change": red_ml_change,
                                                "green_ml_change": green_ml_change,
                                                "blue_ml_change": blue_ml_change
                                            })

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

        red_ml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_change) FROM ledger"))
        blue_ml = connection.execute(sqlalchemy.text("SELECT SUM(blue_ml_change) FROM ledger"))
        green_ml = connection.execute(sqlalchemy.text("SELECT SUM(green_ml_change) FROM ledger"))

        red_ml = red_ml.first()[0]
        blue_ml = blue_ml.first()[0]
        green_ml = green_ml.first()[0]

        print("bottler- green ml: " + str(green_ml) + ", red ml: " + str(red_ml) + ", blue ml: " + str(blue_ml))

        query = connection.execute(sqlalchemy.text("SELECT * FROM potions " \
                                                   "WHERE :red_ml >= num_red " \
                                                   "AND :green_ml >= num_green " \
                                                   "AND :blue_ml >= num_blue " \
                                                   "ORDER BY price LIMIT 1"),
                                                   {
                                                       "red_ml": red_ml,
                                                       "green_ml": green_ml,
                                                       "blue_ml": blue_ml,
                                                   })
        
        query = query.first()
        if query is None:
            return []
        query_sku = query.sku
        query_red = query.num_red
        query_green = query.num_green
        query_blue = query.num_blue

        values = []
        if query_red > 0: 
            r_bottles = red_ml // query_red 
            values.append(r_bottles)
        if query_green > 0: 
            g_bottles = green_ml // query_green
            values.append(g_bottles) 
        if query_blue > 0: 
            b_bottles = blue_ml // query_blue 
            values.append(b_bottles)

        # Initialize a variable to store the minimum value
        min_value = 0

        # Iterate through the values
        for value in values:
            if value > 0:
                if min_value == 0 or value < min_value:
                    min_value = value
      
        print(str(query_sku) + ": [" + str(query_red) + ", " + str(query_green) + ", " + str(query_blue) + "]")

        return [
                    {
                        "potion_type": [query_red, query_green, query_blue, 0],
                        "quantity": min_value,
                    }
            ]


