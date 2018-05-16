import discord
import random
import os
import asyncio
import math
import urllib
import urllib.request
import imageio
import limf
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageSequence
from PIL import GifImagePlugin
from datetime import datetime
from cogs.utils.dataIO import dataIO
from discord.ext import commands

busy = {}
filters = {1: ImageEnhance.Color, 2: ImageEnhance.Contrast, 3: ImageEnhance.Brightness, 4: ImageFilter.CONTOUR, 5: ImageFilter.DETAIL, 6: ImageFilter.EMBOSS}
filterNum = 10

class ImageUtils:
	def __init__(self, bot):
		self.bot = bot
		self.frames = 0

	@commands.command(pass_context=True)
	async def randmanip(self, ctx, image):
		frames = []
		user = ctx.message.author
		channel = ctx.message.channel
		x = 0
		eofcheck = True
		if not user.id in busy:
			busy[user.id] = 0
		if busy[user.id] != 1:	
			try:
				urllib.request.urlretrieve("{}".format(image), "{}".format(user.id))
			except:
				await self.bot.say("Could not load file. Possible permissions error. Try different host.")
			im = Image.open("{}".format(user.id))
			im.save("{}.gif".format(user.id), "GIF", save_all=True)
			im.save("original{}.gif".format(user.id), "GIF", save_all=True)
			busy[user.id] = 1
			enhanced = filters[1]
			randNum = random.randint(3, filterNum)
			await self.bot.delete_message(ctx.message)
			for i in range(1, randNum):
				randNum2 = random.randint(1, len(filters))
				frame = Image.open("{}.gif".format(user.id))
				nframes = 0
				while eofcheck:
					frame.save(fp='{}.png'.format(nframes))
					nframes += 1
					try:
						frame.seek(nframes)
					except EOFError:
						self.frames = nframes
						eofcheck = False

				for x in range(0, nframes):
					frame = Image.open("{}.png".format(x))
					frame = frame.convert('RGB')
					filters[1] = ImageEnhance.Color(frame)
					filters[2] = ImageEnhance.Contrast(frame)
					filters[3] = ImageEnhance.Brightness(frame)
					if(randNum2 < 4):
						enhanced = filters[randNum2]
						enhanced.enhance(round(random.uniform(1, 10), 1)).save("{}.png".format(x))
					else:
						frame = frame.filter(filters[randNum2])
						frame.save(fp='{}.png'.format(x))
			with imageio.get_writer('changed{}.gif'.format(user.id), mode='I') as writer:
				for y in range(0, self.frames):
					try:
						image = imageio.imread("{}.png".format(y), format="png")
						writer.append_data(image)
						os.remove("{}.png".format(y))
					except:
						await self.bot.say("{}".format(y))
						break
			await self.bot.send_file(channel, "changed{}.gif".format(user.id))
			os.remove("changed{}.gif".format(user.id))
			os.remove("original{}.gif".format(user.id))
			busy[user.id] = 0

def setup(bot):
	bot.add_cog(ImageUtils(bot))