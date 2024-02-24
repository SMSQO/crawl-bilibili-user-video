## crawl-bilibili-user-video

这个仓库用于爬取一个bilibili用户的所有视频的BVID. 有了BVID, 就可以用其他方法下载视频了. 

#### 指标 : 
- 技术难度: 3/10
- 实用性:   4/10
- 易用性:   3/10
- 可靠性:   3/10
- 编写平台: Ubuntu 22.04


#### usage: 
```
    python3 main.py [mid] 
    (mid为用户id, 可以通过在网页端访问目标用户的个人空间时, 在网址中获取)
```

#### 运行环境需求
1. 在计算机上配置好 webdriver (time consuming); 
2. `pip install selenium`.

#### 脚本原理: 
1. 控制浏览器访问目标用户的个人空间的视频界面; 
2. 从浏览器的logging中查找"获取视频"的API; 
3. 翻页(每页只产出30个视频), 直到获取所有的视频信息. 

#### 其他: 
1. 第一次使用时需要登录;
2. 创建 BilibiliUserVideoCrawler() 时将headless设置为False, 则可以用有界面的方式查看爬取过程; 
3. 由于是操作浏览器从网页爬取, 所以脚本未必可靠: 将来如果B站界面/接口修改, 则可能需要重修脚本;
4. 用浏览器爬取并非最佳实践. 
