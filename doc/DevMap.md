# DevMap

## 预计实现

### 基础部分

-[ ] 屏幕指定区域点击
-[ ] 坐标位置识别
-[ ] 依照给定路线行动

### 更多内容

-[ ] config仅指定部分节点，路线自主规划
-[ ] 地图二值化保存以供寻路

## 各文件内容

### Main

主单元

### Ocr

识别指定部分文字，并将识别出的文字与坐标传递给`wordprocessing`

### Wordprocessing

筛选出tee坐标信息及需要点击坐标内容，具体内容由config决定

### Test

测试部分