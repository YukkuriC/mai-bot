import asyncio
import os
import math
from typing import Optional, Dict, List, Tuple

import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from src.libraries.maimaidx_music import total_list, get_cover_len5_id

from .maimai_rating_base import BestList, ChartInfo, DrawBestBase, \
                                scoreRank, combo, diffs


class DrawBest(DrawBestBase):

    def __init__(self, sdBest:BestList, dxBest:BestList, userName:str):
        super().__init__(sdBest, dxBest, userName)
        self.sdRating = sdBest.rating
        self.dxRating = dxBest.rating
        self.playerRating = self.sdRating + self.dxRating
        self.COLOUMS_IMG = []
        for i in range(8):
            self.COLOUMS_IMG.append(2 + 138 * i)
        for i in range(4):
            self.COLOUMS_IMG.append(988 + 138 * i)
        self.draw()

    def _findRaPic(self) -> str:
        num = '10'
        if self.playerRating < 1000:
            num = '01'
        elif self.playerRating < 2000:
            num = '02'
        elif self.playerRating < 4000:
            num = '03'
        elif self.playerRating < 7000:
            num = '04'
        elif self.playerRating < 10000:
            num = '05'
        elif self.playerRating < 12000:
            num = '06'
        elif self.playerRating < 13000:
            num = '07'
        elif self.playerRating < 14500:
            num = '08'
        elif self.playerRating < 15000:
            num = '09'
        return f'UI_CMN_DXRating_S_{num}.png'

    def _drawBestList(self, img:Image.Image, sdBest:BestList, dxBest:BestList):
        itemW = 131
        itemH = 88
        Color = [(69, 193, 36), (255, 186, 1), (255, 90, 102), (134, 49, 200), (217, 197, 233)]
        levelTriagle = [(itemW, 0), (itemW - 27, 0), (itemW, 27)]
        rankPic = 'D C B BB BBB A AA AAA S Sp SS SSp SSS SSSp'.split(' ')
        comboPic = ' FC FCp AP APp'.split(' ')
        imgDraw = ImageDraw.Draw(img)
        titleFontName = 'src/static/adobe_simhei.otf'
        for num in range(0, len(sdBest)):
            i = num // 7
            j = num % 7
            chartInfo = sdBest[num]
            pngPath = self._getMusicCover(chartInfo.idNum)
            temp = Image.open(pngPath).convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 16, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 15:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (72, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert('RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (103, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j] + 4, self.ROWS_IMG[i + 1] + 4))
        # 不画空占位了
        for num in range(0, len(dxBest)):
            i = num // 3
            j = num % 3
            chartInfo = dxBest[num]
            pngPath = self._getMusicCover(chartInfo.idNum)
            temp = Image.open(pngPath).convert('RGB')
            temp = self._resizePic(temp, itemW / temp.size[0])
            temp = temp.crop((0, (temp.size[1] - itemH) / 2, itemW, (temp.size[1] + itemH) / 2))
            temp = temp.filter(ImageFilter.GaussianBlur(3))
            temp = temp.point(lambda p: int(p * 0.72))

            tempDraw = ImageDraw.Draw(temp)
            tempDraw.polygon(levelTriagle, Color[chartInfo.diff])
            font = ImageFont.truetype(titleFontName, 14, encoding='utf-8')
            title = chartInfo.title
            if self._coloumWidth(title) > 13:
                title = self._changeColumnWidth(title, 12) + '...'
            tempDraw.text((8, 8), title, 'white', font)
            font = ImageFont.truetype(titleFontName, 12, encoding='utf-8')

            tempDraw.text((7, 28), f'{"%.4f" % chartInfo.achievement}%', 'white', font)
            rankImg = Image.open(self.pic_dir + f'UI_GAM_Rank_{rankPic[chartInfo.scoreId]}.png').convert('RGBA')
            rankImg = self._resizePic(rankImg, 0.3)
            temp.paste(rankImg, (72, 28), rankImg.split()[3])
            if chartInfo.comboId:
                comboImg = Image.open(self.pic_dir + f'UI_MSS_MBase_Icon_{comboPic[chartInfo.comboId]}_S.png').convert(
                    'RGBA')
                comboImg = self._resizePic(comboImg, 0.45)
                temp.paste(comboImg, (103, 27), comboImg.split()[3])
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 12, encoding='utf-8')
            tempDraw.text((8, 44), f'Base: {chartInfo.ds} -> {chartInfo.ra}', 'white', font)
            font = ImageFont.truetype('src/static/adobe_simhei.otf', 18, encoding='utf-8')
            tempDraw.text((8, 60), f'#{num + 1}', 'white', font)

            recBase = Image.new('RGBA', (itemW, itemH), 'black')
            recBase = recBase.point(lambda p: int(p * 0.8))
            img.paste(recBase, (self.COLOUMS_IMG[j + 8] + 5, self.ROWS_IMG[i + 1] + 5))
            img.paste(temp, (self.COLOUMS_IMG[j + 8] + 4, self.ROWS_IMG[i + 1] + 4))
        # nope

    def draw(self):
        splashLogo = Image.open(self.pic_dir + 'UI_CMN_TabTitle_MaimaiTitle_Ver214.png').convert('RGBA')
        splashLogo = self._resizePic(splashLogo, 0.65)
        self.img.paste(splashLogo, (10, 10), mask=splashLogo.split()[3])

        ratingBaseImg = Image.open(self.pic_dir + self._findRaPic()).convert('RGBA')
        ratingBaseImg = self._drawRating(ratingBaseImg)
        ratingBaseImg = self._resizePic(ratingBaseImg, 0.85)
        self.img.paste(ratingBaseImg, (240, 8), mask=ratingBaseImg.split()[3])

        namePlateImg = Image.open(self.pic_dir + 'UI_TST_PlateMask.png').convert('RGBA')
        namePlateImg = namePlateImg.resize((285, 40))
        namePlateDraw = ImageDraw.Draw(namePlateImg)
        font1 = ImageFont.truetype('src/static/msyh.ttc', 28, encoding='unic')
        namePlateDraw.text((12, 4), ' '.join(list(self.userName)), 'black', font1)
        nameDxImg = Image.open(self.pic_dir + 'UI_CMN_Name_DX.png').convert('RGBA')
        nameDxImg = self._resizePic(nameDxImg, 0.9)
        namePlateImg.paste(nameDxImg, (230, 4), mask=nameDxImg.split()[3])
        self.img.paste(namePlateImg, (240, 40), mask=namePlateImg.split()[3])

        shougouImg = Image.open(self.pic_dir + 'UI_CMN_Shougou_Rainbow.png').convert('RGBA')
        shougouDraw = ImageDraw.Draw(shougouImg)
        font2 = ImageFont.truetype('src/static/adobe_simhei.otf', 14, encoding='utf-8')
        playCountInfo = f'SD: {self.sdRating} + DX: {self.dxRating} = {self.playerRating}'
        shougouImgW, shougouImgH = shougouImg.size
        playCountInfoW, playCountInfoH = shougouDraw.textsize(playCountInfo, font2)
        textPos = ((shougouImgW - playCountInfoW - font2.getoffset(playCountInfo)[0]) / 2, 5)
        shougouDraw.text((textPos[0] - 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1]), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0], textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] - 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] - 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text((textPos[0] + 1, textPos[1] + 1), playCountInfo, 'black', font2)
        shougouDraw.text(textPos, playCountInfo, 'white', font2)
        shougouImg = self._resizePic(shougouImg, 1.05)
        self.img.paste(shougouImg, (240, 83), mask=shougouImg.split()[3])

        self._drawBestList(self.img, self.sdBest, self.dxBest)

        authorBoardImg = Image.open(self.pic_dir + 'UI_CMN_MiniDialog_01.png').convert('RGBA')
        authorBoardImg = self._resizePic(authorBoardImg, 0.35)
        authorBoardDraw = ImageDraw.Draw(authorBoardImg)
        authorBoardDraw.text((31, 28), '   Generated By\nXybBot & Chiyuki', 'black', font2)
        self.img.paste(authorBoardImg, (1224, 19), mask=authorBoardImg.split()[3])

        dxImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_01.png').convert('RGBA')
        self.img.paste(dxImg, (988, 65), mask=dxImg.split()[3])
        sdImg = Image.open(self.pic_dir + 'UI_RSL_MBase_Parts_02.png').convert('RGBA')
        self.img.paste(sdImg, (865, 65), mask=sdImg.split()[3])

        # self.img.show()


async def generate50(payload: Dict) -> Tuple[Optional[Image.Image], bool]:
    return generate50_img(*(await generate50_query(payload)))


async def generate50_query(payload: Dict) -> Tuple[Optional[Image.Image], bool]:
    async with aiohttp.request("POST", "https://www.diving-fish.com/api/maimaidxprober/query/player", json=payload) as resp:
        if resp.status == 400:
            return None, 400
        if resp.status == 403:
            return None, 403
        obj = await resp.json()
        return obj, 0


def generate50_img(obj, status) -> Tuple[Optional[Image.Image], bool]:
    if status == 400:
        return None, 400
    if status == 403:
        return None, 403
    sd_best = BestList(35)
    dx_best = BestList(15)
    dx: List[Dict] = obj["charts"]["dx"]
    sd: List[Dict] = obj["charts"]["sd"]
    for c in sd:
        sd_best.push(ChartInfo.from_json(c))
    for c in dx:
        dx_best.push(ChartInfo.from_json(c))
    pic = DrawBest(sd_best, dx_best, obj["nickname"]).getDir()
    return pic, 0


def generate50_diff(source, target):
    sd_map, dx_map = {}, {}
    sd_base = dx_base = 1e10
    for sd_chart in source["charts"]["sd"]:
        sd_base = min(sd_base, sd_chart["ra"])
        sd_map[sd_chart["song_id"], sd_chart["level_index"]] = sd_chart["ra"]
    for dx_chart in source["charts"]["dx"]:
        dx_base = min(dx_base, dx_chart["ra"])
        dx_map[dx_chart["song_id"], dx_chart["level_index"]] = dx_chart["ra"]

    # 怎么会有人b50填不满的（恼
    if len(source["charts"]["dx"]) < 15:
        dx_base = 0
    if len(source["charts"]["sd"]) < 35:
        sd_base = 0

    sd_best = BestList(35)
    dx_best = BestList(15)

    for sd_chart in target["charts"]["sd"]:
        ra_key = sd_chart["song_id"], sd_chart["level_index"]
        delta_score = min(sd_chart["ra"] - sd_map.get(ra_key, 0),
                          sd_chart["ra"] - sd_base)
        if delta_score <= 0:
            continue
        chart = ChartInfo.from_json(sd_chart)
        chart.ra = delta_score
        sd_best.push(chart)

    for dx_chart in target["charts"]["dx"]:
        if dx_chart["ra"] <= dx_base:
            continue
        ra_key = dx_chart["song_id"], dx_chart["level_index"]
        delta_score = min(dx_chart["ra"] - dx_map.get(ra_key, 0),
                          dx_chart["ra"] - dx_base)
        if delta_score <= 0:
            continue
        chart = ChartInfo.from_json(dx_chart)
        chart.ra = delta_score
        dx_best.push(chart)

    return DrawBest(sd_best, dx_best, target["nickname"]).getDir()
