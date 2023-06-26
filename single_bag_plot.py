#!/usr/bin/env python3

import os
import rosbag
import numpy as np
import matplotlib.pyplot as plt

# バッグファイルのパス
bag_path = os.path.join('/home/atsuki/lab_ws/src/separation_curve/bagfile', 'example_renga.bag')

# バッグファイルを読み込む
bag = rosbag.Bag(bag_path, 'r')
np_poses = None
for topic, msg, t in bag.read_messages():
    if topic == "/scan":
        np_pose = np.zeros((896, 4))

        for i in range(360):
            np_pose[i, 0] = msg.ranges[i]
            np_pose[i, 1] = msg.intensities[i]
            np_pose[i, 2] = t.secs
            np_pose[i, 3] = t.nsecs
            i += 1

        if np_poses is None:
            np_poses = np_pose
        else:
            np_poses = np.append(np_poses, np_pose, axis=0)

bag.close()

# 500mmごとの強度の平均値を計算
ranges = np_poses[:, 0]
intensities = np_poses[:, 1]

bin_ranges = np.arange(0, 100, 0.1)  # 100mmごとの範囲
bin_intensities = []
bin_intensities_2sigma = []  # 平均に2σを足した値を格納するリスト

for bin_start in bin_ranges:
    bin_end = bin_start + 0.1
    mask = (ranges >= bin_start) & (ranges < bin_end)
    if np.any(mask):  # データが存在する場合のみ計算
        bin_intensity = np.mean(intensities[mask])
        bin_std = np.std(intensities[mask])
        bin_intensity_2sigma = bin_intensity + 2 * bin_std  # 平均に2σを足した値を計算
    else:
        bin_intensity = np.nan
        bin_intensity_2sigma = np.nan
    bin_intensities.append(bin_intensity)
    bin_intensities_2sigma.append(bin_intensity_2sigma)

# プロット
plt.subplot(111)
plt.title("Range & Intensity")
plt.xlabel("Range [m]")
plt.ylabel("Intensity")
plt.xlim(2.5, 8)
plt.ylim(0, 3000)

plt.scatter(np_poses[:, 0], np_poses[:, 1], s=4, c='g', alpha=0.3, label="renga")

# 強度の平均値を赤い点でプロット
valid_indices = ~np.isnan(bin_intensities)
plt.scatter(bin_ranges[valid_indices], np.array(bin_intensities)[valid_indices], c='r', marker='x', label="Average Intensity")

# 平均+2σの値を青い点でプロット
valid_indices_2sigma = ~np.isnan(bin_intensities_2sigma)
plt.scatter(bin_ranges[valid_indices_2sigma], np.array(bin_intensities_2sigma)[valid_indices_2sigma], c='b', marker='o', label="Average + 2σ")

plt.legend(fontsize=10)
plt.show()
