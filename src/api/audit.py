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
        num_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        num_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory"))
        num_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory"))

        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory"))
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory"))

        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    num_red_potions = num_red_potions.first()[0]
    num_green_potions = num_green_potions.first()[0]
    num_blue_potions = num_blue_potions.first()[0]
    num_potions = num_red_potions + num_green_potions + num_blue_potions

    red_ml = red_ml.first()[0]
    blue_ml = blue_ml.first()[0]
    green_ml = green_ml.first()[0]
    num_ml = red_ml + green_ml + blue_ml

    gold = gold.first()[0]

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
