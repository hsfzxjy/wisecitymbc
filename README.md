# wisecitymbc
Website for wisecity.

## 配置

本地调试需要安装：

 + python 2.7 +, 3.0 -
 + MySQL
 + nodejs
 + memcached
 + node-less
 + pip (python 包管理器)
 + npm (nodejs 包管理器)

node库依赖：

 + grunt
 + grunt-cli

python库依赖:

 + django == 1.7.1
 + gevent
 + MySQL-python
 + djangorestframework
 + qiniu
 + pylibmc
 + python-memcached
 + sae-python-dev (如果使用新浪云)

grunt 配置（安装 grunt 后）：

```sh
$ cd front-end/
$ sudo npm install --save-dev
```

网站详情配置： 修改 `site_config/settings.py`。

## 调试

本网站由 [django](https://www.djangoproject.com/) 开发，前端由 grunt 管理。

试运行网站：

```sh
$ chmod +x manage.py
$ ./manage.py runserver 8080 # 访问 localhost:8080
```

前端代码于 `front-end/` 下，修改前请先运行以下代码，以保证文件正确输出至 `static/` 目录下：

```sh
$ grunt watch
```

## 生产环境

 + 请将 `site_packages/` 置于环境变量中
 + `settings.py` 中的 `DEBUG` 调至 `False`
 + 若使用主机，切记**勿将 runserver 当做服务器！**，详情请见 [Deploying Django](https://docs.djangoproject.com/en/1.8/howto/deployment/)