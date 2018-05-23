import discord
import asyncio
import os
from .utils import checks
from cogs.utils.dataIO import dataIO
from discord.ext import commands

class MinerCog:
	"""Automine stuff"""

	def __init__(self, bot):
		self.bot = bot
		self.miners = {}
		self.mining = {}
		self.settings = dataIO.load_json("data/tom/minesettings.json")
		if not 'settings' in self.settings:
			self.settings = {'settings': {}}
		self.debugroom = self.bot.get_channel('443633597417521163')
		self.bank = self.bot.get_cog('Economy').bank
		if not 'mineamount' in self.settings['settings']:
			self.settings['settings']['mineamount'] = 20
		if not 'minelimit' in self.settings['settings']:
			self.settings['settings']['minelimit'] = 5
		if not 'minerate' in self.settings['settings']:
			self.settings['settings']['minerate'] = 60
		self.mineamount = self.settings['settings']['mineamount']
		self.minelimit = self.settings['settings']['minelimit']
		self.minerate = self.settings['settings']['minerate']

	async def mine(self, server, channel):
		await asyncio.sleep(self.minerate)
		if(len(self.miners[server.id][channel.id]) < self.minelimit):
			self.mining[channel.id] = 0
			return 0
		for user in self.miners[server.id][channel.id]:
			userobj = server.get_member(user)
			if not self.bank.account_exists(userobj):
				await self.bot.send_message(self.debugroom, "{} doesn't have a bank account! Creating one now.".format(userobj.mention))
				self.bank.create_account(userobj)
			self.bank.deposit_credits(userobj, self.mineamount)
			await self.bot.send_message(self.debugroom, "Gave {} {} gold".format(user, self.mineamount))
		await self.mine(server, channel)

	async def on_voice_state_update(self, before, after):
		await self.bot.send_message(self.debugroom,"room trigger")
		after_members = ''
		if self.miners[after.server.id] == {}:
			self.bot.send_message(self.debugroom, "Gathering users")
			server = after.server
			for channel in server.channels:
				if channel.type == "Voice":
					for member in channel.voice_members:
						self.miners[after.server.id][channel.id].append(member.id)
					if len(self.miners[after.server.id][channel.id]) > self.minelimit:
						if u"\U0001F4B0" not in channel.name:
							await self.bot.edit_channel(channel, name=channel.name+u"\U0001F4B0")
						try:
							if not self.mining[channel.id] == 1:
								self.mining[channel.id] = 1
								await self.mine(after.server, channel)
						except KeyError:
							self.mining[channel.id] = 1
							await self.mine(after.server, channel)
		try:
			after_members = after.voice_channel.voice_members
		except:
			await self.bot.edit_channel(before.voice.voice_channel, name=before.voice.voice_channel.name.replace(u"\U0001F4B0", ''))
			await self.bot.send_message(self.debugroom, "Channel empty")
			try:
				self.miners[before.server.id][before.voice_channel.id] = []
			except KeyError:
				self.miners[before.server.id] = {}
				self.miners[before.server.id][before.voice_channel.id] = []
			return 0
		try:
			if after.id not in self.miners[after.server.id][after.voice_channel.id]:
				await self.bot.send_message(self.debugroom, "Added {} to miners".format(after.name))
				self.miners[after.server.id][after.voice_channel.id].append(after.id)
		except KeyError:
			await self.bot.send_message(self.debugroom, "Added {} to miners".format(after.name))
			try:
				self.miners[after.server.id][after.voice_channel.id] = []
			except KeyError:
				self.miners[after.server.id] = {}
				self.miners[after.server.id][after.voice_channel.id] = []
			self.miners[after.server.id][after.voice_channel.id].append(after.id)
		if after.voice.self_deaf:
			await self.bot.send_message(self.debugroom, "{} is deafened, removing from miners")
			self.miners[after.server.id][after.voice_channel.id].remove(after.id)
		if len(self.miners[after.server.id][after.voice_channel.id]) >= self.minelimit:
			if u"\U0001F4B0" not in after.voice_channel.name:
				await self.bot.edit_channel(after.voice.voice_channel, name=after.voice.voice_channel.name+u"\U0001F4B0")
			try:
				if not self.mining[after.voice_channel.id] == 1:
					self.mining[after.voice_channel.id] = 1
					await self.mine(after.server, after.voice_channel)
			except KeyError:
				self.mining[after.voice_channel.id] = 1
				await self.mine(after.server, after.voice_channel)
		if len(after_members) < len(self.miners[after.server.id][after.voice_channel.id]):
			await self.bot.send_message(self.debugroom, "{} left".format(after.name, self.minelimit))
			self.miners[after.server.id][after.voice_channel.id].remove(after.id)
		if len(self.miners[after.server.id][after.voice_channel.id]) < self.minelimit:
			await self.bot.edit_channel(after.voice.voice_channel, name=after.voice.voice_channel.name.replace(u"\U0001F4B0", ''))

	@commands.command(pass_context=True)
	@checks.mod_or_permissions(administrator=True)
	async def debugminers(self, ctx):
		await self.bot.send_message(ctx.message.channel, "Current Miners: " + str(self.miners))

	@commands.command(pass_context=True)
	async def checksettings(self, ctx):
		await self.bot.send_message(ctx.message.channel, "limit: {} rate: {} amount: {}".format(self.minelimit, self.minerate, self.mineamount))

def check_folders():
	if not os.path.exists("data/tom"):
		print("Creating data/tom folder...")
		os.makedirs("data/tom")


def check_files():
	if not dataIO.is_valid_json("data/tom/minesettings.json"):
		print("Creating mine's settings.json...")
		dataIO.save_json("data/tom/minesettings.json", {})

def setup(bot):
	check_folders()
	check_files()
	bot.add_cog(MinerCog(bot))
