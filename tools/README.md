# 小工具目录

## 主文件

文件名|说明
--|--
gen_aqua_music_map.py|生成客户端的曲名-ID映射表与歌曲-版本映射表
gen_prober_music_data.py|从查分网站获取原始歌曲数据
pushpull_mai_stat.py|从查分网站拉取数据并搬运到aqua服
gen_music_crossmap|建立查分网站与aqua服所有歌曲id映射

## 辅助文件

文件名|说明
--|--
cache_access.py|让我康康`../cache`里的json们
cfg_reader.py|读取CONFIG.json至模块变量
CONFIG.json|一些配置