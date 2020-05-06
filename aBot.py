import discord,datetime,random,configparser,os
def timeNow(): return (datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') + ' ')

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
token = settings['token']



client = discord.Client()

@client.event
async def on_voice_state_update(member, before, after):
  if client.is_ready() and before.channel != after.channel:
    print(timeNow() + str(member) + ' moved')
    everyone = discord.utils.get(member.guild.roles, name='@everyone')
    allChannelNames = []
    hiddenChannels = []
    publicChannels = []
    for channel in member.guild.voice_channels:
      for overwrite in channel.overwrites_for(everyone):
        if overwrite[0] == 'read_messages':
          if overwrite[1] == False:
            hiddenChannels.append(channel)
            allChannelNames.append(channel.name)
          else:
            publicChannels.append(channel)
            allChannelNames.append(channel.name)

    # Public channel management
    unoccupiedPublicChannelsCount = 0
    unoccupiedPublicChannels = []
    for i,channel in enumerate(publicChannels):
      if len(channel.members) == 0:
        unoccupiedPublicChannelsCount += 1
        unoccupiedPublicChannels.append(channel)
    if unoccupiedPublicChannelsCount < emptyPublicChannels and len(publicChannels) < maxPublicChannels:
      random.shuffle(publicChannelNamePool)
      for name in publicChannelNamePool:
        if name not in allChannelNames:
          clonedPublicChannel = await publicChannels[0].clone(name = name)
          print(timeNow() + clonedPublicChannel.name + ' created')
          break
    elif unoccupiedPublicChannelsCount > emptyPublicChannels and len(publicChannels) > minPublicChannels:
      toDeletePublicChannel = unoccupiedPublicChannels[len(unoccupiedPublicChannels) - 1]
      await toDeletePublicChannel.delete()
      print(timeNow() + toDeletePublicChannel.name + ' deleted')

    # Hidden channel management
    unoccupiedHiddenChannelsCount = 0
    unoccupiedHiddenChannels = []
    for i,channel in enumerate(hiddenChannels):
      if len(channel.members) == 0:
        unoccupiedHiddenChannelsCount += 1
        unoccupiedHiddenChannels.append(channel)
    if unoccupiedHiddenChannelsCount < emptyHiddenChannels and len(hiddenChannels) < maxHiddenChannels:
      random.shuffle(hiddenChannelNamePool)
      for name in hiddenChannelNamePool:
        if name not in allChannelNames:
          clonedHiddenChannel = await hiddenChannels[0].clone(name = name)
          await clonedHiddenChannel.edit(position=len(hiddenChannels) + 1)
          print(timeNow() + clonedHiddenChannel.name + ' created')
          break
    elif unoccupiedHiddenChannelsCount > emptyHiddenChannels and len(hiddenChannels) > minHiddenChannels:
      toDeleteHiddenChannel = unoccupiedHiddenChannels[len(unoccupiedHiddenChannels) - 1]
      await toDeleteHiddenChannel.delete()
      print(timeNow() + toDeleteHiddenChannel.name + ' deleted')

@client.event
async def on_ready():
  for guild in client.guilds:
    print(timeNow() + 'Logged in as {0} in {1}'.format(client.user, guild.name))
@client.event
async def on_connect(): print(timeNow() + 'Connected ')
@client.event
async def on_disconnect(): print(timeNow() + 'Disconnected ')
@client.event
async def on_resumed(): print(timeNow() + 'Resumed ')
client.run(token)
