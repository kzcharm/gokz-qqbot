# gokz-qqbot

>  该机器人支持添加到好友列表私聊命令使用, 机器人会自动同意
> 也可以拉到其他群里使用(偶尔会自动同意)

### 通用指定参数:

- `-q` | `--qid` 指定你想查询的人的QQ号
- `-s` | `--steamid` 指定你想查询的人的steamid
- `-m` | `--mode` 指定KZ模式 `k, s, v` | `kzt, skz, vnl`
- `-u` | `--update` 强制更新. 例如kzgo.eu的截图默认会缓存一天, 加上此条会强制生成新的截图

例:

- > - `/kz -m s` 用 `-m s` 指定生成skz模式的截图
  > - `/kz -q 986668916 -m v` 生成qq号*986668916*用户的VNL模式截图
  > - `/kz -s 1061976400 -u` 生成steamid为*1061976400*用户的截图, 并强制更新

### 通用

- `/help` 查看帮助

- `/bind <steamid>` 绑定steamid, 支持任意格式. 例: `/bind STEAM_1:0:530988200`
- `/mode <mode>` 切换默认模式 例: `/mode skz`

### GOKZ全球

- `/kz` | `/kzgo` 生成kzgo.eu截图. 例:

- `/pb <map_name>` 查询玩家在某张地图上的PB
- `/pr` 查询玩家最新跳的一张图
- `/wr  <map_name>` 查询世界记录

### GOKZ.TOP

- `/rank` | `/排行` 查询玩家的[gokz.top](https://gokz.top/)排名
- `/pk` 与他人进行Rank PK, 需要用 `-q` 或者 `-s` 指定对手

- `/mp`| `/mapprogress` |`/进度 <map_name>` 查询玩家在某张地图上的进步情况
-  `/ccf` | `/查成分` 查询玩家游玩最多的服务器
- `/find <name>` 通过昵称查找玩家(注意这个并不是实时更新)

## How to start

1. generate project using `nb create` .
2. create your plugin using `nb plugin create` .
3. writing your plugins under `src/plugins` folder.
4. run your bot using `nb run --reload` .

## Documentation

See [Docs](https://nonebot.dev/)
