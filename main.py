#!/usr/bin/env python3

from simple_webdriver import SimpleWebDriver
import re
import json
import logging
from typing import List, Dict
from argparse import ArgumentParser

log = logging.getLogger('blbl-user-video-crawler')
log.setLevel(logging.INFO)

class BilibiliUserVideoCrawler(): 

    klee: SimpleWebDriver

    def __init__(self, headless=True): 
        if not self.ensure_login(): 
            log.info('Can\'t login. Exiting...')
            exit(1)
        self.klee = SimpleWebDriver(user_data_dir='data/user_data', headless=headless)

    def ensure_login(self, retry=-1) -> bool: 

        def check_login() -> bool: 
            with SimpleWebDriver(user_data_dir='data/user_data', headless=True) as ambor: 
                url = 'https://space.bilibili.com/'
                ambor.get(url)
                return ambor.current_url.startswith(url)
        
        def retrying(): 
            if retry == -1: 
                while True: yield 0
            else: 
                yield from range(retry + 1)
        
        for _ in retrying(): 
            if check_login(): 
                log.info('Logged in.')
                return True
            log.info('Loggin failed. Trying to login with UI. Press [Enter] if you are ready.')
            input()
            with SimpleWebDriver(user_data_dir='data/user_data', headless=False) as ambor: 
                ambor.get('https://space.bilibili.com/')
                log.info('Press [Enter] if you finish logging in.')
                input()

        return False
        

    def crawl(self, mid: str, page_limit:int=-1) -> List[Dict]: 
        klee = self.klee
        pattern = re.compile('https://api.bilibili.com/x/space/wbi/arc/search.*')

        def pages(first_page: str): 
            klee.get(first_page)
            total_page = int(klee['//span[@class="be-pager-total"]'].text[1:-2].strip())
            log.info(f'fetching page 1/{total_page}...')
            yield
            rng = range(min(total_page + 1, page_limit) - 1) \
                    if page_limit != -1 \
                    else range(total_page - 1)
            for i in rng:
                i += 2
                log.info(f'fetching page {i}/{total_page}...')
                klee['//li[@title="下一页"]'].click()
                yield

        def perpage(): 
            rsep = None
            for url, _, resp in klee.packets(): 
                if re.match(pattern, url): 
                    break

            if resp is None: return []
            return json.loads(resp['body'])['data']['list']['vlist']
        
        res = [
            it 
            for _ in pages(f'https://space.bilibili.com/{mid}/video')
            for it in perpage()
        ]
        return res


def main(): 
    parser = ArgumentParser()
    parser.add_argument('mid', type=str)
    args = parser.parse_args()

    klee = BilibiliUserVideoCrawler()
    ret = klee.crawl(args.mid)
    ret = [it['bvid'] for it in ret]

    for it in ret: 
        print(it)


if __name__ == '__main__': 
    main()
