import pymongo
from pymongo.mongo_client import MongoClient 

# Important Note about the security !!!!! Just here for experamint 
Connection_string = "mongodb+srv://moksasbeh_db_user:Mmm2003@cluster01.dtypy19.mongodb.net/?appName=Cluster01"

try : 
    # Create Database Connection 
    Client = MongoClient(Connection_string)
    # Database 
    db = Client['ConversationalBank']
    # Database Collections 
    Users_col = db['Users']
    Accounts_col = db['Accounts']
    Transactions_col = db['Transactions']
    Benficiaries_col = db['Benficiaries']

    Client.admin.command('ping') 
    print('Database Connected Done !') 

except Exception as e : 
    print(e)
    Client = None
    db = None
    Users_col = None
    Accounts_col = None
    Transactions_col = None
    Benficiaries_col = None
    