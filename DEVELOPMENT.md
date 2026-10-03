# Beta v0.1.0

## 目的
iPhone SafariからApple AR Quick Lookを起動し、ARKitによる実空間認識と3Dオブジェクト配置が動作することを確認する。

## 今回やらないこと
- カニギターモデル
- 撮影UI
- Webページ内での独自ARレンダリング
- オブジェクト選択
- 保存
- SNS投稿

## 実機確認
1. iPhone SafariでBetaページを開く
2. 「ARを開始」をタップ
3. カメラ権限を許可
4. 床が十分見えるように端末を動かす
5. 3Dオブジェクトを床面に配置
6. 移動・回転・拡大縮小を確認
7. Quick Lookを閉じてWebページに戻れることを確認

## ブランチ運用
- main: 正式版
- beta: 実機確認版

Betaで確認後、問題がなければmainへ反映する。


## 実機確認結果

2026-10-02 / iPhone Safari

- AR Quick Look 起動: OK
- 実空間の床への3Dモデル配置: OK
- モデル移動: OK
- モデル回転: OK
- ピンチ拡大縮小: OK

Beta v0.1.1 を最小ARプロトタイプの実機検証成功版とする。


## Beta v0.2.0

### 目的
外部のAppleサンプルに依存せず、リポジトリ内に保存した自前USDZをiPhone SafariからAR表示する。

### テストモデル
- path: `assets/test-object.usdz`
- 構成: 赤い立方体 + 黄色い球
- 実寸: 約20cm
- テクスチャなし
- USDZは無圧縮ZIP、格納データを64-byte境界に配置

### 実機確認項目
1. ページに `Beta v0.2.0` と表示される
2. 「ARを開始」からQuick Lookが起動する
3. 赤い立方体と黄色い球が表示される
4. 床へ配置できる
5. 移動・回転・拡大縮小ができる


### Beta v0.2.0 実機確認結果

2026-10-02 / iPhone Safari

- リポジトリ内USDZ読み込み: OK
- Quick Look起動: OK
- 床への配置: OK
- 移動・回転・拡大縮小: OK

Beta v0.2.0 を自前USDZ配信の実機検証成功版とする。


## Beta v0.3.0

### 目的
既存の `kani-camera` で使用している実物のKA-23カニギターFBXとPBRテクスチャをUSDZへ変換し、iPhone SafariのAR Quick Lookで実空間に配置する。

### 使用データ
- FBX: `CrabGuitarKA23_High.fbx`
- Albedo: `KA23_Red_Albedo.png`
- Metallic: `KA23_Solid_Metallic.png`
- Roughness: `KA23_Solid_Roughness.png`
- AR用生成物: `assets/kani-guitar-red.usdz`
- 最大寸法: 約0.80m

### 変換
GitHub Actions上のBlender 4.5 LTSで自動変換する。
`scripts/convert_to_usdz.py` を更新するとUSDZを再生成できる。

### 実機確認項目
1. ページに `Beta v0.3.0` と表示される
2. ARを開始すると赤いカニギターが表示される
3. 形状が既存モデルと一致している
4. テクスチャの向き・色が正しい
5. 床に自然な向きで接地する
6. 実寸感が適切か確認する
7. 移動・回転・拡大縮小ができる


## Beta v0.4.0

### 目的
AR Quick LookをそのままARレンダリング基盤として使い、カニギターARカメラとしての撮影フローを検証する。

### 方針
- AR配置・移動・回転・拡縮・照明推定・落ち影はQuick Lookに任せる
- 写真撮影もQuick Look側の撮影機能を使用する
- Web側はAR起動前後の導線を担当する
- WebページからQuick Lookのシャッターを直接操作したり、撮影画像をJavaScriptで直接受け取ることは想定しない

### 実機確認項目
1. ページに `Beta v0.4.0` と表示される
2. 「ARカメラを起動」でQuick Lookが開く
3. カニギターを配置して構図を決められる
4. Quick Look内で写真を撮影できる
5. 撮影画像がiPhoneの「写真」アプリに保存される
6. ARを閉じるとWebページへ戻れる
7. 戻った後に撮影結果確認の案内が表示される


## Beta v0.4.2 診断結果

2026-10-03 / iPhone Safari

- iPhone再起動前: Quick LookのARタブがグレーアウト
- iPhone再起動後: Apple公式モデルのAR表示 OK
- iPhone再起動後: カニギターUSDZのAR表示 OK

結論:
- カニギターUSDZ自体は正常
- Web側のARリンクも正常
- 症状はiPhone側のQuick Look / ARセッションの一時的不調と判断
- 再発時の暫定対処: Safari終了 → 改善しなければiPhone再起動

## Beta v0.4.3

診断用Apple公式モデルボタンを削除し、カニギターARカメラの通常導線へ戻す。
ARタブがグレーアウトした場合の再起動案内をページ内に追加。


## Beta v0.4.3 撮影確認結果

2026-10-03 / iPhone Safari

- AR上でカニギターを配置: OK
- Quick Look内で写真撮影: OK
- 実写背景を含む写真保存: OK
- カニギターの質感・照明・落ち影: OK
- 撮影後にARへ戻ると背景がグレーになる場合あり

### 運用上の結論
Quick Lookは「1回のAR起動につき1枚撮影」として扱う。
撮影後はいったんARを閉じ、次の写真はWebページからARを再起動する。

## Beta v0.4.4

撮影フローを1ショット/1セッション前提に整理。
撮影後の案内を「写真確認 / 次の撮影はARを再起動」に変更。
