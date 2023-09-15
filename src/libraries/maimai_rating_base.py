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
                 ra: int, comboId: int, scoreId: int, title: str, ds: float,
                 lv: str):
        self.idNum = idNum
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
                  ra=data["ra"],
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
