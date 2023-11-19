import os
from PIL import Image
from src.libraries.maimaidx_music import get_cover_len5_id, total_list


def computeRa(ds: float, achievement: float) -> int:
    baseRa = 22.4
    if achievement < 50:
        baseRa = 7.0
    elif achievement < 60:
        baseRa = 8.0
    elif achievement < 70:
        baseRa = 9.6
    elif achievement < 75:
        baseRa = 11.2
    elif achievement < 80:
        baseRa = 12.0
    elif achievement < 90:
        baseRa = 13.6
    elif achievement < 94:
        baseRa = 15.2
    elif achievement < 97:
        baseRa = 16.8
    elif achievement < 98:
        baseRa = 20.0
    elif achievement < 99:
        baseRa = 20.3
    elif achievement < 99.5:
        baseRa = 20.8
    elif achievement < 100:
        baseRa = 21.1
    elif achievement < 100.5:
        baseRa = 21.6

    return int(ds * (min(100.5, achievement) / 100) * baseRa)


def computeRa_b40(ds: float, achievement: float) -> int:
    baseRa = 14.0
    if achievement >= 50 and achievement < 60:
        baseRa = 5.0
    elif achievement < 70:
        baseRa = 6.0
    elif achievement < 75:
        baseRa = 7.0
    elif achievement < 80:
        baseRa = 7.5
    elif achievement < 90:
        baseRa = 8.0
    elif achievement < 94:
        baseRa = 9.0
    elif achievement < 97:
        baseRa = 10
    elif achievement < 98:
        baseRa = 12.5
    elif achievement < 99:
        baseRa = 12.7
    elif achievement < 99.5:
        baseRa = 13.0
    elif achievement < 100:
        baseRa = 13.2
    elif achievement < 100.5:
        baseRa = 13.5

    return int(ds * (min(100.5, achievement) / 100) * baseRa)


class ChartInfo(object):

    def __init__(self, idNum: str, diff: int, tp: str, achievement: float,
                 comboId: int, scoreId: int, title: str, ds: float, lv: str):
        self.idNum = int(idNum)
        self.diff = diff
        self.tp = tp
        self.achievement = achievement
        self.ra = computeRa(ds, achievement)
        self.ra_b40 = computeRa_b40(ds, achievement)
        self.comboId = comboId
        self.scoreId = scoreId
        self.title = title
        self.ds = ds
        self.lv = lv

    def __str__(self):
        return '%-50s' % f'{self.title} [{self.tp}]' + f'{self.ds}\t{diffs[self.diff]}\t{self.ra}'

    def __eq__(self, other):
        return self.ra == other.ra

    def __lt__(self, other):
        if self.ra == other.ra:
            if self.ds == other.ds:
                return self.achievement < other.achievement
            return self.ds < other.ds
        return self.ra < other.ra

    @classmethod
    def from_json(cls, data):
        rate = [
            'd', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss',
            'ssp', 'sss', 'sssp'
        ]
        ri = rate.index(data["rate"])
        fc = ['', 'fc', 'fcp', 'ap', 'app']
        fi = fc.index(data["fc"])
        ret = cls(idNum=total_list.by_title(data["title"]).id,
                  title=data["title"],
                  diff=data["level_index"],
                  ds=data["ds"],
                  comboId=fi,
                  scoreId=ri,
                  lv=data["level"],
                  achievement=data["achievements"],
                  tp=data["type"])
        return ret


class BestList(object):

    def __init__(self, size: int):
        self.data = []
        self.size = size

    def push(self, elem):
        if len(self.data) >= self.size and elem < self.data[-1]:
            return
        self.data.append(elem)
        self.data.sort()
        self.data.reverse()
        while (len(self.data) > self.size):
            del self.data[-1]

    def pop(self):
        del self.data[-1]

    def __str__(self):
        return '[\n\t' + ', \n\t'.join([str(ci) for ci in self.data]) + '\n]'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    @property
    def rating(self):
        return sum(i.ra for i in self.data)

    @property
    def rating_b40(self):
        return sum(i.ra_b40 for i in self.data)


class DrawBestBase():

    def __init__(self, sdBest: BestList, dxBest: BestList, userName: str):
        self.sdBest = sdBest
        self.dxBest = dxBest
        self.userName = self._stringQ2B(userName)
        self.pic_dir = 'src/static/mai/pic/'
        self.cover_dir = 'src/static/mai/cover/'
        self.cover_dir_aqua = 'src/static/mai/cover_aqua/'
        self.img = Image.open(self.pic_dir +
                              'UI_TTR_BG_Base_Plus.png').convert('RGBA')
        self.ROWS_IMG = [2]
        for i in range(6):
            self.ROWS_IMG.append(116 + 96 * i)

    def _Q2B(self, uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:  #转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)

    def _stringQ2B(self, ustring):
        """把字符串全角转半角"""
        return "".join([self._Q2B(uchar) for uchar in ustring])

    def _getCharWidth(self, o) -> int:
        widths = [(126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0),
                  (733, 1), (879, 0), (1154, 1), (1161, 0), (4347, 1),
                  (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0),
                  (9000, 1), (9002, 2), (11021, 1), (12350, 2), (12351, 1),
                  (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2),
                  (63743, 1), (64106, 2), (65039, 1), (65059, 0), (65131, 2),
                  (65279, 1), (65376, 2), (65500, 1), (65510, 2), (120831, 1),
                  (262141, 2), (1114109, 1)]
        if o == 0xe or o == 0xf:
            return 0
        for num, wid in widths:
            if o <= num:
                return wid
        return 1

    def _coloumWidth(self, s: str):
        res = 0
        for ch in s:
            res += self._getCharWidth(ord(ch))
        return res

    def _changeColumnWidth(self, s: str, len: int) -> str:
        res = 0
        sList = []
        for ch in s:
            res += self._getCharWidth(ord(ch))
            if res <= len:
                sList.append(ch)
        return ''.join(sList)

    def _resizePic(self, img: Image.Image, time: float):
        return img.resize((int(img.size[0] * time), int(img.size[1] * time)))

    def _drawRating(self, ratingBaseImg: Image.Image):
        COLOUMS_RATING = [86, 100, 115, 130, 145]
        theRa = self.playerRating
        i = 4
        while theRa:
            digit = theRa % 10
            theRa = theRa // 10
            digitImg = Image.open(
                self.pic_dir + f'UI_NUM_Drating_{digit}.png').convert('RGBA')
            digitImg = self._resizePic(digitImg, 0.6)
            ratingBaseImg.paste(digitImg, (COLOUMS_RATING[i] - 2, 9),
                                mask=digitImg.split()[3])
            i = i - 1
        return ratingBaseImg

    def getDir(self):
        return self.img

    def _getMusicCover(self, idNum):
        pngPath = self.cover_dir + f'{get_cover_len5_id(idNum)}.png'
        if not os.path.exists(pngPath):
            pngPath = self.cover_dir_aqua + f'UI_Jacket_{-int(idNum):06d}.png'
        if not os.path.exists(pngPath):
            pngPath = self.cover_dir + '01000.png'
        return pngPath
