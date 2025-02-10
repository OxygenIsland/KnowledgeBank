3、mac 配置 homebrew
5、微信文件传输助手里的视频整理一下
6、[obsidian图片排版](https://www.bilibili.com/video/BV1fB4y1i7qf/?spm_id_from=333.337.search-card.all.click&vd_source=ae99cbe2bab29b19bc05583b76d35b48)
7、稀土进出口量，做一些全局的分析，
8、人民币汇率下降和上升的影响
9、美元加息降息对经济的影响

> [!todo]+ 今日待做
> - [x] 1、收集一个笑话
> - [x] 2、拍一张照片
> - [x] 3、每天写点东西，感悟、心得、日记、知识整理、都可以

> [!todo]+ 本周待做
> - [ ] 1、整理好的脱口秀的稿子

> [!todo]+ 本月待做
> - [ ] 1、日本经济发展的历史

## Articles to be completed
```dataview 
LIST
FROM ""
WHERE status = "todo" 
```


## 需要完成和消化的文章
```dataview 
LIST
FROM ""
WHERE status = "ing"
```

## 需要整理的Fleeting
```dataview 
LIST
FROM ""
WHERE status = "todo" AND type = "Fleeting"
```

## 100封给朋友的信 
```dataview 
TABLE length(rows) AS "数量"
FROM ""
WHERE contains(file.tags, "100封给朋友的信")
GROUP BY "符合条件的笔记"
```

