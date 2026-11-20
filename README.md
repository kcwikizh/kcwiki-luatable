# Kcwiki-Luatable

[![GitHub CI](https://github.com/kcwikizh/kcwiki-luatable/actions/workflows/python-app.yml/badge.svg)](https://github.com/kcwikizh/kcwiki-luatable/actions/workflows/python-app.yml)
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

## 关于 en.kancollewiki.net 的人机校验

深海敌舰/深海装备/制空数据来自 `en.kancollewiki.net`。该站对 GitHub 托管 runner 的出口 IP
（Azure / AS8075）直接返回 Cloudflare 人机校验页，特征为：

```
HTTP 403, cf-mitigated: challenge, "Just a moment..."
```

实测 curl / urllib / aiohttp、换 UA、换 Referer、换 HTTP 版本、换站点别名域名表现一致，
属于按出口 IP/ASN 的挑战，客户端无法通过。因此在托管 runner 上会跳过 `ShinkaiLuatable`：

- 相关表（`shinkai-items.lua` / `shinkai-ships.lua` / `airpower_table.lua`）本次不生成；
- 部署步骤用 `keep_files` 保留线上旧文件，不会像以前那样把已发布的文件整份删掉；
- 构建会打印 `::warning::` 注解，可在一眼看到摘要里发现。

要让这三张表恢复更新，二选一：

1. 给 workflow 配置 `KCWIKI_PROXY` secret（非受限出口的 HTTP/SOCKS5 代理）；
2. 联系 wiki 管理员为该 bot 的出口放行（MediaWiki 侧 bot 白名单 / Cloudflare 规则豁免）。
