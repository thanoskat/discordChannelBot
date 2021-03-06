import discord,datetime,random,configparser,os
def timeNow(): return (datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

# Read config file
config = configparser.ConfigParser()
config.read(os.path.splitext(__file__)[0] + '.ini', encoding='utf-8')
settings = config['Settings']
minHiddenChannels = int(settings['minHiddenChannels'])
maxHiddenChannels = int(settings['maxHiddenChannels'])
emptyHiddenChannels = int(settings['emptyHiddenChannels'])
hiddenChannelNamePool = settings['hiddenChannelNamePool'].split(', ')
minPublicChannels = int(settings['minPublicChannels'])
maxPublicChannels = int(settings['maxPublicChannels'])
emptyPublicChannels = int(settings['emptyPublicChannels'])
publicChannelNamePool = settings['publicChannelNamePool'].split(', ')
whitelistedUserIDs = settings['whitelistedUsers'].split(', ')
textChannelID = int(settings['textChannel'])
answer = settings['answer']
token = settings['token']

client = discord.Client(status = discord.Status.dnd)
c = 18 #fixed output name width

@client.event
async def on_voice_state_update(member, before, after):
  if client.is_ready() and before.channel != after.channel:
    if before.channel is None:
      print(f'{timeNow()} {str(member):{c}} joined at position    {str(after.channel.position)}')
    elif after.channel is None:
      print(f'{timeNow()} {str(member):{c}} left from position    {str(before.channel.position)}')
    else:
      print(f'{timeNow()} {str(member):{c}} moved from position   {str(before.channel.position)} to {str(after.channel.position)}')
    everyone = discord.utils.get(member.guild.roles, name='@everyone')
    allChannelNames = []
    hiddenChannels = []
    publicChannels = []
    for channel in member.guild.voice_channels:
      for overwrite in channel.overwrites_for(everyone):
        if overwrite[0] == 'read_messages':
          if overwrite[1] == False:
            hiddenChannels.append(channel)
          else:
            publicChannels.append(channel)
          allChannelNames.append(channel.name)

    # Public channel management
    unoccupiedPublicChannelsCount = 0
    unoccupiedPublicChannels = []
    for channel in publicChannels:
      if len(channel.members) == 0:
        unoccupiedPublicChannelsCount += 1
        unoccupiedPublicChannels.append(channel)
    if unoccupiedPublicChannelsCount < emptyPublicChannels and len(publicChannels) < maxPublicChannels:
      random.shuffle(publicChannelNamePool)
      for name in publicChannelNamePool:
        if name not in allChannelNames:
          clonedPublicChannel = await publicChannels[0].clone(name = name)
          break
    elif unoccupiedPublicChannelsCount > emptyPublicChannels and len(publicChannels) > minPublicChannels:
      await unoccupiedPublicChannels[len(unoccupiedPublicChannels) - 1].delete()

    # Hidden channel management
    unoccupiedHiddenChannelsCount = 0
    unoccupiedHiddenChannels = []
    for channel in hiddenChannels:
      if len(channel.members) == 0:
        unoccupiedHiddenChannelsCount += 1
        unoccupiedHiddenChannels.append(channel)
    if unoccupiedHiddenChannelsCount < emptyHiddenChannels and len(hiddenChannels) < maxHiddenChannels:
      random.shuffle(hiddenChannelNamePool)
      for name in hiddenChannelNamePool:
        if name not in allChannelNames:
          clonedHiddenChannel = await hiddenChannels[0].clone(name = name)
          await clonedHiddenChannel.edit(position=len(hiddenChannels))
          break
    elif unoccupiedHiddenChannelsCount > emptyHiddenChannels and len(hiddenChannels) > minHiddenChannels:
      await unoccupiedHiddenChannels[len(unoccupiedHiddenChannels) - 1].delete()

@client.event
async def on_guild_channel_create(channel):
  print(f'{timeNow()} {channel.name:{c}} created at position   {str(channel.position)}')
@client.event
async def on_guild_channel_delete(channel):
  print(f'{timeNow()} {channel.name:{c}} deleted from position {str(channel.position)}')
@client.event
async def on_guild_channel_update(before, after):
  if before.position != after.position:
    print(f'{timeNow()} {before.name:{c}} moved from position   {str(before.position)} to {str(after.position)}')

@client.event
async def on_message(message):
  if client.is_ready():
    if message.channel.type == discord.ChannelType.private:
      if str(message.author.id) in whitelistedUserIDs:
        for guild in client.guilds:
          textChannel = discord.utils.get(guild.text_channels, id = textChannelID)
          await textChannel.send(message.content)
      elif message.author != client.user:
        print(f'{timeNow()} {str(message.author):{c}} messaged: {message.content}')
        await message.channel.send(answer)

@client.event
async def on_ready():
  for guild in client.guilds:
    print(f'{timeNow()} {str(client.user):{c}} in {guild.name}')
  print('')
@client.event
async def on_connect():
  print(f'{timeNow()} Connected')
@client.event
async def on_disconnect():
  print(f'{timeNow()} Disconnected')
@client.event
async def on_resumed():
  print(f'{timeNow()} Resumed')

client.run(token)
