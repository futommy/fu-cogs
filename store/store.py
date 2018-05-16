import discord
import random
import os
import asyncio
import math
from datetime import datetime
from cogs.utils.dataIO import dataIO
from discord.ext import commands

forSale = {'Fishing Rod Level 2': 1000}

class tomstore:
	"""My custom cog that does stuff!"""

	def __init__(self, bot):
		self.items = dataIO.load_json("data/tom/store.json")
		self.bot = bot
		self.bank = self.bot.get_cog('Economy').bank

	@commands.command(pass_context=True)
	async def buyitem(self, ctx):
		user = ctx.message.author

	@commands.command(pass_context=True)
	async def store(self, ctx):
		user = ctx.message.author
		count = 0
		iceBoxFish = "";
		if not self.bank.account_exists(user):
			await self.bot.say("{} You don't have a bank account! Please run `//bank register`".format(user.mention))
		else:
			await self.bot.say("Hi {}! We currently have the following in stock:".format(user.mention));
			for i in forSale:
				count += 1
				spacing = 35 - len("{}: {}".format(i, forSale[i]))
				spacingStr = ""
				seperatorStr = ""
				for x in range(1, spacing):
					spacingStr += " "
				for y in range(1, 49):
					if y == 24:
						seperatorStr += "╪"
					else:
						seperatorStr += "="
				if count % 2 == 0:
					iceBoxFish += " {}: {} Credits\n".format(i, forSale[i])
					iceBoxFish += "{}\n".format(seperatorStr)
				else:
					iceBoxFish += " {}: {} Credits{}|".format(i, forSale[i], spacingStr)
			await self.bot.say("```{}```".format(iceBoxFish));

def check_folders():
	if not os.path.exists("data/tom"):
		print("Creating data/tom folder...")
		os.makedirs("data/tom")


def check_files():
	f = "data/tom/store.json"
	if not dataIO.is_valid_json(f):
		print("Creating empty store.json...")
		dataIO.save_json(f, {})

def setup(bot):
	check_folders()
	check_files()
	bot.add_cog(tomstore(bot))

