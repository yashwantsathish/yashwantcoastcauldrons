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
        number_of_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        ml_in_barrels = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    return {"number_of_potions": number_of_potions.first()[0], "ml_in_barrels": ml_in_barrels.first()[0], "gold": gold.first()[0]}

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
