from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
import time
import json
from typing import Tuple, Generator, Any

class SimpleWebDriver(webdriver.Chrome): 

    def __init__(
            self, 
            headless=False, 
            user_data_dir=None,
            options: Options=None
    ): 
        options = options or Options()
        caps = {
            "browserName": "chrome",
            'goog:loggingPrefs': {'performance': 'ALL'}
        }
        for key, value in caps.items():
            options.set_capability(key, value)

        if headless: 
            # :: ATTENTION :: 
            # Somtimes this don't work. 
            # You should check either '--headless=new' or '--headless' work, 
            # and modify this by yourself. 
            options.add_argument('--headless=new')
        if user_data_dir: 
            options.add_argument(f'--user-data-dir={user_data_dir}')
        super().__init__(options=options)
        self.implicitly_wait(10)

    def packets(
            self, 
            *, 
            timeout=10,
            json_only=True,
    ) -> Generator[Tuple[str, str, Any], None, None]: 
        sp = time.time()
        while True: 
            logs = self.get_log('performance')
            for packet in logs:
                try: 
                    data = json.loads(packet['message'])['message']
                    if data['method'] != 'Network.responseReceived': 
                        continue

                    req_id = data['params']['requestId']
                    response = self.execute_cdp_cmd('Network.getResponseBody', {'requestId': req_id})

                    data = data['params']['response']
                    url, typ = data['url'], data['mimeType']

                    if json_only and typ == 'application/json': 
                        yield url, typ, response
                except WebDriverException: pass

            if time.time() - sp > timeout: 
                break
            time.sleep(0.1)


    def __getitem__(self, key) -> WebElement:
        return WebElementPlus(self.find_element(By.XPATH, key))
    
    def __lshift__(self, key) -> WebElement:
        return [WebElementPlus(it) for it in self.find_elements(By.XPATH, key)]


    

class WebElementPlus(WebElement):
    
    def __init__(self, elem):
        self.proxied = elem

    def __getattr__(self, key):
        return self.proxied.__getattribute__(key)

    def __getitem__(self, key) -> WebElement:
            return WebElementPlus(self.proxied.find_element(By.XPATH, key))
        
    def __lshift__(self, key) -> WebElement:
        return [WebElementPlus(it) for it in self.find_elements(By.XPATH, key)]


