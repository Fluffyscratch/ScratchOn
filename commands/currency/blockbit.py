import scratchattach as sa
from scratchattach import *

session = sa.login("USERNAME", "PASSWORD")
cloud = session.connect_cloud(669020072)

def request_search(username):
  """ Send a request to get user's balance. """
  cloud.set_var("TO_HOST", Encoding.encode(f"search&{username}"))
