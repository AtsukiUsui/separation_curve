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

bin_ranges = np.arange(0, 100, 0.1)  # 500mmごとの範囲
bin_intensities = []
for bin_start in bin_ranges:
    bin_end = bin_start + 0.1
    mask = (ranges >= bin_start) & (ranges < bin_end)
    if np.any(mask):  # データが存在する場合のみ計算
        bin_intensity = np.mean(intensities[mask])
    else:
        bin_intensity = np.nan
    bin_intensities.append(bin_intensity)

# プロット
plt.subplot(111)
plt.title("Range & Intensity UTM-30LX")
plt.xlabel("Range [m]")
plt.ylabel("Intensity")
plt.xlim(2.5, 8)
plt.ylim(0, 3000)

plt.scatter(np_poses[:, 0], np_poses[:, 1], s=4, c='g', alpha=0.3, label="renga")

# 500mmごとの強度の平均値を赤い点でプロット
valid_indices = ~np.isnan(bin_intensities)
plt.scatter(bin_ranges[valid_indices], np.array(bin_intensities)[valid_indices], c='r', marker='o', label="Average Intensity")

plt.legend(fontsize=10)
plt.show()

