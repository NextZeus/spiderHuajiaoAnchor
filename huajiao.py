from bs4 import BeautifulSoup
from bs4 import NavigableString
import requests
import re
import datetime
from mongo import UserModel

def get_soup_by_url(url):
    html = requests.get(url)
    plain_text = html.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    return soup

# 获取花椒直播所有分类id
def get_huajiao_video_categories():
    huajiao_main_url = "http://www.huajiao.com/"
    soup = get_soup_by_url(huajiao_main_url)
    hd_nav = soup.find_all('a', {'href': re.compile('category/')})

    categories = dict()
    for tag in hd_nav:
        des = tag.string
        if des == '更多>':
            continue
        category = tag.get('href')[10:]
        categories[category] = des
    return categories

# 根据 分类id 和 页码 获取对应请求的url
def get_category_url_by_id_and_pageno(catgory_id, pageno):
    catgory_url = "http://www.huajiao.com/category/" + str(catgory_id) + "pageno=" + str(pageno)
    return catgory_url

# 根据直播ID 获取主播用户ID
def get_anchorid_by_liveid(liveid):
    url = "http://www.huajiao.com/l/" + str(liveid)
    soup = get_soup_by_url(url)
    anchor_id = soup.find_all('a', href=re.compile('user/'))[0].get('href')[6:]
    return anchor_id

# 获取主播详细信息 & 直播历史纪录
def get_anchor_info_by_userid(userid):
    person = dict()

    person['userid'] = userid

    url = "http://www.huajiao.com/user/" + str(userid)
    soup = get_soup_by_url(url)

    # userinfo div
    userInfo = soup.find('div', {'id': 'userInfo'})

    if userInfo is not None:
        username = userInfo.find_all('h3')[0].get_text(strip=True)
        person['username'] = username
        # 头像
        avatar = userInfo.find('img').get('src')
        person['avatar'] = avatar

        # 简介
        about = userInfo.find('p', 'about')
        person['about'] = about.get_text(strip=True)

        # 等级
        level = userInfo.find('span', 'level')
        person['level'] = level.get_text(strip=True)

        # other
        clearfix = userInfo.find('ul', 'clearfix')
        for child in clearfix.children:
            if not isinstance(child, NavigableString):
                p = child.find('p').get_text(strip=True)
                h = child.find('h4').get_text(strip=True)
                if h == '关注':
                    person['follow'] = p
                elif h == '粉丝':
                    person['fans'] = p
                elif h == '赞':
                    person['support'] = p
                elif h == '经验值':
                    person['exp'] = p
    else:
        print('userInfo has no find_all method userid:', userid, userInfo)

    print('person: ', person)
    return person

# 获取直播分类列表数据
def get_category_list(catgory_id):
    catgory_url = "http://www.huajiao.com/category/" + str(catgory_id)
    soup = get_soup_by_url(catgory_url)
    # 获取最大分页数
    page_tag = soup.find_all('li', "paginate_button last")
    if len(page_tag) <= 0:
        return []

    last_page_tag = soup.find_all('li', "paginate_button last")[0]
    last_page = int(last_page_tag.get('tabindex'))

    data = list()

    for pageno in range(1, last_page):
        catgory_url = get_category_url_by_id_and_pageno(catgory_id, pageno)
        soup = get_soup_by_url(catgory_url)
        main_list = soup.find_all('a', href=re.compile('/l/'))

        for link in main_list:
            liveId = link.get('href')[3:]
            userid = get_anchorid_by_liveid(liveId)
            if userid != 'uid':
                person = get_anchor_info_by_userid(userid)
                data.append(person)

    return data


def get_all_anchor_data():
    categories = get_huajiao_video_categories()
    print('花椒主播分类: ', categories)
    for category in categories.keys():
        data = get_category_list(category)
        UserModel().bulk_inserts(data)
        print('category ' + str(category)+' anchor-number: ', len(data))


def get_mingxingricheng_data():
    url = "http://www.huajiao.com/recommend/mingxingricheng"
    soup = get_soup_by_url(url)
    video_list = soup.find('ul', 'videolist_lms')

    data = list()

    year = datetime.datetime.now().year
    print('花椒直播 明星行程')

    for child in video_list:
        if not isinstance(child, NavigableString):
            xingcheng = dict()

            image = child.find('img').get('src')
            xingcheng['image'] = image

            date = str(year) + '-' + child.find('span', 'time_pdvims').get_text(" ", strip=True)
            xingcheng['date'] = date

            num_sidvlms = child.find('span', 'num_sidvlms').get_text(" ", strip=True)
            xingcheng['watched'] = num_sidvlms

            tit_idvlms = child.find('p', 'tit_idvlms').a
            user_url = tit_idvlms.get('href')
            user_name = tit_idvlms.get_text(strip=True)

            xingcheng['url'] = user_url
            xingcheng['user_name'] = user_name

            name_idvlms = child.find('p', 'name_idvlms')
            title = name_idvlms.b.get_text() + name_idvlms.a.get_text()
            xingcheng['title'] = title
            data.append(xingcheng)
            print('行程: ', xingcheng)
            return data

# get_mingxingricheng_data()
get_all_anchor_data()

