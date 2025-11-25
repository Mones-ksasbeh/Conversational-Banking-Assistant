import streamlit as st
import requests
import google.generativeai as genai
import json

st.set_page_config(
    page_title="Talk to your Bank" \
    "",
    page_icon="🏦",  
    layout="centered", # 
    initial_sidebar_state="auto"
)

# API 
FASTAPI_URL = "http://127.0.0.1:8000"
MOCKED_DEFAULT_ACCOUNT = "2100908033"
MOCKED_USER_ID = "68f626d9c4f9697a7389b7d9"

try:
    gemini_key = st.secrets["API_Key"]
    genai.configure(api_key=gemini_key)

except KeyError:
    st.error("خطأ: لم يتم العثور على `API_Key` في ملف `secrets.toml`.")
    st.stop()
except Exception as e:
    st.error(f"خطأ أثناء تهيئة Gemini: {e}")
    st.stop()

# API Wrappers
def get_balance_api(account_number: str = None):
    
    if not account_number:
        account_number = MOCKED_DEFAULT_ACCOUNT
    try:
        response = requests.get(f"{FASTAPI_URL}/accounts/{account_number}/balance")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب البيانات")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}

def execute_transfer_api(receiver_account_number: str, amount: float):
    
    sender_account_number = MOCKED_DEFAULT_ACCOUNT

    payload = {
        "sender_account_number": sender_account_number,
        "receiver_account_number": receiver_account_number,
        "amount": amount
    }
    try:
        response = requests.post(f"{FASTAPI_URL}/transfer", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "فشل تنفيذ الحوالة")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}

def get_transactions_api(account_number: str = None, limit: int = 5):
    if not account_number:
        account_number = MOCKED_DEFAULT_ACCOUNT
    try:
        response = requests.get(f"{FASTAPI_URL}/accounts/{account_number}/transactions?limit={limit}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب الحركات")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}
    

def get_account_details_api(account_number: str = None):

    if not account_number:
        account_number = MOCKED_DEFAULT_ACCOUNT
    try:
        response = requests.get(f"{FASTAPI_URL}/accounts/{account_number}/details")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب التفاصيل")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}


def get_user_profile_api():

    user_id = MOCKED_USER_ID 
    try:
        response = requests.get(f"{FASTAPI_URL}/users/{user_id}/profile")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب البروفايل")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}

def get_user_accounts_api():
    
    user_id = MOCKED_USER_ID
    try:
        response = requests.get(f"{FASTAPI_URL}/users/{user_id}/accounts")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب الحسابات")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}


def get_beneficiaries_api():

    user_id = MOCKED_USER_ID 
    try:
        response = requests.get(f"{FASTAPI_URL}/users/{user_id}/beneficiaries")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في جلب المستفيدين")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}

def add_beneficiary_api(beneficiary_name: str, beneficiary_account_number: str):
    
    payload = {
        "user_id": MOCKED_USER_ID, 
        "beneficiary_name": beneficiary_name,
        "beneficiary_account_number": beneficiary_account_number

    }
    try:
        response = requests.post(f"{FASTAPI_URL}/beneficiaries", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في إضافة المستفيد")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}
    

def update_user_profile_api(field: str, value: str):

    payload = {
        "field": field,
        "value": value
    }
    try:
        response = requests.put(f"{FASTAPI_URL}/users/{MOCKED_USER_ID}/profile", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.json().get("detail", "خطأ في تحديث البروفايل")}
    except Exception as e:
        return {"error": f"فشل الاتصال بالـ API: {e}"}
    


def delete_beneficiary_by_name_api(beneficiary_name: str):
 
    try:
        list_response = requests.get(f"{FASTAPI_URL}/users/{MOCKED_USER_ID}/beneficiaries")
        if list_response.status_code != 200:
            return {"error": "فشل جلب قائمة المستفيدين (الخطوة 1)"}
        
        beneficiaries = list_response.json()
    except Exception as e:
        return {"error": f"فشل الاتصال لجلب القائمة: {e}"}

    beneficiary_id_to_delete = None
    for ben in beneficiaries:
        if ben.get("name", "").lower() == beneficiary_name.lower():
            beneficiary_id_to_delete = ben.get("_id") # <-- وجدنا الـ ID
            break
            
    if not beneficiary_id_to_delete:
        return {"error": f"لم يتم العثور على مستفيد بالاسم: {beneficiary_name}"}
        
    try:
        payload = {"user_id": MOCKED_USER_ID} 
        response = requests.delete(f"{FASTAPI_URL}/beneficiaries/{beneficiary_id_to_delete}", json=payload)
        
        if response.status_code == 200:
            return response.json() # (هذا هو رد النجاح: "تم الحذف بنجاح")
        else:
            return {"error": response.json().get("detail", "خطأ في حذف المستفيد (الخطوة 2)")}
            
    except Exception as e:
        return {"error": f"فشل الاتصال لحذف المستفيد: {e}"}

# Define tools for the Gemini model
tools_definitions = [
    {
        "name": "get_balance",
        "description": "الحصول على الرصيد. إذا لم يحدد المستخدم رقم حساب، استخدم الحساب الافتراضي.",
        "parameters": {
            "type": "OBJECT",  
            "properties": {
                "account_number": {
                    "type": "STRING",
                    "description": "رقم الحساب (اختياري، سيتم استخدام الافتراضي إذا لم يُذكر)."
                }
            }
        }
    },
    {
        "name": "execute_transfer",
        "description": "تنفيذ حوالة مالية من الحساب الافتراضي للمستخدم إلى حساب مستفيد آخر.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                
                "receiver_account_number": {
                    "type": "STRING",
                    "description": "رقم حساب المستفيد (إجباري)."
                },
                "amount": {
                    "type": "NUMBER",
                    "description": "المبلغ المراد تحويله (إجباري)."
                }
            },
            "required": ["receiver_account_number", "amount"]
        }
    },
    {
        "name": "get_transactions",
        "description": "الحصول على كشف حساب. إذا لم يحدد المستخدم رقم حساب، استخدم الحساب الافتراضي.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "account_number": {
                    "type": "STRING",
                    "description": "رقم الحساب (اختياري)."
                },
                "limit": {
                    "type": "NUMBER",
                    "description": "عدد الحركات المطلوب (مثلاً: آخر 5 حركات). الافتراضي هو 5."
                }
            }
        }
    },
    {
        "name": "get_account_details",
        "description": "الحصول على كل التفاصيل الكاملة لحساب بنكي معين. استخدم الافتراضي إذا لم يُذكر.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "account_number": {
                    "type": "STRING",
                    "description": "رقم الحساب الذي نريد جلب تفاصيله (اختياري)."
                }
            },
        }
    }, 
    {
        "name": "get_user_profile",
        "description": "الحصول على معلومات الملف الشخصي للمستخدم الحالي، مثل الاسم، الإيميل، أو رقم الهاتف.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    
    {
        "name": "get_user_accounts",
        "description": "الحصول على قائمة بكل الحسابات البنكية (جاري، توفير، إلخ) المسجلة باسم المستخدم الحالي.",
        "parameters": {
            "type": "OBJECT",
            "properties": {} 
        }
    }, 
    {
        "name": "get_beneficiaries",
        "description": "الحصول على قائمة المستفيدين المحفوظين مسبقاً للمستخدم الحالي.",
        "parameters": {
            "type": "OBJECT",
            "properties": {} # لا تحتاج مدخلات
        }
    },
    
    {
        "name": "add_beneficiary",
        "description": "إضافة مستفيد جديد إلى قائمة المستفيدين الخاصة بالمستخدم. يتطلب هذا اسم المستفيد (لقب) ورقم حسابه.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "beneficiary_name": {
                    "type": "STRING",
                    "description": "الاسم أو اللقب الذي يريد المستخدم حفظ المستفيد به، مثل 'أحمد' أو 'شركة الكهرباء'."
                },
                "beneficiary_account_number": {
                    "type": "STRING",
                    "description": "رقم الحساب البنكي الكامل للمستفيد الجديد."
                }
            },
            "required": ["beneficiary_name", "beneficiary_account_number"]
        }
    },
    {
        "name": "update_user_profile",
        "description": "تحديث معلومة معينة في الملف الشخصي للمستخدم، مثل 'email' (الإيميل) أو 'phone' (الهاتف) أو 'address' (العنوان).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "field": {
                    "type": "STRING",
                    "description": "اسم الحقل المراد تعديله (مثل 'email' أو 'phone')."
                },
                "value": {
                    "type": "STRING",
                    "description": "القيمة الجديدة التي سيتم وضعها في الحقل."
                }
            },
            "required": ["field", "value"]
        }
    },
    {
        "name": "delete_beneficiary",
        "description": "حذف مستفيد معين من قائمة المستفيدين الخاصة بالمستخدم. يتطلب هذا 'اسم' المستفيد.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "beneficiary_name": { 
                    "type": "STRING",
                    "description": "الاسم الفريد للمستفيد المراد حذفه (مثل 'Mones Ksasbeh')."
                }
            },
            "required": ["beneficiary_name"]
        }
    }
]


# Map tool names to functions
available_tools = {
    "get_balance": get_balance_api,
    "execute_transfer": execute_transfer_api,
    "get_transactions": get_transactions_api,
    "get_account_details": get_account_details_api, 
    "get_user_profile": get_user_profile_api,
    "get_user_accounts": get_user_accounts_api,
    "get_beneficiaries": get_beneficiaries_api,
    "add_beneficiary": add_beneficiary_api,
    "update_user_profile": update_user_profile_api,
    "delete_beneficiary": delete_beneficiary_by_name_api
}

# Initialize the Gemini model
model = genai.GenerativeModel(model_name="models/gemini-2.5-flash-preview-05-20", tools=tools_definitions)


st.markdown("<h2 style='text-align: center;'>Talk to your bank  🏦  المساعد البنكي الذكي</h2>", unsafe_allow_html=True)

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:

    st.session_state.messages = [
        {"role": "assistant", "content": "أهلاً بك! أنا مساعدك البنكي. كيف يمكنني خدمتك اليوم؟"}
    ]

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("...اسألني"):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        chat = st.session_state.chat
        response = chat.send_message(prompt)

        if not response.candidates:
            st.error("أعتذر، لم أتمكن من معالجة الرد. قد يكون بسبب قيود السلامة.")
        else:
            parts = response.candidates[0].content.parts
            function_call_part = None
            for part in parts:
                if part.function_call:
                    function_call_part = part
                    break

            while function_call_part:
                function_call = function_call_part.function_call
                function_name = function_call.name
                args = dict(function_call.args)
                
                if function_name in available_tools:
                    function_to_call = available_tools[function_name]
                    tool_result = function_to_call(**args)

                    response = chat.send_message(
                        {
                            "function_response": {
                                "name": function_name,
                                "response": {"content": tool_result},
                            },
                        }
                    )
                    
                    if not response.candidates:
                        st.error("أعتذر، لم أتمكن من معالجة رد الأداة.")
                        parts = [] # Clear parts to avoid further error
                        function_call_part = None
                    else:
                        parts = response.candidates[0].content.parts
                        function_call_part = None
                        for part in parts:
                            if part.function_call:
                                function_call_part = part
                                break
                
                else:
                    st.error(f"خطأ: المودل حاول استدعاء دالة غير معروفة: {function_name}")
                    break 

            if parts and parts[0].text:
                final_response_text = parts[0].text
                st.session_state.messages.append({"role": "assistant", "content": final_response_text})
                with st.chat_message("assistant"):
                    st.markdown(final_response_text)
            elif not function_call_part: 
                # This handles cases where the response might be empty after a function call
                # or if the initial response was not a function call and not text.
                st.error("أعتذر، تلقيت رداً غير متوقع.")

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة طلبك: {e}")