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

    with db.engine.begin() as connection:
        num_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        
    num_potions = num_potions.first()[0]
    # Can return a max of 6 unique skus.
    if  num_potions == 0:
        return []
    else:
        return [
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": num_potions,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                },  
            ]
