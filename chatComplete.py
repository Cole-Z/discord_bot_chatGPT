import os
import openai
import tiktoken
import discord
from discord.ext import commands
# add your discord bot token for your server.
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# link your api key from OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_message = {
  "role":
  "system",
  "content":
  """You are intelligent AI designed to help with the game Minecraft. Help with builds and common info!"""
}
user_message = {
  "role":
  "user",
  "content":
  """What are some good starter farms for my world in survival Minecraft?"""
}
max_response_tokens = 250
token_limit = 4096
max_conversation_length = 5
conversation = []
conversation.append(system_message)
conversation.append(user_message)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
intents.members = True

# Create an instance of the bot
bot = commands.Bot(command_prefix="!", intents=intents)


def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
  encoding = tiktoken.encoding_for_model(model)
  num_tokens = 0
  for message in messages:
    num_tokens += 4
    for key, value in message.items():
      num_tokens += len(encoding.encode(value))
      if key == "name":
        num_tokens += -1
  num_tokens += 2
  return num_tokens


async def process_message(user_input):
  conversation.append({"role": "user", "content": user_input})

  if len(conversation) > max_conversation_length:
    conversation.pop(1)

  conv_history_tokens = num_tokens_from_messages(conversation)

  while conv_history_tokens + max_response_tokens >= token_limit:
    del conversation[1]
    conv_history_tokens = num_tokens_from_messages(conversation)

  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=conversation,
    temperature=0.7,
    max_tokens=max_response_tokens,
  )

  conversation.append({
    "role": "assistant",
    "content": response['choices'][0]['message']['content']
  })
  return response['choices'][0]['message']['content']


@bot.event
async def on_ready():
  print(f"{bot.user} has connected to Discord!")


@bot.command()
async def chat(ctx, *, user_input):
  response = await process_message(user_input)
  await ctx.send(response)

@bot.event
async def on_message(message):
  # Ignore messages sent by the bot itself
  if message.author == bot.user:
    return

  # Check if the message is a Direct Message
  if message.guild is None:
    # Process the message without the !chat command
    response = await process_message(message.content)
    await message.channel.send(response)
  else:
    # Process commands in other channels
    await bot.process_commands(message)


bot.run(TOKEN)

    # Check if the message is a Direct Message
    if message.guild is None:
        response = await process_message(message.content)
        await message.channel.send(response)
    else:
        await bot.process_commands(message)

bot.run(TOKEN)
