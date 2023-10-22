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
        num_potions = connection.execute(sqlalchemy.text("SELECT SUM(potions_changed) FROM pot_ledgers"))

        num_ml = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_change + green_ml_change + blue_ml_change) FROM ledger"))

        num_gold = connection.execute(sqlalchemy.text("SELECT SUM(gold_change) FROM ledger"))

    num_potions = num_potions.first()[0]
    num_ml = num_ml.first()[0]
    num_gold = num_gold.first()[0]

    print("Audit- " + "number_of_potions: " + str(num_potions) + " ml_in_barrels: " + str(num_ml) + " gold: " + str(num_gold))

    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": num_gold}

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
