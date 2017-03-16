### 特徴

* 計測対象の指標値をssh <host> <cmd> の形で取得します
 * 一回の実行で複数のホストから収集できます
 * 計測対象にファイルを残さない

* python2とd3jsでreportを生成します．MACにデフォルトで入っているpythonでも動くので，外部ライブラリの追加は不要．
 * ネットワーク環境があれば，d3jsのライブラリはダウンロードできるので，Offic経由のstepを省いています．

### ファイル

* report_links.html 各計測結果レポートへのリンク
* step0_preparation.py 計測対象サーバリストをmonitorの形で生成するスクリプト
* workspace/monitor_XXX/run_XXX/step1_start_monitor.sh 計測開始するスクリプト
* step2_generate_report.py 計測結果可視化させるスクリプト

### 使い方

* MACにリポジトリをcloneする

* monitor を生成

```sh
python step0_prerparation.py <monitor名> <host1>[,host2][,host2] ...

# ./workspace/
# ./workspace/monitor_XXXが生成される
```


* monitor 開始

```sh
./workspace/monitor_<monitor名>_生成日付け/step1_start_monitor.sh <計測感覚(秒)> <計測時間(秒)>

# ./workspace/monitor_XXX/run_XXX/が生成される
```

* レポート生成 を生成

```sh
python step2_generate_report.py

# ./workspace/monitor_XXX/run_XXX/<host>/report.htmlが 生成される
# report_links.htmlが生成される ここから結果を確認する
```
