import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import time  # 遅延処理用

# 日本語フォント設定（Windows用）
matplotlib.rc('font', family='MS Gothic')

# フォルダ名
DRIVER1_FOLDER = "Driver1_CSV"
DRIVER2_FOLDER = "Driver2_CSV"

def delay_message(message, seconds=3):
    """メッセージを表示しつつ遅延"""
    print(message, end="", flush=True)
    for _ in range(seconds):
        print(".", end="", flush=True)
        time.sleep(1)
    print()  # 行を確定

def initialize_folders():
    """初回実行時にフォルダを作成"""
    delay_message("初めての実行のため、必要なフォルダを生成します")
    os.makedirs(DRIVER1_FOLDER, exist_ok=True)
    os.makedirs(DRIVER2_FOLDER, exist_ok=True)
    print(f"\nフォルダを作成しました。\n1: {DRIVER1_FOLDER}\n2: {DRIVER2_FOLDER}")
    print("次の実行をする前に、作成したフォルダにそれぞれのドライバーのCSVデータを追加してください。")
    input("何かキーを押して終了します...")
    exit()

def get_csv_files(folder):
    """指定フォルダ内のCSVファイルを取得"""
    return glob.glob(os.path.join(folder, "*.csv"))

def convert_time_to_seconds(time_str):
    """タイム形式（分:秒.ミリ秒）を秒に変換"""
    try:
        minutes, seconds = time_str.split(':')
        total_seconds = int(minutes) * 60 + float(seconds)
        return total_seconds
    except ValueError:
        return None

def clean_and_prepare_data(data):
    """データを整形して必要な列を準備"""
    # 列名を正規化
    data.columns = data.columns.str.strip().str.replace("\t", "")

    # 不要な「スタート」行を削除
    data = data[data["ラップ"].str.isnumeric()]

    # 必須列の変換
    data["Lap"] = pd.to_numeric(data["ラップ"], errors="coerce")
    data["LapTime"] = data["タイム"].apply(convert_time_to_seconds)
    data["Position"] = pd.to_numeric(data["順位"], errors="coerce")

    # 欠損値を削除し、ラップ順に並べ替え
    data = data.dropna(subset=["Lap", "LapTime", "Position"]).sort_values(by="Lap")

    return data

def plot_graphs(csv_path, driver_name):
    """CSVからラップタイムと順位のグラフを生成"""
    try:
        # CSV読み込み
        data = pd.read_csv(csv_path, encoding="utf-8-sig")  # Shift-JISの場合は "shift-jis" に変更
        data = clean_and_prepare_data(data)

        if data.empty:
            print(f"{csv_path}: 整形後のデータが空です。スキップします。")
            return

        # グラフの描画
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # ラップタイムのプロット
        ax1.set_xlabel("Lap")
        ax1.set_ylabel("Lap Time (seconds)", color="tab:blue")
        ax1.plot(data["Lap"], data["LapTime"], label="Lap Time", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")

        # 順位のプロット（2軸目）
        ax2 = ax1.twinx()
        ax2.set_ylabel("Position", color="tab:red")
        ax2.plot(data["Lap"], data["Position"], label="Position", color="tab:red", linestyle="--")
        ax2.tick_params(axis="y", labelcolor="tab:red")

        # タイトルとレイアウト
        plt.title(f"{driver_name} Race Data")
        fig.tight_layout()

        # 画像保存
        output_file = f"{driver_name}_race_graph.png"
        plt.savefig(output_file)
        print(f"グラフを保存しました: {output_file}")
        plt.close()

    except Exception as e:
        print(f"エラーが発生しました: {e}")

def main():
    # フォルダの存在確認
    delay_message("必要なフォルダがあるか確認しています", seconds=3)
    if not os.path.exists(DRIVER1_FOLDER) or not os.path.exists(DRIVER2_FOLDER):
        print("\nError: CSVデータを格納するフォルダが見つかりません。")
        initialize_folders()

    print("\nフォルダチェックに成功しました！")

    # CSVデータの読み込みとグラフ生成
    delay_message("CSVデータを読み込んでいます", seconds=3)

    # Driver1の処理
    driver1_files = get_csv_files(DRIVER1_FOLDER)
    for file in driver1_files:
        plot_graphs(file, "Driver1")
        os.remove(file)

    # Driver2の処理
    driver2_files = get_csv_files(DRIVER2_FOLDER)
    for file in driver2_files:
        plot_graphs(file, "Driver2")
        os.remove(file)

    delay_message("すべての画像を生成しました！", seconds=3)
    print("\n使用したCSVファイルを削除しました。次回使用時は、もう一度CSVファイルを追加してください。")
    input("何かキーを押して終了します...")

if __name__ == "__main__":
    main()
