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
        num_green = connection.execute(sqlalchemy.text("SELECT quantity FROM potions " \
                                                               "WHERE sku = 'green'"))
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))
        
    num_green = num_green.first()[0]
    num_green_ml = num_green_ml.first()[0]

    print("Catalog - green: " + str(num_green) + " gml: " + str(num_green_ml))
    
    # Can return a max of 6 unique skus.
    if num_green == 0:
        return []

    if(num_green > 0):
        ret_list.append(
                {
                    "sku": "green",
                    "name": "green",
                    "quantity": num_green,
                    "price":  50,
                    "potion_type": [0, 100, 0, 0],
                }
        )
    
    return ret_list
                
            
