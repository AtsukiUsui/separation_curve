#!/usr/bin/env python3

import os
import rosbag
import numpy as np
import matplotlib.pyplot as plt

# バッグファイルのパス
bag_path_1 = os.path.join('/home/atsuki/lab_ws/src/separation_curve/bagfile', 'example_shiba.bag') # grass_bag
bag_path_2 = os.path.join('/home/atsuki/lab_ws/src/separation_curve/bagfile', 'example_renga.bag') # renga_bag 

# バッグファイルを読み込む
bag_1 = rosbag.Bag(bag_path_1, 'r')
bag_2 = rosbag.Bag(bag_path_2, 'r')

np_poses_1 = None
np_poses_2 = None

# バッグファイル1のデータを処理
for topic, msg, t in bag_1.read_messages():
    if topic == "/scan":
        np_pose = np.zeros((896, 4))

        for i in range(360):
            np_pose[i, 0] = msg.ranges[i]
            np_pose[i, 1] = msg.intensities[i]
            np_pose[i, 2] = t.secs
            np_pose[i, 3] = t.nsecs
            i += 1

        if np_poses_1 is None:
            np_poses_1 = np_pose
        else:
            np_poses_1 = np.append(np_poses_1, np_pose, axis=0)

bag_1.close()

# バッグファイル2のデータを処理
for topic, msg, t in bag_2.read_messages():
    if topic == "/scan":
        np_pose = np.zeros((896, 4))

        for i in range(360):
            np_pose[i, 0] = msg.ranges[i]
            np_pose[i, 1] = msg.intensities[i]
            np_pose[i, 2] = t.secs
            np_pose[i, 3] = t.nsecs
            i += 1

        if np_poses_2 is None:
            np_poses_2 = np_pose
        else:
            np_poses_2 = np.append(np_poses_2, np_pose, axis=0)

bag_2.close()

# 強度の平均値を計算
ranges_1 = np_poses_1[:, 0]
intensities_1 = np_poses_1[:, 1]
ranges_2 = np_poses_2[:, 0]
intensities_2 = np_poses_2[:, 1]

bin_ranges = np.arange(0, 100, 0.1)  # 100mmごとの範囲
bin_intensities_1 = []
bin_intensities_2 = []
bin_intensities_2sigma_1 = []  # 平均に2σを足した値を格納するリスト
bin_intensities_2sigma_2 = []

for bin_start in bin_ranges:
    bin_end = bin_start + 0.1
    mask_1 = (ranges_1 >= bin_start) & (ranges_1 < bin_end)
    mask_2 = (ranges_2 >= bin_start) & (ranges_2 < bin_end)
    
    if np.any(mask_1):  # バッグファイル1のデータが存在する場合のみ計算
        bin_intensity_1 = np.mean(intensities_1[mask_1])
        bin_std_1 = np.std(intensities_1[mask_1])
        bin_intensity_2sigma_1 = bin_intensity_1 - 2 * bin_std_1  # 平均に2σを引いた値を計算
    else:
        bin_intensity_1 = np.nan
        bin_intensity_2sigma_1 = np.nan
    
    if np.any(mask_2):  # バッグファイル2のデータが存在する場合のみ計算
        bin_intensity_2 = np.mean(intensities_2[mask_2])
        bin_std_2 = np.std(intensities_2[mask_2])
        bin_intensity_2sigma_2 = bin_intensity_2 + 2 * bin_std_2  # 平均に2σを足した値を計算
    else:
        bin_intensity_2 = np.nan
        bin_intensity_2sigma_2 = np.nan
    
    bin_intensities_1.append(bin_intensity_1)
    bin_intensities_2.append(bin_intensity_2)
    bin_intensities_2sigma_1.append(bin_intensity_2sigma_1)
    bin_intensities_2sigma_2.append(bin_intensity_2sigma_2)

# valid_indices_2sigma_1とvalid_indices_2sigma_2の中間点を計算
bin_intensities_midpoint = (np.array(bin_intensities_2sigma_1) + np.array(bin_intensities_2sigma_2)) / 2


# プロット
plt.subplot(111)
plt.title(f"Range & Intensity")
plt.xlabel("Range [m]")
plt.ylabel("Intensity")
plt.xlim(2.5, 8)
plt.ylim(0, 3000)

# バッグファイル1のデータをプロット
plt.scatter(np_poses_1[:, 0], np_poses_1[:, 1], s=4, c='c', alpha=0.3, label="grass")

# バッグファイル2のデータをプロット
plt.scatter(np_poses_2[:, 0], np_poses_2[:, 1], s=4, c='r', alpha=0.3, label="renga")

# バッグファイル1の強度の平均値を赤い点でプロット
valid_indices_1 = ~np.isnan(bin_intensities_1)
plt.scatter(bin_ranges[valid_indices_1], np.array(bin_intensities_1)[valid_indices_1], c='r', marker='x', label="Average Intensity (grass)")

# バッグファイル2の強度の平均値を青い点でプロット
valid_indices_2 = ~np.isnan(bin_intensities_2)
plt.scatter(bin_ranges[valid_indices_2], np.array(bin_intensities_2)[valid_indices_2], c='g', marker='x', label="Average Intensity (renga)")

# バッグファイル1の平均+2σの値をオレンジの点でプロット
valid_indices_2sigma_1 = ~np.isnan(bin_intensities_2sigma_1)
plt.scatter(bin_ranges[valid_indices_2sigma_1], np.array(bin_intensities_2sigma_1)[valid_indices_2sigma_1], c='purple', marker='o', label="Average + 2σ (grass)")

# バッグファイル2の平均+2σの値を紫の点でプロット
valid_indices_2sigma_2 = ~np.isnan(bin_intensities_2sigma_2)
plt.scatter(bin_ranges[valid_indices_2sigma_2], np.array(bin_intensities_2sigma_2)[valid_indices_2sigma_2], c='b', marker='o', label="Average + 2σ (renga)")

# valid_indices_2sigma_1とvalid_indices_2sigma_2の中間点をプロット
valid_indices_midpoint = valid_indices_2sigma_1 & valid_indices_2sigma_2
plt.scatter(bin_ranges[valid_indices_midpoint], bin_intensities_midpoint[valid_indices_midpoint], c='orange', marker='o', label="Midpoint")

# # 中間点の近似曲線を求める
degree = 3  # 多項式の次数
coefficients = np.polyfit(bin_ranges[valid_indices_midpoint], bin_intensities_midpoint[valid_indices_midpoint], degree)
poly = np.poly1d(coefficients)  # 近似曲線の関数

# 近似曲線の範囲を設定（近似曲線は元データに依存するので元データ大事）
# curve_range = np.linspace(min(bin_ranges), max(bin_ranges), 100) # データがなくても近似曲線をプロットする
curve_range = np.linspace(bin_ranges[valid_indices_midpoint][0], bin_ranges[valid_indices_midpoint][-1], 100) #データがある部分までで止める

# 近似曲線をプロット
plt.plot(curve_range, poly(curve_range), 'm-', label="Approximation Curve")


# 近似曲線の式を出力
print("Approximation Curve:")
print(poly)

plt.legend(fontsize=10)
plt.show()


