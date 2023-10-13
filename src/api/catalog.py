from fastapi import APIRouter

router = APIRouter()

import sqlalchemy
from src import database as db

@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    #Potion Catalog
    print("Catalog")

    ret_list = []

    with db.engine.begin() as connection:
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))
        
    num_red_potions = num_red_potions.first()[0]
    num_green_potions = num_green_potions.first()[0]
    num_blue_potions = num_blue_potions.first()[0]

    print("Catalog - red: " + str(num_red_potions) + " blue: " + str(num_blue_potions) + " green: " + str(num_green_potions))
    # Can return a max of 6 unique skus.
    if  num_red_potions + num_green_potions + num_blue_potions == 0:
        return []

    if(num_red_potions > 0):
        ret_list.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": num_red_potions,
                    "price":  1,
                    "potion_type": [100, 0, 0, 0],
                }
        )
    if(num_green_potions > 0):
        ret_list.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": num_green_potions,
                    "price": 1,
                    "potion_type": [0, 100, 0, 0],
                }
        )
    if(num_blue_potions > 0):
        ret_list.append(
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": num_blue_potions,
                    "price": 1,
                    "potion_type": [0, 0, 100, 0],
                }
        )
    
    return ret_list
                
            
