# Kcwiki-Luatable

[![Travis](https://img.shields.io/travis/kcwikizh/kcwiki-luatable.svg)](https://travis-ci.org/kcwikizh/kcwiki-luatable)
[![GitHub last commit (gh-pages)](https://img.shields.io/github/last-commit/kcwikizh/kcwiki-luatable/gh-pages.svg)](https://github.com/kcwikizh/kcwiki-luatable/tree/gh-pages)

kcwiki lua模块数据机器人🤖️

更新频率: 每日一次

||luatable|json|
|-|-|-|
|舰娘数据|[ships.lua](https://kcwikizh.github.io/kcwiki-luatable/luatable/ships.lua)|[ships.json](https://kcwikizh.github.io/kcwiki-luatable/json/ships.json)|
|装备数据|[items.lua](https://kcwikizh.github.io/kcwiki-luatable/luatable/items.lua)|[items.json](https://kcwikizh.github.io/kcwiki-luatable/json/items.json)|
|深海敌舰数据|[shinkai-ships.lua](https://kcwikizh.github.io/kcwiki-luatable/luatable/shinkai-ships.lua)|[shinkai-ships.json](https://kcwikizh.github.io/kcwiki-luatable/json/shinkai-ships.json)|
|深海装备数据|[shinkai-items.lua](https://kcwikizh.github.io/kcwiki-luatable/luatable/shinkai-items.lua)|[shinkai-items.json](https://kcwikizh.github.io/kcwiki-luatable/json/shinkai-items.json)|
|明石工厂数据|[akashi-list.lua](https://kcwikizh.github.io/kcwiki-luatable/luatable/akashi-list.lua)|[akashi-list.json](https://kcwikizh.github.io/kcwiki-luatable/json/akashi-list.json)|
|季节性语音数据|-|[seasonal](https://kcwikizh.github.io/kcwiki-luatable/seasonal)|

## 使用docker

1. 创建/修改 `.env` 文件，参照 [example.env](https://github.com/kcwikizh/kcwiki-luatable/blob/master/example.env)
2. 构建镜像:
```
docker build -t kcwiki-luatable .
```
3. 使用镜像运行:
```
docker run --env-file .env -t kcwiki-luatable
```
