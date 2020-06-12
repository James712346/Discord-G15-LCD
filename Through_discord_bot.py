import os, time, PIL,numpy, timeit, itertools, GLCD_SDK, platform, ctypes,asyncio, PIL.ImageOps, discord, keyboard
from PIL import Image, ImageDraw, ImageSequence, ImageFont
GLCD_SDK.initDLL("C:\\Program Files\\Logitech Gaming Software\\SDK\\LCD\\x86\\LogitechLcd.dll")
GLCD_SDK.LogiLcdInit("Python",GLCD_SDK.TYPE_COLOR+GLCD_SDK.TYPE_MONO)
Pixel_on = 128
Pixel_off = 127
Blankscreen = Image.fromarray( numpy.ones((43,160),dtype=numpy.uint8) * Pixel_off)
discordapi = "Njk2NTM0ODc0MTYwNjI3NzMz.Xq07cw.LjdTam3wEpemUtxJFPVeN_wz9k4"
userid = 341164679701463040
client = discord.Client()
current_session = None
class WrongSize(Exception):
    pass

def Startlogi():
    GLCD_SDK.LogiLcdInit("Python",GLCD_SDK.TYPE_COLOR+GLCD_SDK.TYPE_MONO)

def imageobjectsend(img, offset = (0,0), center=False, invert=False):
    background = Blankscreen
    if type(img) is list:
        offset = (0,0)
        for image in img:
            background.paste(image, offset)
            offset = (offset[0] + image.size[0],0)
    else:
        if center:
            offset = ((160-img.size[0])//2,0)
        if img.size != (43, 160):
            background.paste(img, offset)
        else:
            background = img
    if invert:
        background = PIL.ImageOps.invert(background)
    GLCD_SDK.LogiLcdMonoSetBackground((ctypes.c_ubyte * 6880)(*list(background.getdata()) ))
    GLCD_SDK.LogiLcdUpdate()

def convertimage(img):
    if type(img) == str:
        img = Image.open(img)
    img = img.convert('L')
    #img = PIL.ImageOps.invert(img)
    width, height = 160, 43
    if width/height >= img.size[0]/img.size[1]:
        width = int(43*(img.size[0]/img.size[1]))
    else:
        height = int(160*(img.size[1]/img.size[0]))
    if img.size != (width, height):
        img = img.resize((width,height), Image.LANCZOS)
    return img

def animation(img, framerate = 15):
    if type(img) == str:
        img = Image.open(img)
    for frame in ImageSequence.Iterator(img):
        imageobjectsend(convertimage(frame))
        time.sleep(1/framerate)

class DiscordVC:
    def __init__(self, title, usercount, userstate = 0):
        Startlogi()
        self.background = Blankscreen
        self.titlefont = ImageFont.truetype("assets\\font.ttf", 10)
        self.itemfont = ImageFont.truetype("assets\\font.ttf", 8)
        self.countfont = ImageFont.truetype("assets\\font.ttf", 16)
        self.title = Image.fromarray( numpy.ones((14,129),dtype=numpy.uint8) * Pixel_off)
        self.title_draw = ImageDraw.Draw(self.title)
        self.title_draw.text((4, 1),title.title(),Pixel_on, font=self.titlefont)
        self.vcstatus = "You Joined the VC"
        self.count = usercount
        self.status = [PIL.ImageOps.invert(Image.open('assets\\'+file).convert('L')) for file in ["unmute.png","talking.png","muted.png","deafened.png"]]
        self.Setstatus = userstate
        self.user_talking = []
        self.update()

    def shutdown(self):
        GLCD_SDK.LogiLcdShutdown()
        self = None

    def talking(self,name,id):
        user = PIL.ImageOps.invert(Image.open('assets\\person-talking.png').convert('L'))
        user_draw = ImageDraw.Draw(user)
        user_draw.text((10, 0),name,Pixel_on, font=self.itemfont)
        self.user_talking.insert(0,[id,user])
        self.update()

    def nottalking(self,id):
        List = [i[0] for i in self.user_talking]
        user_draw.text((10, 0),name,Pixel_on, font=self.itemfont)
        self.user_talking.pop(List.index(id))
        print(user_talking)
        self.update()


    def userconnected(self, name):
        self.vcstatus = name+" connected"
        self.count +=1
        self.update()

    def userdisconnect(self, name, tochannel = None):
        self.vcstatus = name+" disconnected"
        self.count-=1
        if tochannel:
            self.vcstatus = name+" wento "+ tochannel
        self.update()

    def userstatus(self, status=0):
        self.Setstatus = status
        self.update()
        pass

    def update(self):
        offset = (0,0)
        talk = Image.fromarray( numpy.ones((24,129),dtype=numpy.uint8) * Pixel_off)
        for user in self.user_talking:
            talk.paste(user[1], offset)
            if offset[0] == 65:
                offset = (0,offset[1]+8)
            else:
                offset = (65,offset[1])
        vcstatus = Image.fromarray( numpy.ones((7,160),dtype=numpy.uint8) * Pixel_on)
        vcstatus_draw = ImageDraw.Draw(vcstatus)
        vcstatus_draw.text((4, 0),self.vcstatus,Pixel_off, font=self.itemfont)
        count = Image.fromarray( numpy.ones((29,31),dtype=numpy.uint8) * Pixel_off)
        count_draw = ImageDraw.Draw(count)
        count_draw.text((2, 5),str(self.count),Pixel_on, font=self.countfont)
        self.background.paste(self.title)
        self.background.paste(talk, (0,20))
        self.background.paste(count, (129,20))
        self.background.paste(self.status[self.Setstatus], (129,0))
        self.background.paste(vcstatus, (0,12)) #(0,37)
        imageobjectsend(self.background)
        pass

class DiscordMsg:
    def __init__(self):
        pass

@client.event
async def on_ready():
    global current_session
    print('We have logged in as {0.user}'.format(client))
    SERVERS = client.guilds
    for server in SERVERS:
        if server.get_member(userid).voice:
            user_state = 3 if server.get_member(userid).voice.deaf or server.get_member(userid).voice.self_deaf else 2 if server.get_member(userid).voice.mute or server.get_member(userid).voice.self_mute else 0
            current_session = DiscordVC(server.get_member(userid).voice.channel.name,len(server.get_member(userid).voice.channel.members),user_state)
            [current_session.talking(mem.display_name, mem.id) for mem in server.get_member(userid).voice.channel.members]

@client.event
async def on_voice_state_update(member, before, after):
    global current_session
    if after.channel is None:
        if before.channel.guild.get_member(userid) == member:
            current_session.shutdown()
            print(current_session)
        else:
            current_session.userdisconnect(member.display_name)
            current_session.nottalking(member.id)
    elif after.channel.guild.get_member(userid) in after.channel.members:
        if member == after.channel.guild.get_member(userid):
            user_state = 3 if after.deaf or after.self_deaf else 2 if after.mute or after.self_mute else 0
            print("user update")
            if not before.channel == after.channel and after.channel is not None:
                current_session = DiscordVC(after.channel.name,len(after.channel.members),user_state)
                [current_session.talking(mem.display_name, mem.id) for mem in after.channel.members]
            else:
                current_session.userstatus(user_state)
        else:
            current_session.userconnected(member.display_name)
            current_session.talking(member.display_name, member.id)
    elif before.channel.guild.get_member(userid) in before.channel.members:
        print("Guy moved")
        current_session.userdisconnect(member.display_name, after.channel.name)
        current_session.nottalking(member.id)

async def keyboardbuttons():
    while True:
        if current_session:
            if GLCD_SDK.LogiLcdIsButtonPressed(GLCD_SDK.MONO_BUTTON_2):
                keyboard.press_and_release('ctrl+alt+1+2+3+4+5')
                while GLCD_SDK.LogiLcdIsButtonPressed(GLCD_SDK.MONO_BUTTON_2):
                    pass
                print("sendingkey sendingMute")
            elif GLCD_SDK.LogiLcdIsButtonPressed(GLCD_SDK.MONO_BUTTON_3):
                keyboard.press_and_release('ctrl+alt+6+7+8+9+0')
                while GLCD_SDK.LogiLcdIsButtonPressed(GLCD_SDK.MONO_BUTTON_3):
                    pass
                print("sendingkey sendingDefen")
        await asyncio.sleep(0.1)

client.loop.create_task(keyboardbuttons())
client.run(discordapi)

#while True:
#    animation('gay.gif',5)
