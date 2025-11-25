from Database.Database import Accounts_col , Transactions_col
from bson import ObjectId
from bson.decimal128 import Decimal128  

# Get account detalis 
def get_account_details(account_number): 
    # Search for account detalis using account number 
    try :
        # USing PyMongo to find the document in the accounts collectio
        account = Accounts_col.find_one({"account_number" : account_number })
        if account : 
           account["_id"] = str(account["_id"])
           account["user_id"] = str(account["user_id"])
           account["balance"] = str(account["balance"])
           # Return the account details
           return {"status" : "Success" , "data": account}
        else : 
           # Account not found
           return {"status" : "error" , "message": "Account Not Found ! "}

    except Exception as e: 
           # Handle unexpected Errors 
           return {'status' : "error" , "message" : f"An Error occurres {e} ! "}


def get_balance(account_number):
    # serching for account and return balance 
    try:
        # Serching for the balance and using ( projection ) to include just the balance and currency
        account_balance = Accounts_col.find_one(
            {"account_number" : account_number},
            {"balance" : 1 , "currency" : 1 , "_id" : 0}
        )
        if account_balance:
            account_balance['balance'] = str(account_balance['balance'])
            # Return the balance
            return {"status" : "Success" , "data": account_balance}
        else : 
           # Account not found
           return {"status" : "error" , "message": "Account Not Found ! "}
            
    except Exception as e: 
           # Handle unexpected Errors 
           return {'status' : "error" , "message" : f"An Error Occurres {e} ! "}


def get_transactions(account_number, limit=5):
    # Serching for the transactions related to this account number
    try:
        account = Accounts_col.find_one(
            {"account_number": account_number},
            {"_id": 1} 
        )
        if not account:
            # Account not found
            return {"status": "error", "message": "Account Not Found!"}
        
        account_object_id = account["_id"]

        # Fetch transactions for the account
        cursor = Transactions_col.find(
            {"account_id": account_object_id}
        ).sort("timestamp", -1).limit(limit)
        
        transactions_list = []

        # Process each transaction
        for tx in cursor:
            tx["_id"] = str(tx["_id"])
            tx["account_id"] = str(tx["account_id"])
            if "amount" in tx:
                tx["amount"] = str(tx["amount"])
            if "timestamp" in tx:
                tx["timestamp"] = tx["timestamp"].isoformat()
                
            transactions_list.append(tx)
        
        # Return the transactions list
        return {"status": "success", "data": transactions_list}
    # Handle unexpected Errors
    except Exception as e:
        return {'status': "error", "message": f"An Error occurred: {e}"}