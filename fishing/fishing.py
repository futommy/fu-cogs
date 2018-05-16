import discord
import random
import os
import asyncio
import math
from datetime import datetime
from cogs.utils.dataIO import dataIO
from discord.ext import commands

numFish = 152
fishList = {50: "nothing", 70: "clownfish", 90: "salmon", 110: "albacore", 120: "tuna", 130: "trout", 140: "bass", 145: "marlin", 150: "swordfish", 152: "sardines"}
fishCost = {"clownfish": 5, "salmon": 5, "albacore": 5, "tuna": 10, "trout": 10, "bass": 10, "marlin": 20, "swordfish": 20, "sardines": 50}

class fishing:

	def __init__(self, bot):
		self.accounts = dataIO.load_json("data/tom/fish.json")
		self.history = dataIO.load_json("data/tom/fishhistory.json")
		self.bot = bot
		self.bank = self.bot.get_cog('Economy').bank

	def checkExist(self, user):
		if not user.id in self.accounts or not fishList[numFish] in self.accounts[user.id]:
			account = {'fishing': 0}
			for i in fishList:
				fishName = fishList[i]
				account[fishName] = 0
			self.accounts[user.id] = account
		if not user.id in self.history:
			timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
			account = {'timesfished': 0, 'created': timestamp}
			for i in fishList:
				fishName = fishList[i]
				account[fishName] = 0
			self.history[user.id] = account

	@commands.command(pass_context=True)
	async def fish(self, ctx, user: discord.Member=None):
		user = ctx.message.author
		multiplier = 1
		self.checkExist(user)
		if self.accounts[user.id]['fishing'] == 1:
			await self.bot.say("{}, please wait to reel in your line!".format(user.mention));
			return 0;
		self.accounts[user.id]['fishing'] = 1;
		await self.bot.say("{} cast their line!".format(user.mention))
		await asyncio.sleep(5)
		accounts = self.accounts[user.id]
		randNum = random.randint(1,numFish)
		randNum *= multiplier
		sortedFishList = list(fishList)
		for i in sorted(sortedFishList):
			if randNum < i or i == numFish and randNum > numFish:
				caughtFish = fishList[i]
				break
		await self.bot.say("{} caught a(n) {}!".format(user.mention, caughtFish))
		amm = self.accounts[user.id][caughtFish]
		amm += 1
		accounts[caughtFish] = amm
		self.history[user.id][caughtFish] += 1
		self.history[user.id]['timesfished'] += 1
		accounts['fishing'] = 0
		self.accounts[user.id] = accounts
		dataIO.save_json("data/tom/fish.json", self.accounts)
		dataIO.save_json("data/tom/fishhistory.json", self.history)
		
	@commands.command(pass_context=True)
	async def icebox(self, ctx, user: discord.Member=None):
		user = ctx.message.author
		count = 0
		fishCount = 0
		self.checkExist(user)
		iceBoxFish = "";
		for i in fishList:
			fishCount += self.accounts[user.id][fishList[i]]
		await self.bot.say("{} You have {} fish in your icebox. Your fish:".format(user.mention, fishCount));
		for i in sorted(fishList):
			count += 1
			spacing = 23 - len("{}: {}".format(fishList[i], self.accounts[user.id][fishList[i]]))
			spacingStr = ""
			seperatorStr = ""
			for x in range(1, spacing):
				spacingStr += " "
			for y in range(1, 73):
				if y == 24 or y == 48:
					seperatorStr += "╪"
				else:
					seperatorStr += "="
			if count % 3 == 0:
				iceBoxFish += " {}: {}\n".format(fishList[i].capitalize(), self.accounts[user.id][fishList[i]])
				iceBoxFish += "{}\n".format(seperatorStr)
			else:
				iceBoxFish += " {}: {}{}|".format(fishList[i].capitalize(), self.accounts[user.id][fishList[i]], spacingStr)
		await self.bot.say("```{}```".format(iceBoxFish));

	@commands.command(pass_context=True)
	async def sellfish(self, ctx, fishSelling):
		user = ctx.message.author
		self.checkExist(user)
		if fishSelling.lower() in fishCost:
			if self.accounts[user.id][fishSelling.lower()] != 0:
				if not self.bank.account_exists(user):
					await self.bot.say("{} You don't have a bank account! Please run `//bank register`".format(user.mention))
				else:
					self.bank.deposit_credits(user, fishCost[fishSelling.lower()]*self.accounts[user.id][fishSelling.lower()])
					await self.bot.say("{} You sold {} {} for {} credits!".format(user.mention, self.accounts[user.id][fishSelling.lower()], fishSelling.lower(), fishCost[fishSelling.lower()]*self.accounts[user.id][fishSelling.lower()]))
					self.accounts[user.id][fishSelling.lower()] = 0
					dataIO.save_json("data/tom/fish.json", self.accounts)
			else:
				await self.bot.say("{} You do not have any of that fish!".format(user.mention))
		else:
			await self.bot.say("{} That fish does not exist!".format(user.mention))

	@commands.command(pass_context=True)
	async def costs(self, ctx):
		user = ctx.message.author
		count = 0
		fishCosts = "";
		for i in fishCost:
			count += 1
			spacing = 23 - len("{}: {}".format(i, fishCost[i]))
			spacingStr = ""
			seperatorStr = ""
			for x in range(1, spacing):
				spacingStr += " "
			for y in range(1, 73):
				if y == 24 or y == 48:
					seperatorStr += "╪"
				else:
					seperatorStr += "="
			if count % 3 == 0:
				fishCosts += " {}: {}\n".format(i.capitalize(), fishCost[i])
				fishCosts += "{}\n".format(seperatorStr)
			else:
				fishCosts += " {}: {}{}|".format(i.capitalize(), fishCost[i], spacingStr)
		await self.bot.say("```{}```".format(fishCosts));

	@commands.command(pass_context=True)
	async def fishlog(self, ctx):
		user = ctx.message.author
		count = 0
		self.checkExist(user)
		iceBoxFish = "";
		await self.bot.say("{} You have fished {} time(s) since {}. Your fish history:".format(user.mention, self.history[user.id]['timesfished'], self.history[user.id]['created']));
		for i in sorted(fishList):
			count += 1
			spacing = 23 - len("{}: {}".format(fishList[i], self.history[user.id][fishList[i]]))
			spacingStr = ""
			seperatorStr = ""
			for x in range(1, spacing):
				spacingStr += " "
			for y in range(1, 73):
				if y == 24 or y == 48:
					seperatorStr += "╪"
				else:
					seperatorStr += "="
			if count % 3 == 0:
				iceBoxFish += " {}: {}\n".format(fishList[i].capitalize(), self.history[user.id][fishList[i]])
				iceBoxFish += "{}\n".format(seperatorStr)
			else:
				iceBoxFish += " {}: {}{}|".format(fishList[i].capitalize(), self.history[user.id][fishList[i]], spacingStr)
		await self.bot.say("```{}```".format(iceBoxFish));

	@commands.command()
	async def spam(self):
		await self.bot.say("[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]][]]]]]]]]]][][]]]]]]]]][[[[[[[[[[]]]]]]]]]]][[[[[[[[[[[][][][][[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]][][][][]]]]]]]]]][][[[[[[[[[[[[[[[[[][[[[[[[[[[[[[[[[[[[[[][[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]][]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]][[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]][[[[[[[[[[[[[")

def check_folders():
	if not os.path.exists("data/tom"):
		print("Creating data/tom folder...")
		os.makedirs("data/tom")


def check_files():

	f = "data/tom/fishsettings.json"
	if not dataIO.is_valid_json(f):
		print("Creating fishing's settings.json...")
		dataIO.save_json(f, {})

	f = "data/tom/fishhistory.json"
	if not dataIO.is_valid_json(f):
		print("Creating fishing's history.json...")
		dataIO.save_json(f, {})

	f = "data/tom/fish.json"
	if not dataIO.is_valid_json(f):
		print("Creating empty fish.json...")
		dataIO.save_json(f, {})

def setup(bot):
	check_folders()
	check_files()
	bot.add_cog(fishing(bot))

