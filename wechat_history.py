"""
actions in this script:
1. read the json file to get parameter info
2. use webdrive to open the account history home page, the session and
   cookies are then saved.
3. open the account posts by making requests to getmsg
4. loop over the getmsg page until no more message to load
"""
import json
from selenium import webdriver
import os
from datetime import datetime


_CHROME = webdriver.Chrome(r'c:\temp\chromedriver.exe')
_ROOT = 'https://mp.weixin.qq.com/mp/profile_ext?'


def get_account_info(info_json):
    with open(info_json, 'r', encoding='utf-8') as infile:
        d = json.load(infile)

        # make sure all the keys are there and not empty
        assert d['__biz'] not in (None, '')
        assert d['uin'] not in (None, '')
        assert d['key'] not in (None, '')
        assert d['pass_ticket'] not in (None, '')

        return d


def read_page_content(url):
    """ read url body content """
    _CHROME.get(url)
    return _CHROME.find_element_by_xpath('.//body').text


def json_loads_recursive(json_str):
    # if input str is actual a numeric, just return
    if not isinstance(json_str, str):
        return json_str

    # try to load the string
    try:
        d = json.loads(json_str, encoding='utf-8')
    # if the load failed, the the input is not a dict, return it.
    except json.decoder.JSONDecodeError:
        return json_str
    # if successfully loaded, try to load all the values recursively
    else:
        for k, v in d.items():
            d[k] = json_loads_recursive(v)

    return d


def construct_home_url(account_info):
    __biz = '__biz={}'.format(account_info['__biz'])
    uin = 'uin={}'.format(account_info['uin'])
    key = 'key={}'.format(account_info['key'])
    pass_ticket = 'pass_ticket={}'.format(account_info['pass_ticket'])

    params = ['action=home', __biz, uin, key, pass_ticket, 'scene=124',
              'devicetype=Windows+10', 'version=6204014f', 'lang=en',
              'a8scene=7', 'winzoom=1']

    return _ROOT + '&'.join(params)


def construct_message_url(account_info, new=False, next_offset=0):
    """ once home is loaded, only __biz is needed for getmsg """
    __biz = '__biz={}'.format(account_info['__biz'])
    offset = 0 if new else next_offset

    params = ['action=getmsg', __biz, 'offset={}'.format(offset), 'f=json']

    return _ROOT + '&'.join(params)


class Chunk(object):
    """
    Class for each message chunk when making requests to getmsg.

    Attributes:
    - return_code: return code
    - error_message: error message
    - message_count: seems it will always be 10, even when requesting more than 10
    - can_msg_continue: 1 or 0, if 0, no more message to load
    - message_list: list of messages
    - next_offset: offset number of next chunk
    """
    def __init__(self, url):
        self.contents = json_loads_recursive(read_page_content(url))

    @property
    def return_code(self):
        return self.contents.get('ret')

    @property
    def errmsg(self):
        return self.contents.get('errmsg')

    @property
    def message_count(self):
        return self.contents.get('msg_count')

    @property
    def can_msg_continue(self):
        return self.contents.get('can_msg_continue')

    @property
    def message_list(self):
        return self.contents.get('general_msg_list').get('list')

    @property
    def next_offset(self):
        return self.contents.get('next_offset')



def get_all_messages(account_info):
    starting_msg_url = construct_message_url(account_info, new=True)
    chunk = Chunk(starting_msg_url)
    messages = []

    while chunk.errmsg == 'ok':
        # result is good, save the message list
        messages.extend(chunk.message_list)

        # loading more
        if chunk.can_msg_continue:
            offset = chunk.next_offset
            next_url = construct_message_url(account_info, next_offset=offset)
            chunk = Chunk(next_url)
        # nothing to load anymore, return the message
        else:
            return messages


def save_messages_to_csv(messages, account_json_path):
    """ save messages into csv """
    path, name = os.path.split(os.path.abspath(account_json_path))
    output_csv = os.path.join(path, '{}.csv'.format(name.split('.')[0]))

    with open(output_csv, 'w', encoding='utf-8') as outfile:
        outfile.write('publish time, title, url\n')

        for msg in messages:
            # get message posting time
            try:
                pub_timestamp = msg.get('comm_msg_info').get('datetime')
                pub_dt = str(datetime.utcfromtimestamp(pub_timestamp))

                title = msg.get('app_msg_ext_info').get('title')
                url = msg.get('app_msg_ext_info').get('content_url')

                outfile.write('{}, {}, {}\n'.format(pub_dt, title, url))
            except (KeyError, AttributeError) as e:
                pass


def main(account_json):
    account_info = get_account_info(account_json)
    home_url = construct_home_url(account_info)
    _CHROME.get(home_url)
    messages = get_all_messages(account_info)
    print('{} messages collected'.format(len(messages)))
    print('This is the most recent one:')
    print(messages[0])

    save_messages_to_csv(messages, account_json)


if __name__ == '__main__':
    import sys
    account_info = sys.argv[1]
    main(account_info)
