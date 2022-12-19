# 障害シミュレーションツール

CPU負荷やネットワーク障害などをシミュレーションするためのツールです。
Chaos Toolkitから呼び出されることを前提としています。

## 前提

Chaos Toolkitや本プログラムを動作させる環境をクライアント側、本プログラムで障害をシミュレーションする環境をサーバ側として、依存するライブラリやツールは以下のバージョンで動作確認をおこなっています。

### クライアント側

- Python: 3.10
- Chaos Toolkit: 1.12.0

### サーバ側

- OS: RHEL 8.6
- chronyc (chrony): 4.1
- date (GNU coreutils): 8.30
- fio: 3.19
- iptables: 1.8.4
- tc: 5.15.0
- pkill(procps-ng): 3.3.15
- stress-ng: 0.13.10

## 導入方法

リポジトリを取得した後に必要なパッケージをインストールし、`src`ディレクトリを`PYTHONPATH`に追加することでChaos Toolkitから呼び出すことができるようになります。

```bash
git clone https://github.com/fault-injection-testing/fault-injection-tool.git
cd fault-injection-tool
pip install -r requirements.txt
export PYTHONPATH=$PWD/src
```

## 利用方法

### 利用可能な関数

利用可能な関数に関しては[こちら](./functions.md)を参照してください。

### 利用例

Chaos Toolkitの[Configuration](https://chaostoolkit.org/reference/api/experiment/#configuration)を利用して環境変数から障害シミュレーション先に関する情報を設定したり、Chaos Toolkitから障害をシミュレーションする関数を呼び出す例はexampleディレクトリ配下のJSONのシナリオファイルで確認できます。

## 開発者向け

### LintingとFormatting

`black`と`isort`を利用してコードのチェックとフォーマット修正をおこないます。それぞれに必要なコマンドは[Makefile](./Makefile)で実行できます。

以下のコマンドでコード全体のチェックがおこなえます。

```bash
make lint
```

以下のコマンドでコード全体のフォーマット修正がおこなえます。

```bash
make format
```

### テスト

以下のコマンドでテストの実行ができます。

```bash
make test
```

カバレッジの確認は以下のコマンドでできます。

```bash
make cov
```

## ライセンス

本ソフトウェアは、[Apache 2.0 ライセンス](./LICENSE.txt)の元提供されています。

© 2022 TIS Inc.
