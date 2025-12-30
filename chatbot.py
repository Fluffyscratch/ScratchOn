import scratchattach as sa
from openai import OpenAI
import time

index = 0

# AI Setup
client = OpenAI(
    base_url="https://ai.aerioncloud.com/v1",  # This provider has shut down, will need to be changed to another one
    api_key="sk=1234",
)


# Function to simplify AI calling
def answer(query: str, username: str):
    """
    Function to simplify AI calling

    @parameters:

        - query: a sample prompt
        - username: By what name the AI will call the user
    """
    global index
    print("Answering...")

    resp = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
        "content": "You are a helpful scratch.mit.edu user and bot called ScratchOn. You cannot swear or do anything inappropriate. Never say anything bad about someone or something. Your language must be appropriate for 7-12 year olds. Always refer to yourself as ScratchOn, or _Scratch-On_ as your scratch username. Either refer to the user by their username, or don't refer to them at all. Keep your answers short and concise, up to 500 characters. Do not use regular emojis, only use Scratch-style emojis like :), _:D_, or XD. Speak like a scratch.mit.edu user would, using simple words and phrases a 12 years old would use in a chat, for example 'Hey!', 'That's cool!', 'Thanks!', 'No problem!', 'I guess you're right lol'.",
            },
            {"role": "user", "content": f"{username}: {query}"},
        ],
    )

    result = resp.choices[0].message.content

    print("Answered !")
    return result


# Setup scratch connection
with open("ScratchOn_private/password.txt") as f:
    session = sa.login(username="_Scratch-On_", password=f.readlines()[0])

profile = session.connect_linked_user()
events = session.connect_message_events()
print("Logged in")


# Main part : message replyer
@events.event
def on_message(message):
    print("Message detected")

    time.sleep(60)  # Wait 1 minute before replying to prevent comment glitches

    comment = profile.comments(page=1, limit=1)[0]

    comment.reply(
        content=answer(query=message.comment_fragment, username=message.actor_username)
    )
    """
    session.connect_user() gets the ScratchOn profile,
    comment_by_id finds the message based on infos provided by the event handler,
    reply() sends a reply by sending the message to the AI setted up earlier.
    """


events.start(thread=True, ignore_exceptions=True)
