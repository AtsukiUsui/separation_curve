# SPDX-FileCopyrightText: 2023 Atsuki Usui <kmmm13037@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3

import os
import rosbag
import numpy as np
import matplotlib.pyplot as plt
import argparse

degree = 1  # 多項式の次数

# 分離曲線の生成に使用する、距離の範囲
distance_lower_limit = 3.0  # 適切な下限を設定してください
distance_upper_limit = 5.0  # 適切な上限を設定してください

angle_limit = 70

parser = argparse.ArgumentParser(description='Process ROS bag files.')
parser.add_argument('bag_file_1', type=str, help='Path to the grass bag file')
parser.add_argument('bag_file_2', type=str, help='Path to the brick bag file')
args = parser.parse_args()


equation = input("Enter the equation: ")

# 数式を解析して関数オブジェクトを生成
x = np.linspace(-10, 10, 100)
y = eval(equation)


def apply_distance_limit(np_poses, lower_limit, upper_limit):
    valid_indices = (np_poses[:, 0] >= lower_limit) & (
        np_poses[:, 0] <= upper_limit)
    return np_poses[valid_indices]


bag_file_1 = args.bag_file_1
bag_file_2 = args.bag_file_2
bag_filename_1 = os.path.basename(bag_file_1)
bag_filename_2 = os.path.basename(bag_file_2)

# バッグファイルを読み込む
bag_1 = rosbag.Bag(bag_file_1, 'r')
bag_2 = rosbag.Bag(bag_file_2, 'r')

np_poses_1 = None
np_poses_2 = None


# バッグファイル1のデータを処理
for topic, msg, t in bag_1.read_messages():
    if topic == "/diag_scan":
        np_pose = np.zeros((896, 4))

        angle_min = msg.angle_min  # 最小角度
        angle_increment = msg.angle_increment  # 角度の増分

        # for i in range(360):
        #     np_pose[i, 0] = msg.ranges[i]
        #     np_pose[i, 1] = msg.intensities[i]
        #     np_pose[i, 2] = t.secs
        #     np_pose[i, 3] = t.nsecs
        #     i += 1

        for i in range(360):
            angle = angle_min + i * angle_increment  # 各データ点の角度を計算
            range_value = msg.ranges[i]
            if 0 <= range_value <= 10.0 and -angle_limit <= np.degrees(angle) <= angle_limit:
                np_pose[i, 0] = msg.ranges[i]
                np_pose[i, 1] = msg.intensities[i]

        if np_poses_1 is None:
            np_poses_1 = np_pose
        else:
            np_poses_1 = np.append(np_poses_1, np_pose, axis=0)

# 距離の範囲制限を適用
np_poses_1 = apply_distance_limit(
    np_poses_1, distance_lower_limit, distance_upper_limit)


# /luminous_intensity
topic_name = "/luminous_intensity"

# メッセージの総数と合計値を初期化
count_1 = 0
total_illumination_1 = 0.0

# 指定したトピックのメッセージをイテレーション (bag_1)
for topic, msg, t in bag_1.read_messages(topics=[topic_name]):
    illumination = msg.data  # Float64メッセージのデータフィールドから値を取得
    total_illumination_1 += illumination
    count_1 += 1

# 平均値を計算 (bag_1)
if count_1 > 0:
    average_illumination_1 = total_illumination_1 / count_1
    rounded_illumination_1 = round(average_illumination_1, 0)
    integer_illumination_1 = int(rounded_illumination_1)
    print("平均照度 （芝生）:", integer_illumination_1)
else:
    print("No messages found on the", topic_name, "topic.")

bag_1.close()

# バッグファイル2のデータを処理
for topic, msg, t in bag_2.read_messages():
    if topic == "/diag_scan":
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

# 距離の範囲制限を適用
np_poses_2 = apply_distance_limit(
    np_poses_2, distance_lower_limit, distance_upper_limit)

# メッセージの総数と合計値を初期化
count_2 = 0
total_illumination_2 = 0.0

# 指定したトピックのメッセージをイテレーション (bag_2)
for topic, msg, t in bag_2.read_messages(topics=[topic_name]):
    illumination = msg.data  # Float64メッセージのデータフィールドから値を取得
    total_illumination_2 += illumination
    count_2 += 1

# 平均値を計算 (bag_2)
if count_2 > 0:
    average_illumination_2 = total_illumination_2 / count_2
    rounded_illumination_2 = round(average_illumination_2, 0)
    integer_illumination_2 = int(rounded_illumination_2)
    print("平均照度 (レンガ):", integer_illumination_2)
else:
    print("No messages found on the", topic_name, "topic.")

bag_2.close()

# 2つの平均値の平均値を計算
average_illumination_combined = (
    average_illumination_1 + average_illumination_2) / 2
rounded_illumination_combined = round(average_illumination_combined, 0)
integer_illumination_combined = int(rounded_illumination_combined)

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
bin_intensities_midpoint = (
    np.array(bin_intensities_2sigma_1) + np.array(bin_intensities_2sigma_2)) / 2


# プロット
fig = plt.figure(figsize=(12.8, 9.6))  # 新しい図を作成してサイズを指定
plt.subplot(111)
plt.title(
    f"Range & Intensity ({bag_filename_1}, {bag_filename_2})\nAverage Illumination: {integer_illumination_combined}({integer_illumination_1},{integer_illumination_2})")
plt.xlabel("Range [m]")
plt.ylabel("Intensity")
# plt.xlim(2, 7.5)
# plt.xlim(distance_lower_limit, distance_upper_limit)
plt.xlim(0, distance_upper_limit)
plt.ylim(0, 4000)

# バッグファイル1のデータをプロット
plt.scatter(np_poses_1[:, 0], np_poses_1[:, 1],
            s=4, c='c', alpha=0.3, label="grass")

# バッグファイル2のデータをプロット
plt.scatter(np_poses_2[:, 0], np_poses_2[:, 1],
            s=4, c='r', alpha=0.3, label="renga")

# バッグファイル1の強度の平均値を赤い点でプロット
valid_indices_1 = ~np.isnan(bin_intensities_1)
plt.scatter(bin_ranges[valid_indices_1], np.array(bin_intensities_1)[
            valid_indices_1], c='r', marker='x', label="Average Intensity (grass)")

# バッグファイル2の強度の平均値を青い点でプロット
valid_indices_2 = ~np.isnan(bin_intensities_2)
plt.scatter(bin_ranges[valid_indices_2], np.array(bin_intensities_2)[
            valid_indices_2], c='g', marker='x', label="Average Intensity (renga)")

# バッグファイル1の平均+2σの値をオレンジの点でプロット
valid_indices_2sigma_1 = ~np.isnan(bin_intensities_2sigma_1)
plt.scatter(bin_ranges[valid_indices_2sigma_1], np.array(bin_intensities_2sigma_1)[
            valid_indices_2sigma_1], c='purple', marker='o', label="Average + 2σ (grass)")

# バッグファイル2の平均+2σの値を紫の点でプロット
valid_indices_2sigma_2 = ~np.isnan(bin_intensities_2sigma_2)
plt.scatter(bin_ranges[valid_indices_2sigma_2], np.array(bin_intensities_2sigma_2)[
            valid_indices_2sigma_2], c='b', marker='o', label="Average + 2σ (renga)")

# valid_indices_2sigma_1とvalid_indices_2sigma_2の中間点をプロット
valid_indices_midpoint = valid_indices_2sigma_1 & valid_indices_2sigma_2
plt.scatter(bin_ranges[valid_indices_midpoint],
            bin_intensities_midpoint[valid_indices_midpoint], c='orange', marker='o', label="Midpoint", s=100)

# 中間点の近似曲線を求める

coefficients = np.polyfit(bin_ranges[valid_indices_midpoint],
                          bin_intensities_midpoint[valid_indices_midpoint], degree)
poly = np.poly1d(coefficients)  # 近似曲線の関数


# 分離曲線を1行で表し、次数の多い順からソートする
def format_polynomial(coefficients):
    terms = []
    for power, coef in sorted(enumerate(coefficients[::-1]), reverse=True):
        if power == 0:
            term = f"{coef:.4g}"
        elif power == 1:
            term = f"{coef:.4g}x"
        else:
            term = f"{coef:.4g}x^{power}"
        terms.append(term)
    return ' + '.join(terms)


poly_str = format_polynomial(coefficients)

# 近似曲線の範囲を設定（近似曲線は元データに依存するので元データ大事）
curve_range = np.linspace(np.min(bin_ranges), np.max(
    bin_ranges), 100)  # データがなくても近似曲線をプロットする
# curve_range = np.linspace(bin_ranges[valid_indices_midpoint][0],
#                           bin_ranges[valid_indices_midpoint][-1], 100)  # データがある部分までで止める

# 近似曲線をプロット
plt.plot(curve_range, poly(curve_range), 'k-',
         linewidth=6.0, label="Approximation Curve")


# 近似曲線の式をグラフに表示
equation_text = f"Approximation Curve: \n {poly}"
plt.text(3, 200, equation_text, fontsize=12, color='black',
         bbox=dict(facecolor='w', edgecolor='red', boxstyle='square'))

# 入力した曲線をプロット
plt.plot(x, y, linewidth=6.0, color='b')

# 近似曲線の式を出力
print("-------------------------------------------------------\n")
print("生成した分離曲線:")
print(poly, "\n")
print(poly_str, "\n")

# 芝生の認識率（分離曲線より大きい）
intensity_vals_grass = np_poses_1[:, 1]
valid_indices_grass = (np_poses_1[:, 0] != 0) & (
    intensity_vals_grass != 0)  # 距離と強度が0でないインデックスを取得
ratio_grass = (np.sum(intensity_vals_grass[valid_indices_grass] > poly(
    np_poses_1[:, 0][valid_indices_grass])) / len(intensity_vals_grass[valid_indices_grass])) * 100
ratio_grass = round(ratio_grass, 2)  # 小数点第2位までに制限

print("芝生の点群数        :", np.sum(valid_indices_grass))
print("分離曲線以下の点群数:", len(valid_indices_grass))
print("->芝生の認識率      : %.2f%%\n" % ratio_grass)

# レンガの認識率(分離曲線より小さい)
intensity_vals_renga = np_poses_2[:, 1]
valid_indices_renga = (np_poses_2[:, 0] != 0) & (
    intensity_vals_renga != 0)  # 距離と強度が0でないインデックスを取得
ratio_renga = (np.sum(intensity_vals_renga[valid_indices_renga] < poly(
    np_poses_2[:, 0][valid_indices_renga])) / len(intensity_vals_renga[valid_indices_renga])) * 100
ratio_renga = round(ratio_renga, 2)  # 小数点第2位までに制限

print("レンガの点群数      :", np.sum(valid_indices_renga))
print("分離曲線以下の点群数:", len(valid_indices_renga))
print("->レンガの認識率    : %.2f%%\n" % ratio_renga)


# 入力した等式に関しての認識率
print("-------------------------------------------------------\n")
print("入力した等式：", equation, "\n")


# 入力した等式を評価して関数として扱う
def parsed_equation(x): return eval(equation)


# 芝生の認識率（分離曲線より大きい）
ratio_grass_equation = (
    np.sum(intensity_vals_grass[valid_indices_grass] > parsed_equation(
        np_poses_1[:, 0][valid_indices_grass]))
    / len(intensity_vals_grass[valid_indices_grass])
) * 100
ratio_grass_equation = round(ratio_grass_equation, 2)

print("芝生の点群数        :", np.sum(valid_indices_grass))
print("分離曲線以下の点群数:", len(valid_indices_grass))
print("->芝生の認識率      : %.2f%%\n" % ratio_grass_equation)

# レンガの認識率(分離曲線より小さい)
ratio_renga_equation = (
    np.sum(intensity_vals_renga[valid_indices_renga] < parsed_equation(
        np_poses_2[:, 0][valid_indices_renga]))
    / len(intensity_vals_renga[valid_indices_renga])
) * 100
ratio_renga_equation = round(ratio_renga_equation, 2)

print("レンガの点群数      :", np.sum(valid_indices_renga))
print("分離曲線以下の点群数:", len(valid_indices_renga))
print("->レンガの認識率    : %.2f%%" % ratio_renga_equation)

# equationを変換
equation_str = equation = equation.replace('**2', '^2')
equation_str = equation_str.replace('*x', 'x')

# 凡例にラベルを追加
labels = [
    "grass",
    "renga",
    "Average Intensity (grass)",
    "Average Intensity (renga)",
    "Average + 2σ (grass)",
    "Average + 2σ (renga)",
    "Midpoint",
    f"Approximation Curve: \n{poly_str}",
    f"  Grass_ratio:{ratio_grass}%"
    f"\n  Renga_ratio:{ratio_renga}%"
    f"\nInput Equation: \n{equation_str}"
    f"\n  Grass_ratio:{ratio_grass_equation}%"
    f"\n  Renga_ratio:{ratio_renga_equation}%"
]

plt.legend(fontsize=10, loc='upper right', labels=labels)

# 自動保存機能（保存名は、bagファイルの名前）
# 保存パスの作成
save_filename = f"Range & Intensity ({bag_filename_1}, {bag_filename_2}).png"
save_path = os.path.join("plot", save_filename)

# グラフの保存
plt.savefig(save_path, dpi=100)

plt.show()
