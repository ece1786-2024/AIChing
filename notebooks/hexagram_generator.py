import json
import random
import datetime
import math
import itertools

from mdutils.mdutils import MdUtils

with open("../data/gua_attrs.json", "r", encoding="utf-8") as infile:
    gua_attrs = json.load(infile)

with open("../data/detail_gua_info_eng.json", "r", encoding="utf-8") as infile:
    detail_gua_info = json.load(infile)

with open("../data/lines_to_elements.json", "r", encoding="utf-8") as infile:
    lines_to_elements = json.load(infile)

with open("../data/lines_to_index.json", "r", encoding="utf-8") as infile:
    lines_to_index = json.load(infile)

TIAN_GAN = "jia,yi,bing,ding,wu,ji,geng,xin,ren,gui".split(",")
DI_ZHI = "zi,chou,yin,mao,chen,si,wu,wei,shen,you,xu,hai".split(",")


def retrieve_information(
    primary_index, alter_index, alter_list, primary_line_details, alter_line_details
):
    primary_info = detail_gua_info[str(primary_index)]
    alter_info = detail_gua_info[str(alter_index)]
    ignore_field = set(
        ["description", "philosophy", "book_DuanYi", "interpretation_scholar"]
    )
    target_lines = [f"line_{i}" for i in range(1, 7)]

    res = {}
    res["primary"] = {}
    res["alter"] = {}
    for line_key in target_lines + ["general"]:
        res["primary"][line_key] = {}
        for field_key in primary_info[line_key]:
            if field_key not in ignore_field:
                res["primary"][line_key][field_key] = primary_info[line_key][
                    field_key
                ].replace("\n", "\t\t\n")
        if line_key == "general":
            res["primary"]["general"]["name"] = gua_attrs[str(primary_index)]["name"]
            continue
        for attr_key in primary_line_details[line_key]:
            res["primary"][line_key][attr_key] = primary_line_details[line_key][
                attr_key
            ]

    alter_line_keys = [f"line_{i}" for i in alter_list]
    for line_key in alter_line_keys:
        res["alter"][line_key] = {}
        for field_key in alter_info[line_key]:
            if field_key not in ignore_field:
                res["alter"][line_key][field_key] = alter_info[line_key][
                    field_key
                ].replace("\n", "\t\t\n")
        for attr_key in alter_line_details[line_key]:
            res["alter"][line_key][attr_key] = alter_line_details[line_key][attr_key]

    return res


def format_gua_info(gua_info):
    mdFile = MdUtils(file_name="")
    mdFile.new_header(level=1, title="")
    mdFile.new_header(level=2, title="Hexagram Information")

    # Primary Hexagram Heading
    mdFile.new_header(
        level=2, title=f"Primary Hexagram: {gua_info['primary']['general']['name']}"
    )

    # General Information
    mdFile.new_header(level=3, title="General Information")
    mdFile.new_list(
        items=[
            f"Description: {gua_info['primary']['general']['interpretation']}",
            f"Traditional Interpretation: {gua_info['primary']['general']['traditional']}",
            f"Scholar Interpretation: {gua_info['primary']['general']['scholar_interpretation']}",
        ]
    )

    # Line Information
    mdFile.new_header(level=3, title="Line Information")
    line_list = [f"line_{i}" for i in range(1, 7)]
    for line_key in line_list:
        primary_line_info = gua_info["primary"][line_key]
        content_list = [
            f"Line {line_key[-1]}",
            [
                f"Description: {primary_line_info['interpretation']}",
                f"Element: {primary_line_info['elements']}, Relation: {primary_line_info['relations']}, ",
                f"Spirit: {primary_line_info['spirits']}",
            ],
        ]

        if primary_line_info["shi_ying"] != "None":
            content_list[-1].append(
                f"Shi/Ying Line: {primary_line_info['shi_ying']}",
            )
        if line_key in gua_info["alter"]:
            alter_line_info = gua_info["alter"][line_key]
            content_list[-1].append(
                "This line has changed. Line information after change:"
            )
            content_list.append(
                [
                    [
                        f"Description: {alter_line_info.get('interpretation', 'None')}",
                        f"Element: {alter_line_info['elements']}, Relation: {alter_line_info['relations']}",
                    ]
                ],
            )
        mdFile.new_list(content_list)

    return mdFile.get_md_text(), mdFile


def get_altered_hexagram(hexagram_index, alter_list):
    # Load index_to_lines.json and lines_to_index.json

    # Get the primary string representation of the hexagram
    primary_lines = gua_attrs[str(hexagram_index)]["binary"]

    # Convert the primary string to a list to modify it
    altered_lines = list(primary_lines)

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

    altered_hexagram_name = gua_attrs[altered_hexagram_index]["name"]

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
# from: Gold, Wood, Water, Fire, Soil
# given hexagram index, return an element
def get_hexagram_element(hexagram_index):
    assert (
        int(hexagram_index) >= 1 and int(hexagram_index) <= 64
    ), f"Hexagram index out of range, expected 1-64, got {hexagram_index}"
    hexagram_index = str(hexagram_index)
    return gua_attrs[hexagram_index]["element"]


# get the (five)element of each line of the hexagram
# in ancient IChing, six lines in the hexagram can be further categorized into
# different elements
# given hexagram index, return a list of elements represent all six lines
# http://www.360doc.com/content/24/0413/09/80823585_1120246594.shtml
def get_lines_elements(hexagram_index):
    # get the lines representation in "NP" string format
    assert int(hexagram_index) >= 1 and int(hexagram_index) <= 64
    hexagram_index = str(hexagram_index)
    lines = gua_attrs[hexagram_index]["binary"]
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
def get_spirits(day_zhi):
    SPIRITS_ORDER = [
        "Azure Dragon",
        "Vermilion Bird",
        "Hook Snake",
        "Flying Serpent",
        "White Tiger",
        "Black Tortoise",
    ]
    print(f"my day zhi is: {day_zhi}")
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
    # Extract the single element
    line_element = line_elements.split()[-1]

    # Define the relationship mappings
    generation = {
        "wood": "water",
        "fire": "wood",
        "soil": "fire",
        "gold": "soil",
        "water": "gold",
    }

    inverse_generation = {
        "wood": "fire",
        "fire": "soil",
        "soil": "gold",
        "gold": "water",
        "water": "wood",
    }

    harmness = {
        "wood": "gold",
        "fire": "water",
        "soil": "wood",
        "gold": "fire",
        "water": "soil",
    }

    inverse_harmness = {
        "wood": "soil",
        "fire": "gold",
        "soil": "water",
        "gold": "wood",
        "water": "fire",
    }

    # Determine the relationship
    if line_element == hexagram_element:
        return "Sibling"
    elif line_element == generation.get(hexagram_element):
        return "Parents"
    elif line_element == inverse_generation.get(hexagram_element):
        return "Children"
    elif line_element == harmness.get(hexagram_element):
        return "Demons"
    elif line_element == inverse_harmness.get(hexagram_element):
        return "Wife and Wealth"
    else:
        return "None"


def generate_shi_ying(hexagram_index):
    bin_repr = gua_attrs[str(hexagram_index)]["binary"]
    if bin_repr[:3] == bin_repr[3:]:
        shi_yao = 6
    else:
        # 分析内外卦的爻位阴阳关系
        di_yao_same = bin_repr[-1] == bin_repr[-4]
        ren_yao_same = bin_repr[-2] == bin_repr[-5]
        tian_yao_same = bin_repr[-3] == bin_repr[-6]

        if tian_yao_same and not ren_yao_same and not di_yao_same:
            shi_yao = 2
        elif ren_yao_same and not tian_yao_same and not di_yao_same:
            shi_yao = 4
        elif di_yao_same and not tian_yao_same and not ren_yao_same:
            shi_yao = 4
        elif tian_yao_same and ren_yao_same and not di_yao_same:
            shi_yao = 1
        elif tian_yao_same and di_yao_same and not ren_yao_same:
            shi_yao = 3
        elif di_yao_same and ren_yao_same and not tian_yao_same:
            shi_yao = 5
        else:
            shi_yao = 3

    # 确定应爻位置
    ying_yao = (shi_yao + 3) % 6
    if ying_yao == 0:
        ying_yao = 6

    return {"shi": shi_yao, "ying": ying_yao}


def get_shi_ying(hexagram_index):
    info = gua_attrs[str(hexagram_index)]
    return info["shi"], info["ying"]


# get lines details which includes:
# five elements of each line
# spirits of each line
# relations of each line
def get_lines_details(hexagram_index, day_gan, first_index=None):
    if first_index is None:
        hexagram_element = get_hexagram_element(hexagram_index)
    else:
        # this is the second hexagram
        # should use the first hexagram index to get general element
        hexagram_element = get_hexagram_element(first_index)

    elements_sequence = get_lines_elements(hexagram_index)
    shi_pos, ying_pos = get_shi_ying(hexagram_index)

    # calclate the sprits order
    spirits_sequence = get_spirits(day_gan)

    assert len(elements_sequence) == 6 and len(spirits_sequence) == 6

    # get relations
    line_details = {}
    for i, ele in enumerate(elements_sequence):
        relation = get_relations(hexagram_element, ele)
        spirit = spirits_sequence[i]
        shi_or_ying = (
            "Shi" if i + 1 == shi_pos else "Ying" if i + 1 == ying_pos else "None"
        )
        line_details[f"line_{i+1}"] = {
            "elements": ele,
            "relations": relation,
            "spirits": spirit,
            "shi_ying": shi_or_ying,
        }

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


def manual_process(first_index, ri_gan, manual_list=[]):
    # get the time that user starts the hexagram generation process
    time_dict = get_process_time()

    # Manually change RI GAN
    time_dict["iching"]["day"]["stem"] = ri_gan

    # Manual first hexagram
    first_hexagram_index = first_index
    with open("../data/index_to_name.json", "r", encoding="utf-8") as infile:
        index_to_name = json.load(infile)
    first_hexagram_name = index_to_name[str(first_hexagram_index)]
    first_details = get_lines_details(
        first_hexagram_index, time_dict["iching"]["day"]["stem"]
    )

    # Manual get the lines to altered in a list

    alter_list = manual_list

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


if __name__ == "__main__":
    (
        time_dict,
        first_hexagram_index,
        first_hexagram_name,
        first_details,
        alter_list,
        second_hexagram_index,
        second_hexagram_name,
        second_details,
    ) = process()

    raw_gua_info = retrieve_information(
        first_hexagram_index,
        second_hexagram_index,
        alter_list,
        first_details,
        second_details,
    )
    formatted_gua_info, _ = format_gua_info(raw_gua_info)
    print(formatted_gua_info)
