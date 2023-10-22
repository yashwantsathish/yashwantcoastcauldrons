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
        ids = connection.execute(sqlalchemy.text("SELECT DISTINCT potion_id FROM pot_ledgers"))

        ids = ids.first()
        print(ids)
        for id in ids:
            quant = connection.execute(sqlalchemy.text("SELECT SUM(potions_changed) FROM pot_ledgers "\
                                                       "WHERE potion_id = :id"),
                                                       {
                                                           "id": id
                                                       })
            quant = quant.first()[0]
            if quant == 0:
                continue
            potion = connection.execute(sqlalchemy.text("SELECT sku, price, num_red, num_green, num_blue, num_dark " \
                                               "FROM potions WHERE id = :id"), 
                                               {
                                                   "id": id
                                               })
            potion = potion.first()
            ret_list.append(
                {
                    "sku": potion.sku,
                    "name": potion.sku,
                    "quantity": quant,
                    "price": potion.price,
                    "potion_type": [potion.num_red, potion.num_green, potion.num_blue, potion.num_dark],
                }
            )
    
    print(ret_list)
    return ret_list
                
            
