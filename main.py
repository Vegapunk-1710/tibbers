import os
import discord

import torch
import torch.nn as nn
from torchtext.data.utils import get_tokenizer
from torchtext.vocab import build_vocab_from_iterator

from dotenv import load_dotenv

import __main__

class Model(nn.Module):
    def __init__(self, vocab_size, embed_dim):
        super().__init__()
        self.embed_layer =  nn.EmbeddingBag(vocab_size+1, embed_dim)
        self.lstm = nn.LSTM(embed_dim, 20, bidirectional=True) # nn.Tanh()
        self.linear_1 = nn.Linear(40, 32) # nn.ReLU()
        self.linear_2 = nn.Linear(32, 16) # nn.ReLU()
        self.linear_3 = nn.Linear(16, 6) # nn.Sigmoid()
        self.t = nn.Tanh()
        self.r = nn.ReLU()
        self.s = nn.Sigmoid()

    def forward(self, x):
        embedded = self.embed_layer(x)
        out, _ = self.lstm(embedded)
        out = self.t(out)
        out = self.r(self.linear_1(out))
        out = self.r(self.linear_2(out))
        out = self.s(self.linear_3(out))
        return out

setattr(__main__, "Model", Model)
load_dotenv()

def GetPrediction(message):
    model = torch.load('saved_model.pt')
    vocab = torch.load('saved_vocab.pth')
    tokenizer = get_tokenizer("basic_english")
    def yield_tokens(data):
        for text in data:
            yield tokenizer(text)
    text_pipeline = lambda x: vocab(tokenizer(x))
    response = []
    classes = ['Toxic','Severe Toxic', 'Obscene', 'Threat', 'Insult', 'Identity Hate']
    message = text_pipeline(message)
    message = torch.LongTensor(message)
    message = message[None,:]
    pred = model(message)[0]
    results = (pred>0.9).nonzero()
    for r in results:
        response.append(classes[r[0].item()])
    return response

client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('We are logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author.bot:
        return
    msg = str(message.content)
    await message.channel.send(str(GetPrediction(msg)))


client.run(os.getenv('discord_bot_env'))

