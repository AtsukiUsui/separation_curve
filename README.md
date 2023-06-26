# separation_curve
## Overview
分離曲線を生成するプログラムです。  
芝生とレンガのbagファイルを入れると、最適な分離曲線をグラフにプロットし、出力します。


## Install & How to use
```
git@github.com:AtsukiUsui/separation_curve.git
python3 double_bag_plot.py
```

| 変数名     | 初期値            | 説明                | 
| ---------- | ----------------- | ------------------- | 
| bag_path_1 | example_shiba.bag | 芝生のbagファイル   | 
| bag_path_2 | example_renga.bag | レンガのbagファイル | 
| degree     | 3                 | 近似曲線の次数      | 
| dpi     | 1000(初期値：100)                | グラフの解像度   | 

* rosbagは[separation_curve/bagfile](/bagfile)に置いてください。
* プロットしたグラフは[separation_curve/plot](/plot)に以下の名前で保存されます。  
``"Range & Intensity ({bag_filename_1}, {bag_filename_2}).png"``


## Author
  臼井温希  
  千葉工業大学 先進工学部 未来ロボティクス学科  
  kmmm13037@gmail.com

## Lincense
"illuminometer_pub" is under [Apache License 2.0](/LICENSE)

## Reference
[刈払ロボットのためのLIDARの受光強度情報を用いた植生に含まれる石質障害物の検出手法（環境光及び計測対象の湿潤条件を考慮した反射強度の補正式の提案）](https://www.jstage.jst.go.jp/article/transjsme/80/819/80_2014dr0330/_article/-char/ja/)  
著者：大川 真弥, 滝田 好宏, 伊達 央