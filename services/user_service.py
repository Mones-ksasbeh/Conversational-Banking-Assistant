from Database.Database import Users_col , Accounts_col
from bson import ObjectId 


# Get user profile 
def get_user_profile(user_id):
    # serching for the user and return his profile 
    try:
        user_obj_id = ObjectId(user_id)

        user = Users_col.find_one(
            {"_id" : user_obj_id} ,
            {"hashed_password" : 0}
        )

        if user :
            user["_id"] = str(user["_id"])
            return {"status" : "success" , "data" : user}
        else : 
            return {"status" : "error" , "massage" : "User not Found !"}

    except Exception as e :
        return {"status" : "error" , "massage" : f"An error occurred or invalid ID : {e}"}

    

def get_user_accounts(user_id):
    # Serching for all accounst for this user 
    try: 
        cursor = Accounts_col.find(
            {"user_id": user_id},
            {"balance": 1, "account_number": 1, "type": 1, "status": 1} 
        )
        accounts_list = []
        for account in cursor:
            account["_id"] = str(account["_id"])
            accounts_list.append(account)
            
        return {"status": "success", "data": accounts_list}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}

def update_user_profile(user_id: str, field_to_update: str, new_value: str):
    try:
        user_obj_id = ObjectId(user_id)
        
        allowed_fields = ["first_name", "last_name", "email", "phone", "address"]
        if field_to_update not in allowed_fields:
            return {"status": "error", "message": f"لا يمكن تعديل الحقل: {field_to_update}"}

        result = Users_col.update_one(
            {"_id": user_obj_id},
            {"$set": {field_to_update: new_value}}
        )
        
        if result.modified_count > 0:
            return {"status": "success", "message": f"تم تحديث {field_to_update} بنجاح"}
        else:
            return {"status": "error", "message": "لم يتم العثور على المستخدم أو لم يتم تغيير أي بيانات"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}   
            
    