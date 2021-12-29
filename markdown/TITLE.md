# まえがき {-}

## このドキュメントは何 {-}

この本は、Dialog Semiconductor社GreenPAKシリーズSLG46826Gを使ったI2C汎用出力（GPO）エキスパンダを設計したのち、
2行（row）・6列（column）のリレーマトリクスが載ったラズパイの拡張ボード（HAT）に実装するまでをまとめたドキュメントです。

# GreenPAKでGPOエクスパンダを設計する話

## 設計概要

GreenPAK SLG46826を用いて、6ビット幅2ポートの汎用出力（GPO）エクスパンダを設計しました。
6ビット幅を選んだのは、GPAKのI2Cスレーブ機能や後述するHATのボードサイズからくる制限もありますが、
ソフト設計が比較的楽だからです。

![設計概観](images/ioexpander-12bit.svg){.svg width=150mm #fig:design-overview}

## ピン割当て一覧

電源とI2CのSCL/SDAピン以外にはIO4とIO5のピンをI2Cスレーブアドレスの選択に使い、残り13のうち12本ををすべて
汎用出力ピンに使います(未使用ピンが一つあります)。SLG46826はパッケージでピン配置が逆順なので注意してください。
ポート０は電源レベルが混在しますが、ポート１はすべてVDD2レベルで出力します。ポート０をVDDレベルに統一する
こともできますが、I2Cアドレスが固定になってしまうデメリットがあります。

::: {.table width=[0.1,0.2,0.2,0.1,0.4]}
Table: ピン割当て {#tbl:pin-assignment}

| ピン名 | ピン番号(TSSOP) | ピン番号(QFN) | 電源 | 機能割当て         |
|:------:|:---------------:|:-------------:|:----:|:-------------------|
|  VDD   |       20        |       1       | VDD  | VDD                |
|  IO0   |       19        |       2       | VDD  | Port0 bit0         |
|  IO1   |       18        |       3       | VDD  | Port0 bit1         |
|  IO2   |       17        |       4       | VDD  | Port0 bit2         |
|  IO3   |       16        |       5       | VDD  | Port0 bit3         |
|  IO4   |       15        |       6       | VDD  | SLA_2 (bit6)       |
|  IO5   |       14        |       7       | VDD  | SLA_3 (bit7)       |
|  SCL   |       13        |       8       | VDD  | I2C SDL            |
|  SDA   |       12        |       9       | VDD  | I2C SDA            |
|  IO6   |       11        |      10       | VDD  | Unused; leave open |
|  GND   |       10        |      11       | GND  | GND                |
|  IO7   |        9        |      12       | VDD2 | Port0 bit4         |
|  IO8   |        8        |      13       | VDD2 | Port0 bit5         |
|  VDD2  |        7        |      14       | VDD2 | VDD2               |
|  IO9   |        6        |      15       | VDD2 | Port1 bit5         |
|  IO10  |        5        |      16       | VDD2 | Port1 bit4         |
|  IO11  |        4        |      17       | VDD2 | Port1 bit3         |
|  IO12  |        3        |      18       | VDD2 | Port1 bit2         |
|  IO13  |        2        |      19       | VDD2 | Port1 bit1         |
|  IO14  |        1        |      20       | VDD2 | Port1 bit0         |

:::

\newpage

## スレーブアドレス空間

SLG46826は１チップあたり、NVM/EEPROMで１つずつ、レジスタで２つの合計４スレーブアドレスを専有します。
今回の設計では８ビット中MSB２ビットを選択できるようにしてあります。つまり１つのI2Cバスに４個まで繋げられます。
５個以上欲しくなったときはバスマルチプレクサなどを使ってください。

::: {.table width=[0.1,0.1,0.3,0.3]}
Table: スレーブアドレスの設定 {#tbl:slave-address}

| SLA_3 | SLA_2 | *7-bit* Addresses                 | *8-bit* Addresses                 |
|:-----:|:-----:|:----------------------------------|:----------------------------------|
|   0   |   0   | **`0x08`** (`0x09`/`0x0a`/`0x0b`) | **`0x10`** (`0x12`/`0x14`/`0x16`) |
|   0   |   1   | **`0x28`** (`0x29`/`0x2a`/`0x2b`) | **`0x50`** (`0x52`/`0x54`/`0x56`) |
|   1   |   0   | **`0x48`** (`0x49`/`0x4a`/`0x4b`) | **`0x90`** (`0x92`/`0x94`/`0x96`) |
|   1   |   1   | **`0x68`** (`0x69`/`0x6a`/`0x6b`) | **`0xD0`** (`0xD2`/`0xD4`/`0xD6`) |

:::

## 各ポートへのアクセス方法

このICの操作に必要なレジスタは`0x76`/`0x79`/`0x7A`の３箇所だけです。`0x7A`は書き込み専用、残り２つは読み込み専用
レジスタになっています（[@tbl:registers]）。

::: {.table width=[0.075,0.05,0.125,0.35,0.4]}

Table: レジスタ一覧 {#tbl:registers}

| register | R/W | bit        | purpose         | Datasheet                     |
|:--------:|:---:|:-----------|:----------------|:------------------------------|
|  `0x76`  |  R  | 0 (LSB)    | reserved        | LUT2_2_DFF2_OUT               |
|          |     | 1          | reserved        | LUT2_3_PGEN_OUT               |
|          |     | 2          | read Port0 bit0 | LUT3_0_DFF3_OUT               |
|          |     | 3          | read Port0 bit1 | LUT3_1_DFF4_OUT               |
|          |     | 4          | read Port0 bit2 | LUT3_2_DFF5_OUT               |
|          |     | 5          | read Port0 bit3 | LUT3_3_DFF6_OUT               |
|          |     | 6          | read Port0 bit4 | LUT3_4_DFF7_OUT               |
|          |     | 7 (MSB)    | read Port0 bit5 | LUT3_5_DFF8_OUT               |
|  `0x79`  |  R  | 0 (LSB)    | read Port1 bit0 | MULTFUNC_8BIT_1: LUT_DFF_OUT  |
|          |     | 1          | read Port1 bit1 | MULTFUNC_8BIT_2: LUT_DFF_OUT  |
|          |     | 2          | read Port1 bit2 | MULTFUNC_8BIT_3: LUT_DFF_OUT  |
|          |     | 3          | read Port1 bit3 | MULTFUNC_8BIT_4: LUT_DFF_OUT  |
|          |     | 4          | read Port1 bit4 | MULTFUNC_8BIT_5: LUT_DFF_OUT  |
|          |     | 5          | read Port1 bit5 | MULTFUNC_8BIT_6: LUT_DFF_OUT  |
|          |     | 6          | reserved        | MULTFUNC_8BIT_7: LUT_DFF_OUT  |
|          |     | 7 (MSB)    | reserved        | MULTFUNC_16BIT_0: DLY_CNT_OUT |
|  `0x7A`  |  W  | 0 (LSB)    | write bit0      |                               |
|          |     | 1          | write bit1      |                               |
|          |     | 2          | write bit2      |                               |
|          |     | 3          | write bit3      |                               |
|          |     | 4          | write bit4      |                               |
|          |     | 5          | write bit5      |                               |
|          |     | 7..6 (MSB) | port selection  |                               |
|          |     |            | `00` : P0       |                               |
|          |     |            | `01` : P1       |                               |
|          |     |            | `1x` : reserved |                               |

:::

### DFFのクロック生成

各ポートの出力は0x7Aのビット5〜0に書き込みます。ビット6/7はポートの選択に使います。
このビット6/7が`1x`から`00`または`01`に変化するときに2ビットLUTの出力が１から０に変化し、
下りエッジ検出器がDFFのクロックを生成します。
同じポートに連続して書き込みたいときは一旦ビット7/6に`1x`を書き込む必要があります。
つまり、以下のような手順で書き込みます[^repeated-start-failed]：

1. `8'b11XX_XXXX` をレジスタ`0x7A`に書き込む。 `XX_XXXX` は影響を与えない。
   * `| S | AAAA_AAAW | 0111_1010 (0x7A) | 11XX_XXXX | P |`
2. `8'bPPDD_DDDD` をレジスタ`0x7A`に書き込む。ここで`PP`は`00`または`01`で、`DD_DDDD`は書き込みたいデータ
   * `| S | AAAA_AAAW | 0111_1010 (0x7A) | PPDD_DDDD | P |`

または、リピートスタートを使いこれらの書き込みを一度に行います。

* `| S | AAAA_AAAW | 0111_1010 | 11XX_XXXX | Sr | AAAA_AAAW | 0111_1010 | PPDD_DDDD | P |`

# 設計したGPOエクスパンダを使ってラズパイHATを作る話

GPOエクスパンダの設計情報を書き込んだSLG46826にリレーをつなげて２行６列のマトリクス状に配線した、
ラズベリーパイ（ラズパイ）の拡張基板（HAT）を作ります。ブロック図を[@fig:hat-block-diagram]に示します。
各列のコネクタに計測対象、各行のコネクタに計測器類をつなぐ状況を想定しています。
この図では(1,1)と(2,6)のスイッチがオンになっています。

[作ったHATのブロック図](data/matrix-2x6.bob){.svgbob #fig:hat-block-diagram}

## ポート・ピン割当表

::: {.table #tbl:muxhat-pin-assignment}

| &darr;ROW \ COL&rarr; |  1  |  2  |  3  |  4  |  5  |  6  |
|:---------------------:|:---:|:---:|:---:|:---:|:---:|:---:|
|           1           |     |     |     |     |     |     |
|           2           |     |     |     |     |     |     |

:::



::: LANDSCAPE
## 部品表

[部品表](data/2x6muxhat-bom.csv){.table width=[0.1,0.3,0.2,0.1,0.3]}

次ページより、基板の設計図を示します。

## 回路図

![回路図](images/2x6muxhat.pdf){width=120%}

## 配置図

![シルク図](images/2x6muxhat-silk.pdf){width=120%}

:::

## ソフト設計例

以下にPythonの動作確認済のサンプルコードを示します。I2Cアクセスには[SMBus2](https://pypi.org/project/smbus2/)ライブラリ
を使っています。

::: LANDSCAPE

[サンプルコード](data/ioexpander_12bit.py){.listingtable type=python #lst:sample-sourcecode}

:::

::: rmnote

# 改造・拡張アイデア（未テスト）

::: {.table width=[1.1] noheader=true}

+:--------------------------------------------------:+
|**\Large ここに書かれていることはアイデアのみで、\  |
| まったく未テストです。**                           |
+----------------------------------------------------+

:::

\pagebreak

## 電源レールをポートで分けつつ７ビット幅２ポートに拡張する

SLG46826は２電源タイプのGreenPAKなので、異なる電源レール（VDD・VDD2；5Vと3.3Vなど）を使用することができます。
一方、この本の設計では、I2Cアドレスを可変にするため、単一電源レール（VDD = VDD2にしなければならない）
仕様になっています。以下にこの拡張のメリット・デメリットを書いていきます。

### （+）ピン配置がきれい

この改造でピン配置がシンプルになります。もとからSLG46826のピン配置はシンプルで、
電源レールで左右に分かれている感じですが、そのまま同一の電源レールに属するピンが同じポートに並びます。

### （+）GPI１ポート + GPO１ポートにもできる

VDDレールのピンは入出力モードを切り替えられないのですが、VDD2レールのピンはOEピンで
設定が可能です。

*  （-）I2Cアドレス空間を失う
*  （-）ソフトが更にトリッキーになる

## 別の品種を使って8ビット**GPIO**エキスパンダ

:::

# あとがき {-}

- タルコフのワイプとかいう超強力妨害電波によって今回も前日印刷です！
- 原稿PDFはこのQRコードからたどってください ![](images/QRcode.png){#fig:manuscript width=20mm}
