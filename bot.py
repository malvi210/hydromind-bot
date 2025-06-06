# ==== FLASK SERVER TO KEEP ALIVE ====
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Hydro Mind is alive."

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# ==== DISCORD + OPENAI BOT ====
import discord
import openai
import os

# DEBUG: Show environment variable status
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
print(f"[DEBUG] DISCORD_TOKEN: {repr(DISCORD_TOKEN)}")
print(f"[DEBUG] OPENAI_API_KEY: {repr(OPENAI_API_KEY)}")

openai.api_key = OPENAI_API_KEY

# Enable message content
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!ask"):
        query = message.content[4:].strip()
        if not query:
            await message.channel.send("Ask me something after !ask")
            return

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Hydro Mind, an AI that responds based on uploaded transcripts."},
                    {"role": "user", "content": query}
                ]
            )
            answer = response['choices'][0]['message']['content']
            await message.channel.send(answer)
        except Exception as e:
            print(f"[ERROR] OpenAI call failed: {e}")
            await message.channel.send("Something went wrong.")

# Start the webserver + bot
keep_alive()
client.run(DISCORD_TOKEN)
