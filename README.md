# 一步一步爬取花椒直播主播数据

## 第一步 安装所需库
* pip3 install bs4
* pip3 install requests

```
### 第二步 引入库

from bs4 import BeautifulSoup #解析HTML文件库
import requests #请求库
import re  #正则表达式库

```

### 第三步 定义通用bs4处理html文档内容方法
```
# 定义获取bs处理后的文档内容

def get_soup_by_url(url):
    html = requests.get(url)
    plain_text = html.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    return soup

```

### 第四步 定义获取直播分类的方法
```
# 获取花椒直播所有分类
def get_huajiao_video_categories():
    huajiao_main_url = "http://www.huajiao.com/"
    home_soup = get_soup_by_url(huajiao_main_url)
    #
    hd_nav = home_soup.find_all('a', {'href': re.compile('category')})
    print('hd_nav: ', hd_nav)
    categories = dict()
    for tag in hd_nav:
        des = tag.string #有两种 一种是 更多>; 另外一种是分类名
        if des == '更多>':
            continue
        print('des: ', des)
        print('name:', tag.string)
        category = tag.get('href')[10:]
        print('category: ', category)
        categories[category] = des
    print('categories:', categories)
    # 输出结果: categories: {'1000': '正在直播', '2': '女神驾到', '666': '才艺主播', '999': '校园女生', '1001': '音乐达人', '5': '娱乐明星', '1': '高清直播', '3': '高清直播'}

```

### 第五步 深入分类直播列表页面 
熬了个通宵，一晚上没睡着，撸到现在 哈哈 不过感觉撸的很爽 比平时写的要有效很多倍 可能是精力比较集中吧 接着写教程
顺便总结下bs4的一些实际经验
继续写代码

```
# 根据直播ID 获取主播用户ID
def get_anchorid_by_liveid(liveid):
    url = "http://www.huajiao.com/l/" + str(liveid)
    soup = get_soup_by_url(url)
    anchor_id = soup.find_all('a', href=re.compile('user/'))[0].get('href')[6:]
    return anchor_id

# 获取主播详细信息
def get_anchor_info_by_userid(userid):
    person = dict()
    person['userid'] = userid

    url = "http://www.huajiao.com/user/" + str(userid)
    soup = get_soup_by_url(url)

    # userinfo div
    userInfo = soup.find('div', {'id': 'userInfo'})

    username = userInfo.find('h3').get_text(strip=True)
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

    print('person: ', person)
    return person

# 根据 分类id 和 页码 获取对应请求的url
def get_category_url_by_id_and_pageno(catgory_id, pageno):
    catgory_url = "http://www.huajiao.com/category/" + str(catgory_id) + "pageno=" + str(pageno)
    return catgory_url

# 获取直播分类列表数据
def get_category_list(catgory_id):
    catgory_url = "http://www.huajiao.com/category/" + str(catgory_id)
    soup = get_soup_by_url(catgory_url)
    # 获取最大分页数
    page_tag = soup.find_all('li', "paginate_button last")
    if len(page_tag) <= 0:
        return []

    # 获取最大页码
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
            person = get_anchor_info_by_userid(userid)
            data.append(person)

    return data

```


