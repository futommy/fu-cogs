import discord
import asyncio
from .utils import checks
from cogs.utils.dataIO import dataIO
from discord.ext import commands

class MinerCog:
	"""Automine stuff"""

	def __init__(self, bot):
		self.bot = bot
		self.miners = []
		self.settings = dataIO.load_json("data/tom/minesettings.json")
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

	async def mine(server, channel):
		await asyncio.sleep(self.minerate)
		for user in self.miners[server][channel]:
			if not self.bank.account_exists(user):
				await self.bot.send_message(self.debugroom, "{} doesn't have a bank account! Creating one now.".format(user.mention))
				self.bank.create_account(user)
				self.bank.deposit_credits(user, self.bankstarter)
			self.bank.deposit_credits(user, self.mineamount)
			await self.bot.send_message(self.debugroom, "Gave {} {} gold".format(user.id, self.mineamount))
		mine(server, channel)

	async def on_voice_state_update(self, before, after):
		await self.bot.send_message(self.debugroom,"room trigger")
		after_members = ''
		try:
			after_members = after.voice_channel.voice_members
		except:
			await self.bot.edit_channel(before.voice.voice_channel, name=before.voice.voice_channel.name.replace(u"\U0001F4B0", ''))
			await self.bot.send_message(self.debugroom, "Channel empty")
			self.miners[before.server][after.voice_channel.id] = []
			return 0
		if(len(after_members) >= self.minelimit):
			if u"\U0001F4B0" not in after.voice_channel.name:
				await self.bot.edit_channel(after.voice.voice_channel, name=after.voice.voice_channel.name+u"\U0001F4B0")
			if after.id not in self.miners[after.server][after.voice_channel.id]:
				await self.bot.send_message(self.debugroom, "Added {} to miners".format(after.name))
				self.miners[after.server][after.voice_channel.id].append(after.id)
		else:
			await self.bot.edit_channel(after.voice.voice_channel, name=after.voice.voice_channel.name.replace(u"\U0001F4B0", ''))
			await self.bot.send_message(self.debugroom, "{} left and set members below limit ({})".format(after.name, self.minelimit))
			self.miners[after.server][after.voice_channel.id].remove(after.id)

	@commands.command(pass_context=True)
	@checks.mod_or_permissions(administrator=True)
	async def debugminers(self, ctx):
		await self.bot.send_message(ctx.message.channel, "Current Miners: " + str(self.miners[after.server][after.voice_channel.id]))

def check_folders():
	if not os.path.exists("data/tom"):
		print("Creating data/tom folder...")
		os.makedirs("data/tom")


def check_files():
	if not dataIO.is_valid_json("data/tom/minesettings.json"):
		print("Creating mine's settings.json...")
		dataIO.save_json(f, {})

def setup(bot):
	check_folders()
	check_files()
	bot.add_cog(MinerCog(bot))