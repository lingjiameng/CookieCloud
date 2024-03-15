## 基于Python的CookieCloud服务器端

参考原始项目, 基于FastApi开发

## 使用方法

Windows双击运行打包出的exe程序即可启动

默认CookieCloud服务器地址 `http://localhost:10375/cookiecloud/`
或者将localhost替换为运行机器的ip地址

可配置项, 通过系统环境变量配置
- `COOKIE_CLOUD_PORT`: 指定服务器端口，默认为10375 (若程序启动后异常退出，可尝试修改端口)

## 开发环境

- `windows 10`
- `python 3.11.8`
- `requirements.txt`

```
pip install -r requirements.txt

python main.py
```

## 参考项目地址

- [easychen/CookieCloud](https://github.com/easychen/CookieCloud)
- [lupohan44/PyCookieCloud](https://github.com/lupohan44/PyCookieCloud)
