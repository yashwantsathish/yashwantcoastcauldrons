from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    print("audit")
    with db.engine.begin() as connection:
        potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potions"))

        ml = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_blue_ml, num_green_ml FROM global_inventory"))

        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    num_potions = 0
    for row in potions:
        num_potions += row.quantity

    num_ml = 0
    for row in ml:
        num_ml += row.num_red_ml + row.num_green_ml + row.num_blue_ml  
    
    gold = gold.first()[0]

    print("Audit- " + "number_of_potions: " + str(num_potions) + " ml_in_barrels: " + str(num_ml) + " gold: " + str(gold))

    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
