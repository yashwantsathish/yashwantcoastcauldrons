import random
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

import sqlalchemy
from src import database as db

ids = set()
carts_dict = {}

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response= can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    #search_page

    # Set Current Index
    curr_index = int(search_page) if search_page else 1
    print(curr_index)
    
    # Find what to sort by
    if sort_col == search_sort_options.customer_name:
        sorter = "name"
    
    elif sort_col == search_sort_options.item_sku:
        sorter = "sku"

    elif sort_col == search_sort_options.line_item_total:
        sorter = "price"
    
    #... and how to sort
    if sort_order == search_sort_order.asc:
        order = "ASC"

    elif sort_order == search_sort_order.desc:
        order = "DESC"

    # Get customer name (carts name), item sku (potions), quantity (cart_items), gold (price potions table)
    with db.engine.begin() as connection:
        print(customer_name)
        query = connection.execute(sqlalchemy.text("SELECT name, cart_items.quantity, potions.sku, potions.price, timestamp FROM carts " \
                                           "JOIN cart_items on carts.id = cart_items.cart_id " \
                                           "JOIN potions on potions.id = cart_items.potion_id " \
                                            "WHERE carts.name ILIKE :customer_name || '%' " \
                                            "AND potions.sku ILIKE :potion_sku || '%' " \
                                            f"ORDER BY {sorter} {order}"), 
                                            {
                                                "customer_name": customer_name,
                                                "potion_sku": potion_sku, 
                                            })
        
        query = query.fetchall()

        query_len = len(query)
        curr_index = int(curr_index)
        if query_len > curr_index + 5:
            next_index = curr_index + 5
            prev_index = curr_index - 5
            if prev_index < 0:
                prev_index = ""
        else:
            prev_index = ""
            next_index = ""
            if curr_index > 1:
                prev_index = curr_index - 5

        display_list = []

        for i in range(curr_index, min(curr_index + 5, query_len)):
            row = query[i]
            print(row.name)
            display_list.append(
                {
                    "line_item_id": i - 1,
                    "item_sku": row.sku,
                    "customer_name": row.name,
                    "line_item_total": row.price * row.quantity,
                    "timestamp": "2021-01-01T00:00:00Z",
                }
            )

    print("prev index: " + str(prev_index))
    print("next index: " + str(next_index))

    return {
        "previous": prev_index,
        "next": next_index,
        "results": display_list,
    }

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """    
    print("create cart")
    
    with db.engine.begin() as connection:
        name = new_cart.customer
        id = connection.execute(sqlalchemy.text("INSERT INTO carts (name) VALUES(:name) RETURNING id"), 
                                {
                                    "name": name
                                })
        id = id.first()[0]

    print("cart id: " + str(id))
    return {"cart_id": id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """     
    return carts_dict[cart_id]

class CartItem(BaseModel):
    quantity: int

   
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    print("set item quantity")
    print (str(cart_id) + ": " + item_sku + ", " + str(cart_item.quantity))
    print(cart_item)

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO cart_items (cart_id, quantity, potion_id) " \
                                           "SELECT :id, :quantity, id " \
                                           "FROM potions WHERE sku = :item_sku"),  
                    {
                        "id": cart_id,
                        "quantity": cart_item.quantity, 
                        "item_sku": item_sku
                    })

    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    print("checkout")
    gold = 0 

    num_bought = 0
    gold_paid = 0

    with db.engine.begin() as connection:
        # Getting potion_id, quantity, price columns for given cart items
        query = connection.execute(sqlalchemy.text("SELECT potion_id, cart_items.quantity, potions.price FROM cart_items " \
                                                   "JOIN potions ON potion_id = potions.id " \
                                                   "WHERE cart_id = :cart_id"),
                                                   {
                                                       "cart_id": cart_id
                                                   })
        # Iterating through all cart items for given cart
        for row in query:
            id = row.potion_id
            price = row.price
            print("potion id: " + str(id) + " price: " + str(price))
            quant = row.quantity
            num_bought += quant
            
            connection.execute(sqlalchemy.text("INSERT INTO pot_ledgers (potion_id, potions_changed) " \
                                               "VALUES (:id, -:quant) "),
                                               {
                                                   "id": id,
                                                   "quant": quant
                                               })
            gold_paid += price * quant
        
        # gold = gold + gold_paid
        connection.execute(sqlalchemy.text("INSERT INTO ledger (gold_change) VALUES (:gold_paid)"), 
                           {
                               "gold_paid": gold_paid
                           })

        return {"total_potions_bought": num_bought, "total_gold_paid": gold_paid}

