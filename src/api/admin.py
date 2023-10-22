from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth   

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    with db.engine.begin() as connection:

        connection.execute(sqlalchemy.text("TRUNCATE ledger"))
        connection.execute(sqlalchemy.text("TRUNCATE pot_ledgers CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))

        connection.execute(sqlalchemy.text("INSERT INTO ledger (gold_change) VALUES (100)"))    
        
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Slo Pikachu",
        "shop_owner": "Yashwant Sathish Kumar",
    }

