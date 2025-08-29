import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", '8186557'))
API_HASH = os.getenv("API_HASH","efd77b34c69c164ce158037ff5a0d117")
BOT_TOKEN = os.getenv("BOT_TOKEN","7996370332:AAFTubxCVDb5q2SKJUx7-Cr3J3_Xe2DRLsE")

OWNER_ID = int(os.getenv("OWNER_ID", "130737653"))
MONGO_URI = os.getenv("MONGO_URI","mongodb+srv://kuldiprathod2003:kuldiprathod2003@cluster0.wxqpikp.mongodb.net/?retryWrites=true&w=majority")