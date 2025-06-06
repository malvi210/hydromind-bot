# ==== FLASK SERVER TO KEEP REPLIT AWAKE ====
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
import os
import openai

# Load secrets from Replit Secrets tab
DISCORD_TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Load all transcripts into memory
def load_transcripts(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"
    return all_text.strip()

transcript_memory = load_transcripts("transcripts")

# Initialize Discord client
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
        query = message.content[5:].strip()

        if not query:
            await message.channel.send("Ask me something using `!ask <your question>`.")
            return

        prompt = f"""
You are Hydro Mind, an intelligent AI brain trained on the following transcripts. Speak like you're remembering this info, not quoting it. Be helpful, fluid, and concise.

Transcript Memory:
{transcript_memory}

User asked: {query}
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7,
            )
            reply = response['choices'][0]['message']['content']
            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send("Something went wrong.")
            print(e)

# ==== KEEP ALIVE AND RUN ====
keep_alive()
client.run(DISCORD_TOKEN)

