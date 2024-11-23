import json
import random
import datetime
import math
import itertools

with open("../data/index_to_lines.json", "r", encoding="utf-8") as infile:
    index_to_lines = json.load(infile)

with open("../data/lines_to_index.json", "r", encoding="utf-8") as infile:
    lines_to_index = json.load(infile)

with open("../data/index_to_name.json", "r", encoding="utf-8") as infile:
    index_to_name = json.load(infile)

with open("../data/detail_gua_info_eng.json", "r", encoding="utf-8") as infile:
    detail_gua_info = json.load(infile)

TIAN_GAN = "jia,yi,bing,ding,wu,ji,geng,xin,ren,gui".split(",")
DI_ZHI = "zi,chou,yin,mao,chen,si,wu,wei,shen,you,xu,hai".split(",")


def retrieve_information(original_index, alter_index, alter_list):
    original_info = detail_gua_info[str(original_index)]
    alter_info = detail_gua_info[str(alter_index)]
    ignore_field = set(["description", "philosophy", "scholar_interpretation"])
    res = {}
    res["original"] = {}
    res["alter"] = {}
    for line_key in original_info:
        res["original"][line_key] = {}
        for field_key in original_info[line_key]:
            if field_key not in ignore_field:
                res["original"][line_key][field_key] = original_info[line_key][
                    field_key
                ]

    alter_line_keys = [f"line_{i}" for i in alter_list]
    for line_key in alter_line_keys:
        res["alter"][line_key] = {}
        for field_key in alter_info[line_key]:
            if field_key not in ignore_field:
                res["alter"][line_key][field_key] = alter_info[line_key][field_key]

    return res


def get_altered_hexagram(hexagram_index, alter_list):
    # Load index_to_lines.json and lines_to_index.json

    # Get the original string representation of the hexagram
    original_lines = index_to_lines[str(hexagram_index)]

    # Convert the original string to a list to modify it
    altered_lines = list(original_lines)

    # Apply the alterations based on the alter_list
    for pos in alter_list:
        # Adjust for 1-based index by subtracting 1
        index = pos - 1
        # Flip 'P' to 'N' or 'N' to 'P'
        altered_lines[index] = "P" if altered_lines[index] == "N" else "N"

    # Join the altered lines back into a string
    altered_lines_string = "".join(altered_lines)

    # Get the altered hexagram index from lines_to_index.json
    altered_hexagram_index = lines_to_index[altered_lines_string]

    altered_hexagram_name = index_to_name[altered_hexagram_index]

    return altered_lines_string, altered_hexagram_index, altered_hexagram_name


# in ancient IChing, it has its own system to record time
# called TIAN GAN and DI ZHI: Celesitial Stems and earthly branches
# we need to transfer a standard UTC into this format
# later we will use this time format to get details of the given hexagram
def getJieqi(year, x=3):
    if x not in range(1, 25):
        return None
    try:
        year = int(year)
        x = int(x)
    except:
        return None
    if year < 1900:
        return None
    x -= 1
    startDT = datetime.datetime(1899, 12, 31)
    # 相差的天数
    days = 365.242 * (year - 1900) + 6.2 + 15.22 * x - 1.9 * math.sin(0.262 * x)
    delta = datetime.timedelta(days=days)
    return startDT + delta


def getYearGanzhi(dt, num=False):
    if not isinstance(dt, datetime.datetime):
        return ""
    if dt.year < 1900:
        return ""

    y = dt.year

    ganNum = (y - 4) % 10
    zhiNum = (y - 4) % 12

    if num:
        return (ganNum + 1, zhiNum + 1)

    return (TIAN_GAN[ganNum], DI_ZHI[zhiNum])


def getJieqiList_byYear(year, jie_only=False, qi_only=False, addNum=False):
    try:
        year = int(year)
    except:
        return []
    res = []
    if jie_only and qi_only:  # 两者相排斥
        raise KeyError
    if jie_only:
        for i in range(1, 25, 2):
            if addNum:
                res.append((getJieqi(year, x=i), i))
            else:
                res.append(getJieqi(year, x=i))
    elif qi_only:
        for i in range(2, 25, 2):
            if addNum:
                res.append((getJieqi(year, x=i), i))
            else:
                res.append(getJieqi(year, x=i))
    else:
        for i in range(1, 25):
            if addNum:
                res.append((getJieqi(year, x=i), i))
            else:
                res.append(getJieqi(year, x=i))
    return res


def getMonthGanzhi(dt):
    if not isinstance(dt, datetime.datetime):
        return ""
    if dt.year < 1900:
        return ""
    jieqiDtList = getJieqiList_byYear(dt.year, jie_only=True)
    startzhi = 1
    zhiNum = 0
    for jieqiDT, index in zip(jieqiDtList, range(12)):
        if dt >= jieqiDT:
            zhiNum = startzhi + index
    ganList = {
        2: 1,
        3: 2,
        4: 3,
        5: 4,
        6: 5,
        7: 6,
        8: 7,
        9: 8,
        10: 9,
        11: 10,
        0: 11,
        1: 12,
    }
    yg = getYearGanzhi(dt, num=True)[0]
    ganNum = (yg * 2 + ganList[zhiNum]) % 10
    if ganNum == 0:
        ganNum = 10
    ganNum -= 1

    return (TIAN_GAN[ganNum], DI_ZHI[zhiNum])


def getDayGanzhi(dt, num=False):
    if not isinstance(dt, datetime.date):
        return ""
    startdate = datetime.datetime(1901, 1, 1)
    startganzhi = 16
    delta = dt - startdate
    if delta.days + delta.seconds < 0:
        return ""
    res = (startganzhi + delta.days) % 60
    if res == 0:
        res = 60
    ganNum = (res - 1) % 10
    zhiNum = (res - 1) % 12
    if num:
        return (ganNum + 1, zhiNum + 1)
    return (TIAN_GAN[ganNum], DI_ZHI[zhiNum])


def getHourZhi(n, num=False):
    try:
        n = int(n)
        cnt = (n + 1) / 2
        if cnt == 12:
            cnt = 0
        if num:
            return cnt + 1

        return DI_ZHI[int(cnt)]
    except:
        return ""


def getHourGanzhi(dt, num=False):
    startDT = datetime.datetime(year=1901, month=1, day=1, hour=1)
    startGanzhi = 1
    if not isinstance(dt, datetime.datetime):
        return ""
    delta = dt - startDT
    if delta.seconds < 0:
        return ""
    hours = delta.days * 24 + delta.seconds / 3600
    ganNum = int(startGanzhi + hours / 2) % 10
    if num:
        return (ganNum + 1, getHourZhi(dt.hour, num=True))
    return (TIAN_GAN[ganNum], getHourZhi(dt.hour))


def get_process_time():
    # Get the current time
    current_time = datetime.datetime.now()

    # Extract the year, month, day, and hour
    year = current_time.year
    month = current_time.month
    day = current_time.day
    hour = current_time.hour

    dt = datetime.datetime(int(year), int(month), int(day), int(hour))

    time = {
        "utc": {
            "year": dt.year,
            "month": dt.month,
            "day": dt.day,
            "hour": dt.hour,
        },
        "iching": {
            "year": {"stem": getYearGanzhi(dt)[0], "brach": getYearGanzhi(dt)[1]},
            "month": {"stem": getMonthGanzhi(dt)[0], "brach": getMonthGanzhi(dt)[1]},
            "day": {"stem": getDayGanzhi(dt)[0], "brach": getDayGanzhi(dt)[1]},
            "hour": {"stem": getHourGanzhi(dt)[0], "brach": getHourGanzhi(dt)[1]},
        },
    }

    return time


# get the (five)element of the hexagram
# in ancient IChing, a hexagram would be categorized into a general element
# from: gold, wood, water, fire, soil
# given hexagram index, return an element
def get_hexagram_element(hexagram_index):
    assert hexagram_index >= 1 and hexagram_index <= 64
    hexagram_index = str(hexagram_index)
    with open("../data/index_to_element.json", "r", encoding="utf-8") as infile:
        index_to_element = json.load(infile)
    return index_to_element[hexagram_index]


# get the (five)element of each line of the hexagram
# in ancient IChing, six lines in the hexagram can be further categorized into
# different elements
# given hexagram index, return a list of elements represent all six lines
# http://www.360doc.com/content/24/0413/09/80823585_1120246594.shtml
def get_lines_elements(hexagram_index):
    # get the lines representation in "NP" string format
    assert hexagram_index >= 1 and hexagram_index <= 64
    hexagram_index = str(hexagram_index)
    with open("../data/lines_to_elements.json", "r", encoding="utf-8") as infile:
        lines_to_elements = json.load(infile)
    with open("../data/index_to_lines.json", "r", encoding="utf-8") as infile:
        index_to_lines = json.load(infile)
    lines = index_to_lines[hexagram_index]
    assert len(lines) == 6
    elements = []

    low_lines = lines[:3]
    # prepare the lower three elements
    elements.append(lines_to_elements[low_lines]["lower"]["0"])
    elements.append(lines_to_elements[low_lines]["lower"]["1"])
    elements.append(lines_to_elements[low_lines]["lower"]["2"])

    up_lines = lines[-3:]
    # prepare the upper three elements
    elements.append(lines_to_elements[up_lines]["upper"]["0"])
    elements.append(lines_to_elements[up_lines]["upper"]["1"])
    elements.append(lines_to_elements[up_lines]["upper"]["2"])

    assert len(elements) == 6
    return elements


# in ancient IChing, the "six spirits" are symbolic for each line of the hexagram
# it helps to provide deeper interpretation
def assign_spirits(day_zhi):
    SPIRITS_ORDER = [
        "Azure Dragon",
        "Vermilion Bird",
        "Hook Snake",
        "Flying Serpent",
        "White Tiger",
        "Black Tortoise",
    ]
    if day_zhi == "jia" or day_zhi == "yi":
        start_index = 0
    elif day_zhi == "bing" or day_zhi == "ding":
        start_index = 1
    elif day_zhi == "wu":
        start_index = 2
    elif day_zhi == "ji":
        start_index = 3
    elif day_zhi == "geng" or day_zhi == "xin":
        start_index = 4
    elif day_zhi == "ren" or day_zhi == "gui":
        start_index = 5

    return list(
        itertools.islice(itertools.cycle(SPIRITS_ORDER), start_index, start_index + 6)
    )


# in ancient IChing, the "six relations" are symbolic for each line of the hexagram
# it helps to provide deeper interpretation
def get_relations(hexagram_element, line_elements):
    # extract single element
    line_elements = line_elements.split()[-1]
    if line_elements == hexagram_element:
        # same elements indicates siblings
        return "Sibling"
    elif (
        line_elements
        == {
            "wood": "water",
            "fire": "wood",
            "soil": "fire",
            "gold": "soil",
            "water": "gold",
        }[hexagram_element]
    ):
        # elements generation indicates parents
        return "Parents"
    elif (
        line_elements
        == {
            "wood": "fire",
            "fire": "soil",
            "soil": "gold",
            "gold": "water",
            "water": "wood",
        }[hexagram_element]
    ):
        # inverse generation indicates Children
        return "Children"
    elif (
        line_elements
        == {
            "wood": "gold",
            "fire": "water",
            "soil": "wood",
            "gold": "fire",
            "water": "soil",
        }[hexagram_element]
    ):
        # harmness indicates Demons
        return "Demons"
    elif (
        line_elements
        == {
            "wood": "soil",
            "fire": "gold",
            "soil": "water",
            "gold": "wood",
            "water": "fire",
        }[hexagram_element]
    ):
        # inverse harmness indicates Wife and Wealth
        return "Wife and Wealth"
    return "None"


# get lines details which includes:
# five elements of each line
# spirits of each line
# relations of each line
def get_lines_details(hexagram_index, day_gan, first_index=None):
    if first_index == None:
        hexagram_element = get_hexagram_element(hexagram_index)
    else:
        # this is the second hexagram
        # should use the first hexagram index to get general element
        hexagram_element = get_hexagram_element(first_index)

    elements_sequence = get_lines_elements(hexagram_index)

    # calclate the sprits order
    spirits_sequence = assign_spirits(day_gan)

    assert len(elements_sequence) == 6 and len(spirits_sequence) == 6

    # get relations
    line_details = []
    for i, ele in enumerate(elements_sequence):
        relation = get_relations(hexagram_element, ele)
        spirit = spirits_sequence[i]
        line_details.append(
            {
                "line": f"{i+1}",
                "elements": ele,
                "relations": relation,
                "spirits": spirit,
            }
        )

    return line_details


def process():
    # get the time that user starts the hexagram generation process
    time_dict = get_process_time()
    # get the first hexagram
    first_hexagram_index = random.randint(1, 64)
    with open("../data/index_to_name.json", "r", encoding="utf-8") as infile:
        index_to_name = json.load(infile)
    first_hexagram_name = index_to_name[str(first_hexagram_index)]
    first_details = get_lines_details(
        first_hexagram_index, time_dict["iching"]["day"]["stem"]
    )

    # get the lines to altered in a list
    # Randomly determine the number of elements in the list (0 to 6)
    num_elements = random.randint(0, 6)

    # Generate a list of unique random integers between 1 and 6
    alter_list = random.sample(
        range(1, 7), num_elements
    )  # range(1, 7) generates numbers 1 through 6

    # get the second hexagram
    altered_string, second_hexagram_index, second_hexagram_name = get_altered_hexagram(
        first_hexagram_index, alter_list
    )

    if len(alter_list) != 0:
        second_details = get_lines_details(
            int(second_hexagram_index),
            time_dict["iching"]["day"]["stem"],
            first_hexagram_index,
        )
    else:
        second_details = None

    return (
        time_dict,
        str(first_hexagram_index),
        first_hexagram_name,
        first_details,
        alter_list,
        str(second_hexagram_index),
        second_hexagram_name,
        second_details,
    )
