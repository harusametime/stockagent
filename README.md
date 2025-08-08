# 株式取引エージェント

日経225 ETF（1579.T と 1360.T）のための包括的な自動取引システム

## 概要

このシステムは、日経225 ETF（1579.T）と逆日経225 ETF（1360.T）の自動取引のための高度なアルゴリズム取引プラットフォームです。バックテスト、ライブ取引、リアルタイム市場データ分析の機能を提供します。

## 主な機能

- 📊 **バックテスト**: 複数の取引戦略の歴史的パフォーマンス分析
- 🤖 **ライブ取引**: KabusAPIを使用したリアルタイム自動取引
- 📈 **市場データ**: リアルタイム価格監視と分析
- ⚙️ **リスク管理**: ストップロス、利食い、ポジション管理
- 🔄 **複数戦略**: 平均回帰、モメンタム、ペア取引など

## 取引戦略

### 利用可能な戦略
1. **平均回帰** - RSIとボリンジャーバンドを使用
2. **モメンタム** - MACDと出来高分析
3. **ペア取引** - 1579.TとETFの価格差を利用
4. **トレンドフォロー** - 移動平均クロスオーバー
5. **ボラティリティブレイクアウト** - ボラティリティベースの取引
6. **レンジ相場戦略** - 横ばい市場向けの戦略

## セットアップ

### 前提条件

- Python 3.8+
- KabusAPI アカウント（ライブ取引用）
- Windows OS（Nginx リバースプロキシ用）

### クイックスタート

1. **リポジトリをクローン**:
```bash
git clone https://github.com/harusametime/stockagent.git
cd stockagent
```

2. **環境設定**:
```bash
# .env.example から .env を作成
cp .env.example .env

# .env ファイルを編集してAPI認証情報を設定
notepad .env
```

3. **依存関係をインストール**:
```bash
pip install -r requirements.txt
```

4. **アプリケーションを実行**:
```bash
streamlit run app.py
```

## Docker/Podman を使用した実行

### Docker の場合
```bash
# イメージをビルド
docker-compose build

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### Podman の場合（Windows）
```bash
# PowerShell で実行
.\podman-run.ps1 build
.\podman-run.ps1 start

# または一括実行
.\podman-run.ps1 quick
```

### macOS/Linux の場合
```bash
# Bash で実行
./macos/docker-run.sh build
./macos/docker-run.sh start

# または Podman
./macos/podman-run.sh build
./macos/podman-run.sh start
```

## 環境変数設定

`.env` ファイルで以下の変数を設定してください：

```env
# KabusAPI 設定（リバースプロキシ使用）
KABUSAPI_HOST=host.containers.internal
KABUSAPI_PORT=8080
KABUSAPI_ENV=dev  # オプション: dev (ポート 18081) または prod (ポート 18080)
KABUSAPI_PASSWORD=your_password_here

# 取引設定
INITIAL_CAPITAL=1000000
MAX_POSITION_SIZE=500000
STOP_LOSS_PCT=5
TAKE_PROFIT_PCT=10
MAX_DAILY_TRADES=10
```

## リバースプロキシ設定（Windows）

KabusAPIは `localhost` 接続のみを許可するため、コンテナからアクセスするにはリバースプロキシが必要です。

### 自動セットアップ（推奨）
```bash
# 管理者権限でPowerShellを実行
powershell -ExecutionPolicy Bypass -File setup-windows.ps1
```

### 手動セットアップ
1. Nginx をダウンロード・インストール
2. 設定ファイルを配置
3. プロキシを起動

詳細は `README_REVERSE_PROXY.md` を参照してください。

## 使用方法

### バックテスト
1. **バックテスト** タブを選択
2. 戦略とパラメータを設定
3. **バックテストを実行** をクリック
4. 結果とP&L分析を確認

### ライブ取引
1. **ライブ取引** タブを選択
2. **接続テスト** で API 接続を確認
3. 取引戦略とパラメータを設定
4. **自動取引開始** で取引を開始

### 市場データ
1. **市場データ** タブを選択
2. 自動更新間隔を設定
3. リアルタイム価格と履歴チャートを監視

## API接続テスト

プロキシ接続をテストするには：

```bash
# PowerShell で実行
.\podman-run.ps1 proxy

# または直接テスト
podman run --rm -it --add-host host.containers.internal:192.168.1.20 curlimages/curl curl -v -H "Content-Type: application/json" -d "{'APIPassword':'APIKensyou'}" http://host.containers.internal:8080/kabusapi/token
```

## トラブルシューティング

### よくある問題

1. **接続エラー**:
   - Nginx プロキシが起動しているか確認
   - Windows ファイアウォールの設定を確認
   - ポート 8080 が使用可能か確認

2. **認証エラー**:
   - `.env` ファイルのパスワードを確認
   - KabusAPI が localhost:18081 で起動しているか確認

3. **データ取得エラー**:
   - インターネット接続を確認
   - Yahoo Finance API の制限を確認

### ログの確認

```bash
# Docker の場合
docker-compose logs stockagent

# Podman の場合
.\podman-run.ps1 logs
```

## 開発

### プロジェクト構造

```
stockagent/
├── app.py                      # Streamlit メインアプリ
├── backtesting.py              # バックテストエンジン
├── live_trading.py             # ライブ取引エージェント
├── trading_algorithms.py       # 取引アルゴリズム
├── requirements.txt            # Python 依存関係
├── Dockerfile                  # Docker 設定
├── docker-compose.yml          # Docker Compose 設定
├── podman-compose.yml          # Podman Compose 設定
├── nginx-simple.conf           # Nginx 設定
├── setup-windows.ps1           # Windows セットアップスクリプト
├── podman-run.ps1              # Windows Podman 実行スクリプト
├── macos/                      # macOS 用スクリプト
│   ├── docker-run.sh           # Docker 実行スクリプト
│   └── podman-run.sh           # Podman 実行スクリプト
├── test/                       # テストファイル
│   ├── test_api_connection.py  # API接続テスト
│   ├── test_backtesting.py     # バックテストテスト
│   └── ...                     # その他のテストファイル
├── analysis/                   # 分析スクリプト
│   ├── analyze_pairs_trading.py # ペア取引分析
│   ├── compare_all_strategies.py # 戦略比較
│   └── ...                     # その他の分析ファイル
└── README_en.md                # 英語版README
```

### 新しい戦略の追加

1. `trading_algorithms.py` に戦略関数を追加
2. `STRATEGIES` 辞書に戦略を登録
3. `app.py` でパラメータ設定UIを追加

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 免責事項

このソフトウェアは教育目的で提供されています。実際の取引での使用は自己責任で行ってください。投資にはリスクが伴い、元本を失う可能性があります。

---

**注意**: KabusAPIの使用には証券会社との契約が必要です。また、自動取引を行う前に十分なテストを実施してください。