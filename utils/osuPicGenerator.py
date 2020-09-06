from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
import io
import aiohttp
from database import OsuStats, get_or_none, manager


PATH = "plugins/osuPicGenerator/"


class osuPicGenerator:

    def __init__(self, server, nickname, vk_id, mode):
        self.server = server
        self.nickname = nickname
        self.playUserID = 0
        self.country = ""
        self.avatar_server = ""
        self.vk_id = vk_id

        self.fonts = [
            ImageFont.truetype(PATH+"arial_regular.ttf", 29),
            ImageFont.truetype(PATH+"arial_bold.ttf", 29),
            ImageFont.truetype(PATH+"symbola.ttf", 29)
        ]
        self.base_img = Image.open(PATH+"bg.png").convert("RGBA")
        self.base_img_alpha = Image.open(PATH+"bg.png").convert("RGBA")

        self.colors = [
            (255, 255, 255),  # white
            (0, 255, 0),  # greeen
            (255, 0, 0),  # red
            (155, 155, 155)  # grey
        ]

        self.playModeStr = mode

        self.isHaveApiSS = False
        self.stats = []
        self.stats_graph = []

        self.osuApiKey = "<osu_token>"

        self.generatedPic = None
    
    @property
    def playMode(self):
        if self.playModeStr == "std":
            return 0
        elif self.playModeStr == "taiko":
            return 1
        elif self.playModeStr == "ctb":
            return 2
        elif self.playModeStr == "mania":
            return 3


    def toFixed(self, numObj, digits=0):
        return f"{numObj:.{digits}f}"


    def humanize(self, value):
        return "{:,}".format(round(value)).replace(",", ".")
    

    async def getStats(self):
        prev_stats = await get_or_none(OsuStats, server=self.server, nickname=self.nickname, mode=self.playModeStr)
        if not prev_stats:
            prev_stats = await manager.create_or_get(OsuStats, server=self.server, nickname=self.nickname, mode=self.playModeStr)
            prev_stats = prev_stats[0]
        
        if self.server == "ofc":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://osu.ppy.sh/api/get_user", params={
                    'k': self.osuApiKey,
                    'u': self.nickname
                }) as response:
                        info = await response.json()
            except Exception as e:
                print(e)
                return
            
            self.isHaveApiSS = True
            self.stats = [
                self.humanize(int(info[0]['pp_rank'])),
                self.humanize(int(info[0]['pp_country_rank'])),
                self.humanize(int(float(info[0]['pp_raw']))),
                self.humanize(int(info[0]['playcount'])),
                int(float(info[0]['level'])),
                self.toFixed(float(info[0]['accuracy']), 2),
                self.humanize(int(info[0]['count_rank_ssh'])),
                self.humanize(int(info[0]['count_rank_ss'])),
                self.humanize(int(info[0]['count_rank_sh'])),
                self.humanize(int(info[0]['count_rank_s'])),
                self.humanize(int(info[0]['count_rank_a']))
            ]

            old_stats = eval(prev_stats.stat)
            self.stats_graph = [
                [old_stats[0], int(info[0]['pp_rank'])],
                [old_stats[1], int(info[0]['pp_country_rank'])],
                [old_stats[2], int(float(info[0]['pp_raw']))],
                [old_stats[3], int(info[0]['playcount'])],
                [old_stats[4], int(float(info[0]['level']))],
                [old_stats[5], float(info[0]['accuracy'])],
                [old_stats[6], int(info[0]['count_rank_ssh'])],
                [old_stats[7], int(info[0]['count_rank_ss'])],
                [old_stats[8], int(info[0]['count_rank_sh'])],
                [old_stats[9], int(info[0]['count_rank_s'])],
                [old_stats[10], int(info[0]['count_rank_a'])],
            ]

            new_stats = [
                int(info[0]['pp_rank']), int(info[0]['pp_country_rank']), 
                int(float(info[0]['pp_raw'])), int(info[0]['playcount']),
                int(float(info[0]['level'])), float(info[0]['accuracy']),
                int(info[0]['count_rank_ssh']), int(info[0]['count_rank_ss']),
                int(info[0]['count_rank_sh']), int(info[0]['count_rank_s']),
                int(info[0]['count_rank_a'])
            ]

            prev_stats.stat = str(new_stats)
            
            self.playUserID = info[0]['user_id']
            self.country = info[0]['country']
            self.avatar_server = "https://a.ppy.sh/"
            await manager.update(prev_stats)
        elif self.server == "kurikku":
            print(self.nickname)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://kurikku.pw/api/v1/users/full", params={
                        'name': self.nickname
                }) as response:
                        info = await response.json()
    
                if info['code'] != 200:
                    raise Exception()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://kurikku.pw/api/v1/scores/ranksget", params={
                        'userid': info['id'],
                        'mode': self.playMode
                }) as response:
                        infoRanks = await response.json()
            except Exception as e:
                print(e)
                return
            
            self.isHaveApiSS = True
            self.stats = [
                self.humanize(info[self.playModeStr]['global_leaderboard_rank']),
                self.humanize(info[self.playModeStr]['country_leaderboard_rank']),
                self.humanize(int(info[self.playModeStr]['pp'])),
                self.humanize(info[self.playModeStr]['playcount']),
                int(info[self.playModeStr]['level']),
                self.toFixed(info[self.playModeStr]['accuracy'], 2),
                self.humanize(infoRanks['sshd']),
                self.humanize(infoRanks['ss']),
                self.humanize(infoRanks['sh']),
                self.humanize(infoRanks['s']),
                self.humanize(infoRanks['a'])
            ]

            old_stats = eval(prev_stats.stat)
            self.stats_graph = [
                [old_stats[0], info[self.playModeStr]['global_leaderboard_rank']],
                [old_stats[1], info[self.playModeStr]['country_leaderboard_rank']],
                [old_stats[2], int(info[self.playModeStr]['pp'])],
                [old_stats[3], info[self.playModeStr]['playcount']],
                [old_stats[4], int(info[self.playModeStr]['level'])],
                [old_stats[5], info[self.playModeStr]['accuracy']],
                [old_stats[6], infoRanks['sshd']],
                [old_stats[7], infoRanks['ss']],
                [old_stats[8], infoRanks['sh']],
                [old_stats[9], infoRanks['s']],
                [old_stats[10], infoRanks['a']]
            ]

            new_stats = [
                info[self.playModeStr]['global_leaderboard_rank'], info[self.playModeStr]['country_leaderboard_rank'],
                int(info[self.playModeStr]['pp']), info[self.playModeStr]['playcount'],
                int(info[self.playModeStr]['level']), info[self.playModeStr]['accuracy'],
                infoRanks['sshd'], infoRanks['ss'], infoRanks['sh'], infoRanks['s'], infoRanks['a']
            ]

            prev_stats.stat = str(new_stats)
            self.playUserID = info['id']
            self.country = info['country']
            self.avatar_server = "https://a.kurikku.pw/"
            await manager.update(prev_stats)
        elif self.server == "gatari":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.gatari.pw/users/get", params={
                    'u': self.nickname
                }) as response:
                        infoGet = await response.json() 

                async with aiohttp.ClientSession() as session:
                    async with session.get("https://api.gatari.pw/user/stats", params={
                    'u': self.nickname,
                    'mode': self.playMode
                }) as response:
                        infoStats = await response.json() 

                a = infoStats['stats']['rank']
            except:
                return
            
            self.isHaveApiSS = True
            self.stats = [
                self.humanize(infoStats['stats']['rank']),
                self.humanize(infoStats['stats']['country_rank']),
                self.humanize(int(infoStats['stats']['pp'])),
                self.humanize(infoStats['stats']['playcount']),
                self.humanize(int(infoStats['stats']['level'])),
                self.toFixed(infoStats['stats']['avg_accuracy'], 2),
                self.humanize(infoStats['stats']['xh_count']),
                self.humanize(infoStats['stats']['x_count']),
                self.humanize(infoStats['stats']['sh_count']),
                self.humanize(infoStats['stats']['s_count']),
                self.humanize(infoStats['stats']['a_count']),
            ]
            
            old_stats = eval(prev_stats.stat)
            self.stats_graph = [
                [old_stats[0], infoStats['stats']['rank']],
                [old_stats[1], infoStats['stats']['country_rank']],
                [old_stats[2], int(infoStats['stats']['pp'])],
                [old_stats[3], infoStats['stats']['playcount']],
                [old_stats[4], int(infoStats['stats']['level'])],
                [old_stats[5], infoStats['stats']['avg_accuracy']],
                [old_stats[6], infoStats['stats']['xh_count']],
                [old_stats[7], infoStats['stats']['x_count']],
                [old_stats[8], infoStats['stats']['sh_count']],
                [old_stats[9], infoStats['stats']['s_count']],
                [old_stats[10], infoStats['stats']['a_count']]
            ]

            new_stats = [
                infoStats['stats']['rank'], infoStats['stats']['country_rank'],
                int(infoStats['stats']['pp']), infoStats['stats']['playcount'],
                int(infoStats['stats']['level']), infoStats['stats']['avg_accuracy'],
                infoStats['stats']['xh_count'], infoStats['stats']['x_count'],
                infoStats['stats']['sh_count'], infoStats['stats']['s_count'],
                infoStats['stats']['a_count']
            ]

            prev_stats.stat = str(new_stats)
            self.playUserID = infoGet['users'][0]['id']
            self.country = infoGet['users'][0]['country']
            self.avatar_server = "https://a.gatari.pw/"
            await manager.update(prev_stats)
        elif self.server == "akatsuki":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://akatsuki.pw/api/v1/users/full", params={
                    'name': self.nickname
                }) as response:
                        info = await response.json()

                if info['code'] != 200:
                    raise Exception()
            except Exception as e:
                return
            
            self.isHaveApiSS = False
            self.stats = [
                self.humanize(info[self.playModeStr]['global_leaderboard_rank']),
                self.humanize(info[self.playModeStr]['country_leaderboard_rank']),
                self.humanize(int(info[self.playModeStr]['pp'])),
                self.humanize(info[self.playModeStr]['playcount']),
                int(info[self.playModeStr]['level']),
                self.toFixed(info[self.playModeStr]['accuracy'], 2)
            ]

            old_stats = eval(prev_stats.stat)
            self.stats_graph = [
                [old_stats[0], info[self.playModeStr]['global_leaderboard_rank']],
                [old_stats[1], info[self.playModeStr]['country_leaderboard_rank']],
                [old_stats[2], int(info[self.playModeStr]['pp'])],
                [old_stats[3], info[self.playModeStr]['playcount']],
                [old_stats[4], int(info[self.playModeStr]['level'])],
                [old_stats[5], info[self.playModeStr]['accuracy']]
            ]

            new_stats = [
                info[self.playModeStr]['global_leaderboard_rank'], info[self.playModeStr]['country_leaderboard_rank'],
                int(info[self.playModeStr]['pp']), info[self.playModeStr]['playcount'], int(info[self.playModeStr]['level']),
                info[self.playModeStr]['accuracy']
            ]

            prev_stats.stat = str(new_stats)
            self.playUserID = info['id']
            self.country = info['country']
            self.avatar_server = "https://a.akatsuki.pw/"
            await manager.update(prev_stats)
        elif self.server == "ripple":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get("https://ripple.moe/api/v1/users/full", params={
                    'name': self.nickname
                }) as response:
                        info = await response.json()

                if info['code'] != 200:
                    raise Exception()
            except Exception as e:
                return
            
            self.isHaveApiSS = False
            self.stats = [
                self.humanize(info[self.playModeStr]['global_leaderboard_rank']),
                self.humanize(info[self.playModeStr]['country_leaderboard_rank']),
                self.humanize(int(info[self.playModeStr]['pp'])),
                self.humanize(info[self.playModeStr]['playcount']),
                int(info[self.playModeStr]['level']),
                self.toFixed(info[self.playModeStr]['accuracy'], 2)
            ]

            old_stats = eval(prev_stats.stat)
            self.stats_graph = [
                [old_stats[0], info[self.playModeStr]['global_leaderboard_rank']],
                [old_stats[1], info[self.playModeStr]['country_leaderboard_rank']],
                [old_stats[2], int(info[self.playModeStr]['pp'])],
                [old_stats[3], info[self.playModeStr]['playcount']],
                [old_stats[4], int(info[self.playModeStr]['level'])],
                [old_stats[5], info[self.playModeStr]['accuracy']]
            ]

            new_stats = [
                info[self.playModeStr]['global_leaderboard_rank'], info[self.playModeStr]['country_leaderboard_rank'],
                int(info[self.playModeStr]['pp']), info[self.playModeStr]['playcount'], int(info[self.playModeStr]['level']),
                info[self.playModeStr]['accuracy']
            ]

            prev_stats.stat = str(new_stats)
            self.playUserID = info['id']
            self.country = info['country']
            self.avatar_server = "https://a.ripple.moe/"
            await manager.update(prev_stats)


    async def generate(self):
        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"{self.avatar_server}{self.playUserID}") as response:
                avatar = Image.open(io.BytesIO(await response.read())).convert("RGBA")

        async with aiohttp.ClientSession() as sess:
            async with sess.get(f"https://osu.ppy.sh/images/flags/{self.country}.png") as response:
                flag = Image.open(io.BytesIO(await response.read())).convert("RGBA")

        if self.playModeStr == "std":
            mode_img = Image.open(PATH+"osu.png").convert("RGBA").resize((50, 50), Image.ANTIALIAS)
        elif self.playModeStr == "mania":
            mode_img = Image.open(PATH+"mania.png").convert("RGBA").resize((50, 50), Image.ANTIALIAS)
        elif self.playModeStr == "ctb":
            mode_img = Image.open(PATH+"ctb.png").convert("RGBA").resize((50, 50), Image.ANTIALIAS)
        elif self.playModeStr == "taiko":
            mode_img = Image.open(PATH+"taiko.png").convert("RGBA").resize((50, 50), Image.ANTIALIAS)

        self.base_img.paste(avatar.resize((self.base_img.size), Image.ANTIALIAS))
        self.base_img.paste(self.base_img_alpha, (0,0), mask=self.base_img_alpha)

        if avatar.size[0] - avatar.size[1] != 0:
            # need crop to square
            avatar.crop((0, 0, 0, avatar.size[1]-avatar.size[0]))

        avatar = avatar.resize((200, 200), Image.ANTIALIAS)

        ll_size = (1000, 1000)
        mask = Image.new('L', ll_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + ll_size, fill=255)
        mask = ImageOps.fit(mask, avatar.size, method=Image.BICUBIC, centering=(0.5, 0.5))
        avatar.putalpha(mask)

        self.base_img.paste(avatar, (45, 187), avatar)
        self.base_img.paste(flag, (70, 420), flag)
        self.base_img.paste(mode_img, (170, 417), mode_img)

        draw = ImageDraw.Draw(self.base_img)
        draw.text((378, 80), text="Stats for:", fill=self.colors[0], font=self.fonts[0], align="center")
        draw.text((490, 80), text=f" {self.nickname} (на {self.server})", fill=self.colors[0], font=self.fonts[1], align="left")

        base_stats_1 = '''Ранк:
Ранк по стране:
PP:
Play Count:
Уровень:
Аккуратность:
SS(hd):
SS:
S(hd):
S:
A:'''.split("\n")

        base_stats_2 = '''Ранк:
Ранк по стране:
PP:
Play Count:
Уровень:
Аккуратность:'''.split("\n")

        text_coord = (274, 138)
        coordinates_to_draw = []
        coordinates_to_draw_graphs = []
        for x in (base_stats_1 if self.isHaveApiSS else base_stats_2):
            w, h = draw.textsize(x, font=self.fonts[0])
            coordinates_to_draw.append((text_coord[0] + w + 5, text_coord[1]+2))

            draw.text(text_coord, x, fill=self.colors[0], font=self.fonts[0], align="left")
            text_coord = (text_coord[0], text_coord[1]+37)

        pos = 0
        for x in self.stats:
            w, h = draw.textsize(str(x), font=self.fonts[1])
            coordinates_to_draw_graphs.append((coordinates_to_draw[pos][0] + w + 5, coordinates_to_draw[pos][1]+2))
            draw.text(coordinates_to_draw[pos], str(x), fill=self.colors[0], font=self.fonts[1])
            pos+=1

        pos = 0    
        for x in self.stats_graph:
            whatToDraw = ["", "", ()]
            if x[0] == x[1]:
                whatToDraw = ["🡙", "0", self.colors[3]]
            elif x[0] > x[1]:
                whatToDraw = ["🡓", f"{self.humanize(x[1]-x[0])}", self.colors[2]]
            elif x[0] < x[1]:
                whatToDraw = ["🡑", f"+{self.humanize(x[1]-x[0])}", self.colors[1]]

            draw.text(coordinates_to_draw_graphs[pos], text=f"{whatToDraw[0]}", font=self.fonts[2], fill=whatToDraw[2], align="left")
            draw.text((coordinates_to_draw_graphs[pos][0]+25, coordinates_to_draw_graphs[pos][1]-1), font=self.fonts[1], text=f"{whatToDraw[1]}", fill=whatToDraw[2], align="left")
            pos+=1

        buffer = io.BytesIO()
        self.base_img.save(buffer, format='PNG')
        buffer.seek(0)

        self.generatedPic = buffer
