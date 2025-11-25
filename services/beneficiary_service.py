from Database.Database import Benficiaries_col, Accounts_col
from bson import ObjectId
import datetime

def add_beneficiary(user_id, beneficiary_name, beneficiary_account_number, bank_name="Inte"):
    try:
        # Check if the beneficiaries existing
        existing = Benficiaries_col.find_one({
            "user_id": user_id,
            "account_number": beneficiary_account_number
        })
        
        if existing:
            return {"status": "error", "message": "هذا المستفيد مضاف سابقاً"}

        # prepare the document for inserting 
        beneficiary_doc = {
            "user_id": user_id,  
            "name": beneficiary_name, 
            "account_number": beneficiary_account_number,
            "bank_name": bank_name, 
            "added_at": datetime.datetime.now()
        }
        
        # Excute the insrting 
        result = Benficiaries_col.insert_one(beneficiary_doc)
        
        # Return success message
        return {
            "status": "success",
            "message": "تمت إضافة المستفيد بنجاح",
            "beneficiary_id": str(result.inserted_id)
        }
    # Handle unexpected Errors
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}


# Get the beneficiaries List 
def get_beneficiaries(user_id):
    try:
        cursor = Benficiaries_col.find({"user_id": user_id})
        beneficiaries_list = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            beneficiaries_list.append(doc)
        # Return the beneficiaries list
        return {"status": "success", "data": beneficiaries_list}
    # Handle unexpected Errors
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}


def delete_beneficiary(user_id: str, beneficiary_id: str):
 
    try:
        beneficiary_obj_id = ObjectId(beneficiary_id)
        
        result = Benficiaries_col.delete_one({
            "_id": beneficiary_obj_id,
            "user_id": user_id 
        })
        
        if result.deleted_count > 0:
            return {"status": "success", "message": "تم حذف المستفيد بنجاح"}
        else:
            return {"status": "error", "message": "المستفيد غير موجود أو لا تملك صلاحية حذفه"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}