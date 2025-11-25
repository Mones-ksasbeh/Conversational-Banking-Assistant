from Database.Database import Client, Accounts_col, Transactions_col 
from datetime import datetime 
from bson.decimal128 import Decimal128
from decimal import Decimal 

def execute_transfer (sender_account_number , reciver_account_number , amount):
    # Validate input parameters
    if amount <= 0 :
        return {"status" : "error" , "message": "المبلغ يجب ان يكون أكبر من صفر !"}
    if sender_account_number == reciver_account_number:
        return {"status" : "error" , "message": "لا يمكن التحويل لنفس الحساب !"}

    try:
        amount_py_decimal = Decimal(str(amount))
    
    except Exception as e:
        # Handle invalid amount format
        return {"status": "error", "message": f"خطأ في تنسيق المبلغ: {e}"}

    try: 
        # Fetch sender and receiver account details
        sender_account = Accounts_col.find_one({"account_number": sender_account_number})
        reciver_account = Accounts_col.find_one({"account_number": reciver_account_number})

        # Validate accounts existence and status
        if not sender_account: 
            return {"status" : "error" , "message": "جساب المرسل غير موجود !"}
        if not reciver_account:
             return {"status": "error", "message": "حساب المستفيد غير موجود"}

        # Check if accounts are active
        if sender_account.get("status") != "active":
            return {"status" : "error" , "message": "جساب المرسل غير فعال !"}
        if reciver_account.get("status") != "active":
              return {"status": "error", "message": "حساب المستفيد غير نشط"}

        sender_balance_py_decimal = sender_account["balance"].to_decimal()

        # Check for sufficient funds
        if sender_balance_py_decimal < amount_py_decimal:
            return {"status" : "error" , "message": "الرصيد غير كافي لاتمام العمليه "}
    # Handle unexpected Errors
    except Exception as e:
        return {"status" : "error" , "message": f"خطأ أثناء جلب معلومات الحساب ! {e}"}

    # Prepare amounts for MongoDB operations
    amount_mongo_decimal = Decimal128(amount_py_decimal)
    negative_amount_mongo_decimal = Decimal128(-amount_py_decimal) 

    # Execute the transfer within a transaction
    session = None
    try:
        
        with Client.start_session() as session :
            
            session.start_transaction()
            try:
                Accounts_col.update_one({"account_number" : sender_account_number } ,
                                        {"$inc" : {"balance" : negative_amount_mongo_decimal}},
                                        session = session) 

                Accounts_col.update_one({"account_number" : reciver_account_number } ,
                                        {"$inc" : {"balance" : amount_mongo_decimal}},
                                        session = session) 

                debit_doc = {
                    "account_id" : sender_account["_id"],
                    "amount" : amount_mongo_decimal,
                    "type" : "withdrawal",
                    "currency" : sender_account.get("currency"), 
                    "timestamp" : datetime.now(),
                    "status" : "completed",
                    "description": f"Transfer to {reciver_account_number}"
                }
                Transactions_col.insert_one(debit_doc, session=session)

                credit_doc = {
                    "account_id" : reciver_account["_id"],
                    "amount" : amount_mongo_decimal,
                    "type" : "deposit",
                    "currency" : sender_account.get("currency"), 
                    "timestamp" : datetime.now(),
                    "status" : "completed",
                    "description": f"Transfer from {sender_account_number}"
                }
                Transactions_col.insert_one(credit_doc, session=session)
                
                session.commit_transaction()

            except Exception as e:
                session.abort_transaction()
                raise e 

            new_balance = sender_balance_py_decimal - amount_py_decimal
            return {
                "status" : "success" ,
                "message" : "تمت الحوالة بنجاح !", 
                "new_balance" : str(new_balance)
            }
    except Exception as e:
        return {"status" : "error" , "message": f"فشلت عملية التحويل ! {e}"}