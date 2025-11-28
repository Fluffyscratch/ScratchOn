import scratchattach as sa
from openai import OpenAI
import time

index = 0

# AI Setup
client = OpenAI(base_url="https://ai.aerioncloud.com/v1", api_key="sk=1234")

# Initial message
completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful scratch.mit.edu assistant called FluffyBot"}
    ]
)

# Function to simplify AI calling
def answer(query : str, username : str):
    """
    Function to simplify AI calling

    @parameters:

        - query: a sample prompt
        - username: By what name the AI will call the user
    """
    global index
    global completion
    print("Answering...")

    completion = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful scratch.mit.edu assistant called FluffyBot. You cannot swear or do anything inappropriate. Do not say anything bad about someone or something. "},
        {"role": f"scrather called {username}", "content": query}
    ]
)

    result = completion.choices[0].message.content

    print("Answered !")
    return result

# Setup scratch connection
with open("ScratchOn_private/password.txt") as f:
    session = sa.login(username="-FluffyBot-", password=f.readlines()[0])

profile = session.connect_linked_user()
events = session.connect_message_events()
print("Logged in")

# Main part : message replyer
@events.event
def on_message(message):
    print("Message detected")

    time.sleep(10)

    comment = profile.comments(page=1, limit=1)[0]
    
    comment.reply(content=answer(query=message.comment_fragment, username=message.actor_username))
    """
    session.connect_user() gets the FluffyBot profile,
    comment_by_id finds the message based on infos provided by the event handler,
    reply() sends a reply by sending the message to the AI setted up earlier.
    """

events.start(thread=True, ignore_exceptions=True)
