from fastapi import FastAPI , HTTPException , Body
from pydantic import BaseModel , EmailStr
from typing import List , Optional 

from services import user_service , account_service , transaction_service , beneficiary_service

# Data Models
class TransferRequest(BaseModel):
    # Data model for transfer request
    sender_account_number: str
    receiver_account_number: str
    amount: float

class BeneficiaryCreate(BaseModel):
    # Data model for creating a new beneficiary
    user_id: str 
    beneficiary_name: str
    beneficiary_account_number: str
    bank_name: Optional[str] = "Internal" 

class ProfileUpdateRequest(BaseModel):
    field: str  
    value: str  

# Run the App
app = FastAPI(
    title = "AI Banlking Assistant API", 
    description = "API for AI Banking Assistant Application",
    version = "1.0.0"
    )

# Endpoints definitions
# Get account balance
@app.get("/accounts/{account_number}/balance")
def get_account_balance(account_number: str):
    # Get account balance 
    result = account_service.get_balance(account_number)
    if result['status'] == 'error':
        raise HTTPException(status_code=404 , detail=result['message'])
    
    return result["data"]

# Get account details
@app.get("/accounts/{account_number}/details")
def get_account_details(account_number: str):
    # Get account details
    result = account_service.get_account_details(account_number)
    if result['status'] == 'error':
        raise HTTPException(status_code=404 , detail=result['message'])
    
    return result["data"]
@app.get("/users/{user_id}/profile")
def get_user_profile(user_id: str):
    """
    جلب معلومات البروفايل لمستخدم معين.
    """
    # (تأكد من اسم الدالة في السيرفس عندك)
    result = user_service.get_user_profile(user_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
        
    return result["data"]

# Get recent transactions for an account
@app.get("/accounts/{account_number}/transactions")
def get_account_transactions(account_number: str, limit: int = 5):
    result = account_service.get_transactions(account_number, limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
        
    return result["data"]

# Create a transfer between accounts
@app.post("/transfer")
def create_transfer(request: TransferRequest):
    # Create a transfer between accounts
    result = transaction_service.execute_transfer(
        request.sender_account_number,
        request.receiver_account_number,
        request.amount
    )
    if result['status'] == 'error':
        raise HTTPException(status_code=400 , detail=result['message'])
    
    return result

# Get user profile
@app.get("/users/{user_id}/accounts")
def get_accounts_for_users(user_id: str):
    # Get all accounts for a user
    result = user_service.get_user_accounts(user_id)
    if result['status'] == 'error':
        raise HTTPException(status_code=404 , detail=result['message'])
    
    return result["data"]


# Add a new beneficiary
@app.post("/beneficiaries")
def add_beneficiary(request: BeneficiaryCreate):
    # Add a new beneficiary for a user
    result = beneficiary_service.add_beneficiary(
        request.user_id,
        request.beneficiary_name,
        request.beneficiary_account_number,
        request.bank_name
    )
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])

    return result

# Get all beneficiaries for a user
@app.get("/users/{user_id}/beneficiaries")
def get_user_beneficiaries(user_id: str):
    # Get all beneficiaries for a user
    result = beneficiary_service.get_beneficiaries(user_id)
    if result['status'] == 'error':
        raise HTTPException(status_code=404 , detail=result['message'])
    
    return result["data"]

# Update user profile information
@app.put("/users/{user_id}/profile")
def update_user_profile_info(user_id: str, request: ProfileUpdateRequest):
    result = user_service.update_user_profile(
        user_id,
        request.field,
        request.value
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@app.delete("/beneficiaries/{beneficiary_id}")
def delete_user_beneficiary(beneficiary_id: str, user_id_body: dict = Body(...)):
 
    user_id = user_id_body.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    result = beneficiary_service.delete_beneficiary(user_id, beneficiary_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
        
    return result


