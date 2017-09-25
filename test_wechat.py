import pytest
from wechat_history import json_loads_recursive, get_account_info
from wechat_history import construct_home_url, construct_message_url


class TestWechatHistory(object):

    @classmethod
    def setup_class(cls):
        cls.account_info = get_account_info(r'./test_data/cespn.json')

    def test_json_loads_recursive(self):
        json_str_path = r'./test_data/test_json_string.txt'
        with open(json_str_path, 'r', encoding='utf-8') as infile:
            s = infile.read().replace('\ufeff', '')
            d = json_loads_recursive(s)
            assert d['general_msg_list']['list'][0]['comm_msg_info']['id'] == 1000000168

    def test_construct_home_url(self):
        home_url = construct_home_url(self.account_info)
        assert home_url == 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA5NDQ2OTcwMA==&uin=ODY5MzgzODYx&key=b2baee5628b77e3da8189a732c27fd12d54a73138b8429aaf4e0fee2525495e40f5bfe70ea51d44d92904fba6ec511f1ce803828704022fc9952183a8d02dd55e430ad1105217e2f1a35daed5deddced&pass_ticket=7KhgUrkHBffZrR2o7IGyewYIeD%2BcksGv%2FnjgvABhysjA2SImJa3yttNaFx0zjWuB&scene=124&devicetype=Windows+10&version=6204014f&lang=en&a8scene=7&winzoom=1'

    def test_construct_message_url(self):
        msg_url = construct_message_url(self.account_info, new=True)
        assert msg_url == 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA5NDQ2OTcwMA==&offset=0&f=json'

        msg_url2 = construct_message_url(self.account_info, next_offset=300)
        assert msg_url2 == 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=MzA5NDQ2OTcwMA==&offset=300&f=json'


if __name__ == '__main__':
	pytest.main()