### What is it?
This project is used for collecting historical posts from a given wechat public account. The original idea is borrowed from [fst034356](https://github.com/fst034356/crawler/tree/master/wechat). However in this repo, another rest point `getmsg` is found and used to get posts by json. It could be faster than the original script, which is using PhantomJS to scroll and fetch more posts.

### Dependencies
- selenium
- [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads)

### how to get the history from a wechat public account
1. install fiddler and wechat for windows/mac
2. Open the public account in wechat app on windows/mac, and also fiddler
3. In wechat app, open the account history
4. In fiddler, find the request with host as `mp.weixin.qq.com`, and url starts with `/mp/profile_ext?action=home`.
4. In the request url, copy `__biz`, `uin`, `key`, `pass_ticket` into json file. You can save it by wechat name for easy organization
5. Run the script `python wechat_history.py {json file path}`

Note: `uin` and `pass_ticket` can be reused on one machine. `__biz` stands for each unique account, so it will be different for different wechat account. `key` is updated every 2 hours or so, it is recommended to get a new key when rerunning the script after a long time.

### TODOs
1. Save message list
2. update message list by time
