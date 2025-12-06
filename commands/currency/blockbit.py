import scratchattach as sa
from scratchattach import *

username = "test" 
session = sa.login("USERNAME", "PASSWORD")
cloud = session.connect_cloud(669020072)

cloud.set_var("TO_HOST", f"{Encoding.encode(f"search&{username}")
