---
title: "[[关于上下桩bug的归类和分析]]"
type: Reference
status: ing
Creation Date: 2026-09-16 15:20
tags:
---
上桩状态稳定性差，容易和底层状态耦合，比如急停的时候，上桩的状态就会被改变，整个状态就会乱掉了
上桩的状态没有明确的变化逻辑，导致UIUX的conner case也比较多，产生的bug也比较多
