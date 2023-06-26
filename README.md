# separation_curve
## Overview
分離曲線を生成するプログラムです。  
芝生とレンガのbagファイルを入れると、最適な分離曲線をグラフにプロットし、出力します。

## Install & How to use
```
git@github.com:AtsukiUsui/separation_curve.git
python3 double_bag_plot.py
```
以下オプション
| 変数名     | 初期値            | 説明                | 
| ---------- | ----------------- | ------------------- | 
| bag_path_1 | example_shiba.bag | 芝生のbagファイル   | 
| bag_path_2 | example_renga.bag | レンガのbagファイル | 
| degree     | 3                 | 近似曲線の次数      | 

* グラフは以下の名前で保存される  
"Range & Intensity ({bag_filename_1}, {bag_filename_2}).png"
* 

## 
* [single_bag_plot.py](separation_curve/single_bag_plot.py)
