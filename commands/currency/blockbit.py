import scratchattach as sa
from scratchattach import *

session = sa.login("USERNAME", "PASSWORD")
cloud = session.connect_cloud(669020072)

def request_search(username):
  """ Send a request to get user's balance. """
  cloud.set_var("TO_HOST", Encoding.encode(f"search&{username}"))

def get_response():
  """ Get response for the last request. """
  i = 1
  vars = []
  while i < 10:
    vars.append(cloud.get_var(f"FROM_HOST{i}"))
    i = i + 1
