#!/usr/bin/env python3
"""Sinh trang series và bảy bài "Trích xuất nhìn là hiểu" cho xdev.asia.

    python3 build-ner-series.py

Mọi con số trong bài đọc từ ``ner-measured.json`` — đúng file mà các khung video đọc —
nên bài viết không thể lệch số khỏi video. Chạy lại sau khi có video id thì phần nhúng
video được điền; chưa có thì bỏ khối nhúng, không để link chết.

Id của series và từng bài suy ra bằng uuid5 từ slug, nên chạy lại không đổi id.
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VIDEOS = Path.home() / "Codes/make-1million-usd/videos"
NER_REPO = Path.home() / "Codes/ner-nhin-la-hieu"
M = json.loads((VIDEOS / "ner-measured.json").read_text())
C, E = M["corpus"], M["ep"]

NS = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")
uid = lambda s: str(uuid.uuid5(NS, s))                        # noqa: E731
pt = lambda v: f"{v * 100:.2f}".replace(".", ",")             # noqa: E731
pc = lambda v, n=2: f"{v * 100:.{n}f}".replace(".", ",") + "%"  # noqa: E731
num = lambda v: f"{v:,}".replace(",", " ")                    # noqa: E731

SERIES_SLUG = "trich-xuat-nhin-la-hieu"
REPO = "https://github.com/tdduydev/ner-nhin-la-hieu"
AUTHOR = ("019c9616-d2b4-713f-9b2c-40e2e92a05cf", "Duy Tran",
          "avatars/7e8eb5c6-4cac-455b-a701-4060f085d501.jpeg")
CATEGORY = ("019c9618-bb00-7000-b000-bb0000000001", "AI & Machine Learning", "ai-machine-learning")

# Khối cảnh báo dữ liệu tổng hợp — bắt buộc trên MỌI bài, không chỉ trang series.
SYNTHETIC = f"""> **Dữ liệu ở đây là tổng hợp.** Corpus {num(C['sentences'])} câu tiếng Việt sinh bằng mã, không
> phải corpus thật — môi trường dựng series không có mạng để tải corpus NER tiếng Việt. Các
> hiện tượng bài này đo là hệ quả của **cấu trúc** bài toán nên tái hiện đúng trên dữ liệu
> tổng hợp; nhưng **mức tuyệt đối không so được** với số công bố trên corpus thật, và series
> không so. Tên tổ chức trong dữ liệu là hư cấu."""

LESSONS = [
    dict(
        n=1, chapter=1, slug="bai-1-accuracy-93-ma-khong-lay-ra-duoc-gi",
        title=f"Bài 1: Accuracy {pc(E['01']['allOAccuracy'], 0)} mà không lấy ra được gì",
        desc=f"Mô hình trả O cho mọi token đạt {pc(E['01']['allOAccuracy'])}, và trích xuất được 0 thực thể.",
        minutes=14, script="ep01_accuracy",
        body=f"""
## Hai con số không mâu thuẫn nhau

Dựng một mô hình không học gì: nó trả lời `O` cho mọi token, không bao giờ đánh dấu thực
thể nào. Đo trên {C['test']} câu kiểm:

| | |
|---|---|
| Độ chính xác | **{pc(E['01']['allOAccuracy'])}** |
| Số thực thể lấy ra được | **0** |
| Token F1 | {E['01']['allOTokenF1']:.2f} |
| Span F1 | {E['01']['allOSpanF1']:.2f} |

Tập kiểm có {C['testSpans']['PER'] + C['testSpans']['ORG'] + C['testSpans']['LOC']} thực thể thật. Mô hình lấy ra 0. Và nó vẫn thắng ở cột đầu tiên.

## Vì sao: mẫu số là thứ ta không cần

Trong corpus, chỉ **{pc(C['entityTokenRate'])}** token là thực thể. {pc(C['oTokenRate'])} còn lại
là chữ nền, và trả lời `O` cho chữ nền thì luôn đúng.

Độ chính xác lấy mẫu số là **mọi token**. Nên nó bị chi phối gần như hoàn toàn bởi đúng phần
ta không quan tâm. Nó không tính sai — nó trả lời một câu hỏi khác câu ta hỏi.

## Trích xuất không phải phân loại

Phân loại có một câu hỏi và một đáp án. Trích xuất thì:

- số đáp án tuỳ từng câu — có câu không có thực thể nào, có câu có bốn;
- mỗi đáp án là một **đoạn**, phải đúng cả loại lẫn hai đầu biên.

Đầu ra không phải một nhãn cho cả câu, mà là một danh sách đoạn kèm vị trí.

## Token là âm tiết, và điều đó quan trọng

Tách theo khoảng trắng thì `Nguyễn Văn An` là **ba token** nhưng chỉ **một cái tên**.

Đoán đúng hai trong ba âm tiết: token đúng 2/3, nghe như gần đúng. Còn cái tên thì sai hẳn —
không có nửa cái tên. Tiếng Việt làm chuyện này gắt hơn tiếng Anh, nơi một tên riêng thường
là một token.

## Nhãn BIO

Cách gán nhãn phổ biến nhất:

- `B-X` — âm tiết **mở đầu** một thực thể loại X
- `I-X` — âm tiết **nằm trong** thực thể đó
- `O` — mọi thứ còn lại

Một chi tiết đáng nhớ: nhãn của một token phụ thuộc vào **cái nó đang nằm trong**. Trong
corpus này, token `Trang` là `I-LOC` khi nằm trong `Nha Trang`, và là `I-PER` khi nằm trong
`Ngô Ngọc Trang` — cùng một chữ, hai nhãn khác nhau, trong cùng một câu.

## Bốn độ đo, bốn câu hỏi

| Độ đo | Câu hỏi nó trả lời | Dùng khi nào |
|---|---|---|
| Accuracy | Bao nhiêu token đúng nhãn? | Gần như không bao giờ, ở bài toán này |
| Token F1 | Trong các token thực thể, đúng bao nhiêu? | Khi soi mô hình học được gì ở mức token |
| Span F1 | Có lấy đúng cả đoạn, đúng cả hai biên? | **Mặc định — con số để báo** |
| Câu đúng trọn | Cả câu này có dùng được không? | Khi đầu ra đi thẳng vào hệ thống khác |

Từ bài sau, mọi con số của series là span F1.
""",
    ),
    dict(
        n=2, chapter=1, slug="bai-2-token-dung-khong-co-nghia-la-span-dung",
        title="Bài 2: Token đúng không có nghĩa là span đúng",
        desc=f"{E['02']['tokenErrors']} token gán sai nhãn sinh ra {E['02']['wrongSpans']} đoạn sai. Một token sai làm hỏng cả đoạn.",
        minutes=16, script="ep02_token_vs_span",
        body=f"""
## Một mô hình thật, không phải mô hình rỗng

Naive Bayes trên bốn đặc trưng — chính từ đó, từ liền trước, từ liền sau, và từ có viết hoa
hay không — huấn luyện bằng đếm trên {num(C['train'])} câu. Cố tình giữ đơn giản: series này
đo *hiện tượng của bài toán*, không đi thi điểm cao, và một mô hình đơn giản làm chỗ sai lộ
ra rõ hơn.

| | |
|---|---|
| Accuracy token | **{pc(E['02']['tokenAccuracy'])}** |
| Token gán sai nhãn | {E['02']['tokenErrors']} / {num(C['testTokens'])} |
| Câu có ít nhất một đoạn sai | **{E['02']['sentencesWithError']} / {C['test']}** |

## Đếm đoạn thì ra chuyện khác

| | |
|---|---|
| Đoạn thật ở tập kiểm | {E['02']['goldSpansTest']} |
| Đoạn mô hình đoán ra | {E['02']['predSpans']} |
| Trùng khớp chính xác | **{E['02']['exactSpans']}** |
| Đoạn đoán sai | {E['02']['wrongSpans']} |
| Đoạn thật bị mất | {E['02']['missedSpans']} |

Chú ý số đoán ra **nhiều hơn** số thật. Không phải mô hình tham lam — mà {E['02']['goldSpansSplit']}
lần, một đoạn thật bị **cắt thành nhiều đoạn**. Một token bị gán `O` ở giữa một cái tên là đủ.

## Bốn kiểu sai, và bốn trong năm là lỗi biên

| Kiểu | Số lần | Nghĩa là |
|---|---|---|
| Lệch biên phải | {E['02']['errorKinds']['bienPhai']} | biên trái đúng, cắt sai ở cuối |
| Lệch biên trái | {E['02']['errorKinds']['bienTrai']} | biên phải đúng, bắt đầu sai chỗ |
| Lệch cả hai biên | {E['02']['errorKinds']['caHaiBien']} | trùng phần giữa, không trùng biên nào |
| Sai loại | {E['02']['errorKinds']['saiLoai']} | hai biên đúng, gọi tên loại sai |
| Không trùng gì | {E['02']['errorKinds']['khongTrungGi']} | dựng đoạn ở chỗ không có thực thể |

Loại thì mô hình gần như luôn đúng ({E['02']['errorKinds']['saiLoai']} lần sai). Chỗ nó gãy là
**đoạn bắt đầu và kết thúc ở đâu**.

## Một ca thật

Ca dưới đây là lỗi mô hình **thực sự mắc** trên tập kiểm, tìm bằng cách chạy mô hình chứ
không nghĩ ra:

```text
token   :  Mai      Đức      Khôi
nhãn thật: B-PER    I-PER    I-PER      → 1 đoạn: PER "Mai Đức Khôi"
mô hình  : B-PER    I-LOC    I-PER      → 3 đoạn: PER "Mai" · LOC "Đức" · PER "Khôi"
```

Token đúng **2/3**. Đoạn đúng **0**. Và không đoạn nào trong ba cái mô hình sinh ra trùng với
đoạn thật.

Đó là toàn bộ khoảng cách giữa hai cách đếm: {E['02']['tokenErrors']} lỗi token sinh ra
{E['02']['wrongSpans']} đoạn sai. Một token sai không làm hỏng một token — nó làm hỏng **cả đoạn
chứa nó**, và có khi dựng thêm một đoạn thứ hai không hề tồn tại.

## Con số nên báo cho người dùng

**{pc(E['02']['sentencesAllSpansExact'], 0)}** — tỉ lệ câu lấy đúng **trọn** mọi đoạn.
{E['02']['sentencesWithError']} câu còn lại cần người xem lại.

Độ chính xác token nói {pc(E['02']['tokenAccuracy'])}. Người vận hành hệ thống cảm nhận được
{pc(E['02']['sentencesAllSpansExact'], 0)}. Hai con số đó cùng đúng, và chỉ một cái trả lời câu
họ hỏi.
""",
    ),
    dict(
        n=3, chapter=1, slug="bai-3-mot-du-doan-hai-con-so-f1",
        title="Bài 3: Một dự đoán, hai con số F1",
        desc=f"Token F1 {pt(E['03']['tokenF1'])} và span F1 {pt(E['03']['spanF1'])} trên cùng một dự đoán. Khoảng cách lớn dần theo độ dài đoạn.",
        minutes=15, script="ep03_hai_f1",
        body=f"""
## Cùng một dự đoán, tính F1 hai lần

| | Precision | Recall | F1 |
|---|---|---|---|
| **Token** | {pt(E['03']['tokenPrecision'])} | {pt(E['03']['tokenRecall'])} | **{pt(E['03']['tokenF1'])}** |
| **Span** | {pt(E['03']['spanPrecision'])} | {pt(E['03']['spanRecall'])} | **{pt(E['03']['spanF1'])}** |

Cách nhau **{pt(E['03']['gap'])} điểm**. Không con số nào sai.

**Token F1** tính trên từng token nhưng bỏ nhãn `O` khỏi tử số — nếu không thì nó thành
accuracy của bài 1. **Span F1** khắt khe hơn nhiều: một đoạn chỉ tính là đúng khi trùng loại,
trùng token bắt đầu, **và** trùng token kết thúc.

## Khoảng cách đó phụ thuộc vào cái gì

Câu hỏi hay hơn "con số nào cao hơn" là: khoảng cách {pt(E['03']['gap'])} điểm ấy do đâu mà có.

Một đoạn dài ba token chỉ tính là đúng khi **cả ba** token đúng nhãn. Xác suất sai ở đâu đó
trong đoạn tăng theo độ dài. Nên đoạn càng dài, span F1 càng tụt xa token F1.

Đó là suy luận. Đây là số đo:

| Loại | Độ dài TB | Token F1 | Span F1 | Cách nhau |
|---|---|---|---|---|
| LOC (địa điểm) | {E['03']['byKind']['LOC']['avgLen']} token | {pt(E['03']['byKind']['LOC']['tokenF1'])} | {pt(E['03']['byKind']['LOC']['spanF1'])} | **{pt(E['03']['byKind']['LOC']['gap'])}** |
| PER (tên người) | {E['03']['byKind']['PER']['avgLen']} token | {pt(E['03']['byKind']['PER']['tokenF1'])} | {pt(E['03']['byKind']['PER']['spanF1'])} | **{pt(E['03']['byKind']['PER']['gap'])}** |
| ORG (tổ chức) | {E['03']['byKind']['ORG']['avgLen']} token | {pt(E['03']['byKind']['ORG']['tokenF1'])} | {pt(E['03']['byKind']['ORG']['spanF1'])} | **{pt(E['03']['byKind']['ORG']['gap'])}** |

Ba loại, ba độ dài, ba khoảng cách — và chúng xếp **đúng theo thứ tự độ dài**. Đây không phải
chuyện riêng của một loại thực thể nào; nó là hệ quả của việc đo theo đoạn.

## Một chi tiết đáng để ý

Ở mức đoạn, precision **{pt(E['03']['spanPrecision'])}** thấp hơn recall
**{pt(E['03']['spanRecall'])}**.

Nghĩa là mô hình dựng ra nhiều đoạn hơn số đoạn thật — {E['02']['predSpans']} so với
{E['02']['goldSpansTest']}. Nó không bỏ sót nhiều; nó **cắt vụn**. Hai kiểu hỏng đó cần hai cách
sửa khác nhau, và chỉ nhìn F1 gộp thì không phân biệt được.

## Báo số nào

Một quy tắc, không phải sở thích:

- Đầu ra vào **mắt người** → span F1.
- Đầu ra đi thẳng vào **hệ thống khác** → tỉ lệ câu đúng trọn.
- Token F1 → giữ trong nhà, dùng khi đang soi mô hình học được gì.
""",
    ),
    dict(
        n=4, chapter=2, slug="bai-4-tu-dien-manh-toi-dau-sap-o-dau",
        title="Bài 4: Từ điển mạnh tới đâu, sập ở đâu",
        desc=f"Precision {pt(E['04']['spanPrecision'])} nhưng recall {pt(E['04']['spanRecall'])}. Tập đóng thì từ điển ăn, tập mở thì sập.",
        minutes=15, script="ep04_tu_dien",
        body=f"""
## Cách xưa nhất, và nó không tệ

Bỏ mô hình học đi. Gom mọi chuỗi thực thể trong {num(C['train'])} câu huấn luyện thành một từ
điển {E['04']['dictEntries']} mục, rồi với câu mới thì quét từ trái và lấy **chuỗi khớp dài
nhất**.

| | Từ điển | Mô hình học (bài 3) |
|---|---|---|
| Span precision | **{pt(E['04']['spanPrecision'])}** | {pt(E['03']['spanPrecision'])} |
| Span recall | {pt(E['04']['spanRecall'])} | **{pt(E['03']['spanRecall'])}** |
| Span F1 | {pt(E['04']['spanF1'])} | {pt(E['03']['spanF1'])} |

Precision **cao hơn** mô hình học. Vấn đề của từ điển không phải đoán sai — mà là **không thấy**.

## Chỗ nó ăn và chỗ nó sập, đo theo loại

| Loại | Lấy đúng | Recall | Đoạn dựng sai |
|---|---|---|---|
| LOC — địa điểm | {E['04']['byKind']['LOC'][0]} / {E['04']['byKind']['LOC'][0] + E['04']['byKind']['LOC'][2]} | {pc(E['04']['byKind']['LOC'][0] / (E['04']['byKind']['LOC'][0] + E['04']['byKind']['LOC'][2]), 0)} | {E['04']['byKind']['LOC'][1]} |
| ORG — tổ chức | {E['04']['byKind']['ORG'][0]} / {E['04']['byKind']['ORG'][0] + E['04']['byKind']['ORG'][2]} | {pc(E['04']['byKind']['ORG'][0] / (E['04']['byKind']['ORG'][0] + E['04']['byKind']['ORG'][2]), 0)} | {E['04']['byKind']['ORG'][1]} |
| PER — tên người | {E['04']['byKind']['PER'][0]} / {E['04']['byKind']['PER'][0] + E['04']['byKind']['PER'][2]} | **{pc(E['04']['byKind']['PER'][0] / (E['04']['byKind']['PER'][0] + E['04']['byKind']['PER'][2]), 0)}** | {E['04']['byKind']['PER'][1]} |

Cùng một từ điển, cùng một tập kiểm, ba kết cục hoàn toàn khác nhau.

**Địa điểm và tổ chức là tập đóng.** Số tỉnh thành đếm được; số doanh nghiệp lớn cũng đếm được.
Một danh sách đủ tốt là gần như đủ.

**Tên người là tập mở.** Mỗi ngày có tên mới, và không danh sách nào đóng lại được. Thêm dữ
liệu huấn luyện đẩy vấn đề đi xa hơn một chút, không giải quyết nó.

Đo trực tiếp: **{pc(E['04']['unseenRate'])}** chuỗi thực thể ở tập kiểm chưa từng xuất hiện khi
huấn luyện — {E['04']['testSpansUnseen']} trên {E['04']['testSpansSeenInTrain'] + E['04']['testSpansUnseen']} đoạn.

## Chỗ sập thứ hai, tinh hơn

Một chuỗi có thể là hai loại tuỳ ngữ cảnh. Trong corpus này:

| Chuỗi | Là địa điểm | Là tên tổ chức |
|---|---|---|
""" + "\n".join(
            f"| {s} | {c.get('LOC', 0)} lần | {c.get('ORG', 0)} lần |"
            for s, c in sorted(E["04"]["ambiguous"])) + f"""

Từ điển **không có ngữ cảnh** nên buộc phải chọn một loại cho *mọi* lần xuất hiện, và nó chọn
cái gặp nhiều hơn. Hậu quả đo được: **{E['04']['byKind']['ORG'][2]} đoạn ORG** bị gọi thành LOC,
và LOC nhận thêm **{E['04']['byKind']['LOC'][1]} đoạn sai**.

Đó là giới hạn thật của từ điển: nó **tra chuỗi**, nó không đọc câu.

## Nhưng đừng bỏ từ điển

Nó vẫn là lựa chọn đúng khi:

- **danh mục đóng và cố định** — mã sản phẩm, tên tỉnh, mã sân bay: thêm mục là xong, không
  huấn luyện lại;
- **precision quan trọng hơn recall** — khớp thì gần như luôn đúng;
- **cần giải thích được** vì sao một cái tên được lấy ra, bằng một dòng trong bảng.

Trong hệ thống thật, từ điển thường **đứng cạnh** mô hình chứ không thay nó: từ điển giữ phần
chắc chắn, mô hình lo phần còn lại. Hai cách gãy khác nhau nên ghép lại thì bù cho nhau.
""",
    ),
    dict(
        n=5, chapter=2, slug="bai-5-chuoi-nhan-khong-the-ton-tai",
        title="Bài 5: Chuỗi nhãn không thể tồn tại",
        desc=f"{E['05']['invalidTransitions']} chỗ mô hình sinh ra chuỗi nhãn sai luật BIO, mà accuracy {pc(E['05']['tokenAccuracy'])} không thấy.",
        minutes=15, script="ep05_chuoi_bat_kha_thi",
        body=f"""
## Một loại lỗi mà không độ đo nào ở trên nhìn thấy

Accuracy token **{pc(E['05']['tokenAccuracy'])}**. Span F1 **{pt(E['05']['spanF1'])}**. Cả hai đều
không thấy chuyện này: **{E['05']['invalidTransitions']} chỗ** mà chuỗi nhãn mô hình sinh ra
không thể tồn tại.

## Luật BIO cấm những gì

`I-X` chỉ được đứng sau `B-X` hoặc `I-X` — **cùng loại**.

| | |
|---|---|
| Số nhãn | 7 (`O` + B/I cho ba loại) |
| Cặp viết ra được | {E['05']['allTransitions']} |
| Cặp hợp luật | {E['05']['legalTransitions']} |
| Cặp **bất khả thi** | **{E['05']['allTransitions'] - E['05']['legalTransitions']}** |

{E['05']['allTransitions'] - E['05']['legalTransitions']} cặp đó không xuất hiện trong dữ liệu gán nhãn — không phải vì ít gặp, mà vì
**không có nghĩa**. Và mô hình vẫn sinh ra chúng.

## Hai ca thật

```text
token :  Dương    Thư      rời      Tân      Hưng
đoán  :  B-PER    I-PER    I-ORG    B-ORG    I-ORG
thật  :  B-PER    I-PER    O        B-ORG    I-ORG
                           ▲ I-ORG ngay sau I-PER — không thể tồn tại
```

Mô hình gán **động từ `rời`** là phần bên trong một tên tổ chức, ngay sau một tên người.

```text
token :  đồng     quản     trị      Hồng     Lĩnh
đoán  :  O        O        I-ORG    B-ORG    I-ORG
thật  :  O        O        O        B-ORG    I-ORG
                           ▲ một đoạn bắt đầu bằng chữ I
```

## Đếm trên toàn tập kiểm

| Kiểu | Số chỗ |
|---|---|
| Đổi loại ngay giữa một đoạn | **{E['05']['wrongKind']}** |
| `I` mà không có `B` trước nó | {E['05']['oThenI']} |
| **Tổng** | **{E['05']['invalidTransitions']}** |

Và chúng không dồn vào vài câu: rải ra **{E['05']['sentencesWithInvalid']} / {C['test']}** câu, tức
{pc(E['05']['sentencesWithInvalid'] / C['test'], 1)} số câu kiểm chứa ít nhất một chuỗi nhãn không thể tồn tại.

## Vì sao mô hình làm được chuyện đó

Nó chọn nhãn cho **từng token một cách độc lập**: cho điểm mọi nhãn ở vị trí 1, lấy cao nhất;
sang vị trí 2, lấy cao nhất — không nhìn vị trí 1 đã chọn gì; lặp tới hết câu.

Không bước nào kiểm chuỗi kết quả có hợp luật hay không. Không có gì **ngăn** nó viết ra chuỗi
vô nghĩa, nên nó viết.

Đây không phải mô hình yếu. Đây là **cách giải mã** không có ràng buộc — và bài sau sửa đúng
chỗ đó mà không đụng gì tới mô hình.
""",
    ),
    dict(
        n=6, chapter=2, slug="bai-6-cung-mo-hinh-doi-cach-giai-ma",
        title="Bài 6: Cùng mô hình, đổi cách giải mã",
        desc=f"Không thêm đặc trưng, không thêm dữ liệu: span F1 tăng {pt(E['06']['spanF1Delta'])} điểm còn accuracy chỉ nhích {pt(E['06']['tokenAccuracyDelta'])}.",
        minutes=16, script="ep06_viterbi",
        body=f"""
## Đổi đúng một biến

Cùng mô hình cho điểm của bài trước. Không thêm đặc trưng, không thêm dữ liệu, không đổi tham
số. Chỉ đổi cách chọn nhãn.

| | Chọn từng token | Viterbi | Đổi |
|---|---|---|---|
| Chuỗi bất khả thi | {E['05']['invalidTransitions']} | **0** | −{E['05']['invalidTransitions']} |
| Accuracy token | {pc(E['06']['tokenAccuracyBefore'])} | {pc(E['06']['tokenAccuracy'])} | +{pt(E['06']['tokenAccuracyDelta'])} |
| Span F1 | {pt(E['06']['spanF1Before'])} | {pt(E['06']['spanF1'])} | **+{pt(E['06']['spanF1Delta'])}** |
| Câu đúng trọn | {pc(E['02']['sentencesAllSpansExact'], 0)} | {pc(E['06']['sentencesAllSpansExact'], 0)} | +{pt(E['06']['sentencesAllSpansExact'] - E['02']['sentencesAllSpansExact'])} |

Đọc theo hàng: accuracy gần như đứng yên, hai hàng dưới nhảy hẳn. Đó là dấu hiệu lỗi cũ là
**lỗi cấu trúc**, không phải lỗi nhận dạng.

Điểm quan trọng của thiết kế này: bài 5 và bài 6 dùng **chung một mô hình cho điểm**. Nên khi
span F1 nhảy {pt(E['06']['spanF1Delta'])} điểm, biến duy nhất đổi là cách giải mã.

## Viterbi làm gì

Cách cũ: mỗi vị trí quyết định một mình, lấy nhãn cao điểm nhất.

Viterbi: chọn **cả chuỗi nhãn** có tổng điểm cao nhất. Vẫn dùng đúng bộ điểm cũ, nhưng cộng
thêm điểm cho từng cặp nhãn liền nhau, và quyết định trên cả câu.

Chỗ then chốt: điểm của {E['05']['allTransitions'] - E['05']['legalTransitions']} cặp bất khả thi được đặt bằng **âm vô cùng**.

Khác biệt giữa *phạt nặng* và *loại hẳn* là thật:

- **Phạt nặng** — vẫn có thể xảy ra nếu bộ điểm đủ tự tin, chỉ là ít gặp hơn.
- **Loại hẳn** — không bao giờ xảy ra. Viterbi *không thể* trả về chuỗi sai luật.

Đó là lý do con số bất khả thi về **đúng 0**, chứ không phải "giảm nhiều".

## Hai ca của bài trước, giải mã lại

```text
token   :  Dương    Thư      rời      Tân      Hưng
bài 5   :  B-PER    I-PER    I-ORG    B-ORG    I-ORG   ← sai luật
Viterbi :  B-PER    I-PER    O        B-ORG    I-ORG   ← trùng nhãn thật
```

Viterbi không đoán giỏi hơn ở token `rời`. Nó chỉ **không được phép** chọn `I-ORG` ở đó, nên
buộc phải lấy phương án hợp luật tốt nhất — và phương án đó trùng nhãn thật.

## Ai hưởng lợi nhiều nhất

| Loại | Lấy đúng | Recall |
|---|---|---|
| PER — tên người | {E['06']['byKind']['PER'][0]} / {E['06']['byKind']['PER'][0] + E['06']['byKind']['PER'][2]} | **{pc(E['06']['byKind']['PER'][0] / (E['06']['byKind']['PER'][0] + E['06']['byKind']['PER'][2]), 0)}** |
| ORG — tổ chức | {E['06']['byKind']['ORG'][0]} / {E['06']['byKind']['ORG'][0] + E['06']['byKind']['ORG'][2]} | {pc(E['06']['byKind']['ORG'][0] / (E['06']['byKind']['ORG'][0] + E['06']['byKind']['ORG'][2]), 0)} |
| LOC — địa điểm | {E['06']['byKind']['LOC'][0]} / {E['06']['byKind']['LOC'][0] + E['06']['byKind']['LOC'][2]} | {pc(E['06']['byKind']['LOC'][0] / (E['06']['byKind']['LOC'][0] + E['06']['byKind']['LOC'][2]), 0)} |

Tên người có đoạn dài nhất nên chịu thiệt nhiều nhất khi giải mã rời rạc — và cũng hưởng lợi
nhiều nhất khi thêm ràng buộc chuỗi.

## Nói rõ giới hạn

Mức **{pt(E['06']['spanF1'])}** là hệ quả của corpus sinh bằng mã, văn phạm khá cứng. **Đừng mang
con số đó đi so với corpus thật.**

Thứ mang đi được là **khoảng cách**: cùng một mô hình, cùng một dữ liệu, đổi cách giải mã thì
span F1 chênh {pt(E['06']['spanF1Delta'])} điểm. Một con số không kèm điều kiện đo là một con số
không dùng được.
""",
    ),
    dict(
        n=7, chapter=3, slug="bai-7-cho-bio-sap-va-cho-hai-nguoi-khong-dong-y",
        title="Bài 7: Chỗ BIO sập, và chỗ hai người không đồng ý",
        desc=f"Cùng một dự đoán: span F1 {pt(E['07']['modelSpanF1VsA'])} với người gán nhãn này, {pt(E['07']['modelSpanF1VsB'])} với người kia.",
        minutes=17, script="ep07_tran_cua_mo_hinh",
        body=f"""
## Con số của bài trước, đo lại

Bài 6 kết thúc ở span F1 **{pt(E['07']['modelSpanF1VsA'])}**. Đây là **cùng dự đoán đó**, không đổi
một chữ nào trong mô hình, đo với nhãn chuẩn của một người gán nhãn khác:
**{pt(E['07']['modelSpanF1VsB'])}**.

Giảm **{pt(E['07']['modelDropIfOtherAnnotator'])} điểm**. Mô hình không đổi. Dữ liệu huấn luyện
không đổi. Cách giải mã không đổi. Chỉ có **định nghĩa của câu trả lời đúng** là khác.

Phần còn lại của bài giải thích vì sao.

## Chuyện thứ nhất: entity lồng nhau

`Kỹ thuật Hải Phòng` là một tên tổ chức. Nhưng `Hải Phòng` bên trong nó cũng là một địa điểm
thật, và người dùng hoàn toàn có thể cần nó.

BIO phẳng cho mỗi token **đúng một nhãn**, nên nó chỉ giữ được **một tầng**.

| | |
|---|---|
| Đoạn giữ được (tầng ngoài) | {E['07']['testSpansTotal']} |
| Địa điểm nằm trong tên tổ chức, bị bỏ hẳn | **{E['07']['nestedLocInsideOrg']}** ({pc(E['07']['nestedLostRate'])}) |

Chúng không bị đoán sai. **Chúng không có chỗ để tồn tại** trong cách gán nhãn này — nên không
độ đo nào của sáu bài trước nhìn thấy chúng.

## Chuyện thứ hai không nằm ở mô hình

Chuỗi `Tập đoàn Thiên Phú`:

```text
token    :  Tập      đoàn     Thiên    Phú
người A  :  B-ORG    I-ORG    I-ORG    I-ORG    → "Tập đoàn Thiên Phú" (4 token)
người B  :  O        O        B-ORG    I-ORG    → "Thiên Phú" (2 token)
```

Người A tính cả tiền tố loại hình vào tên tổ chức. Người B chỉ lấy phần lõi. **Cả hai quy ước
đều dùng được**, và cả hai đều có tài liệu hướng dẫn thật làm theo.

Với span F1 khớp chính xác, hai đoạn này **không trùng nhau**.

## Đo mức bất đồng — và vì sao phải báo kappa

| | |
|---|---|
| Đoạn ORG gán khác nhau | {E['07']['orgSpansRelabelled']} / {C['testSpans']['ORG']} |
| Tỉ lệ đồng ý mức token | {pc(E['07']['annotatorAgreement'])} |
| **Cohen's kappa** | **{pt(E['07']['annotatorKappa'])}** |
| **Span F1 giữa hai người** | **{pt(E['07']['spanF1BetweenAnnotators'])}** |

Ở dữ liệu NER, nhãn `O` chiếm đa số nên phần trùng do ngẫu nhiên rất lớn. Đó là lý do tỉ lệ
đồng ý {pc(E['07']['annotatorAgreement'], 1)} và kappa {pt(E['07']['annotatorKappa'])} là hai con số
rất khác nhau — và **kappa mới là con số nên báo**.

Còn ở mức đoạn, thứ người dùng thật sự nhận: hai người, không ai sai, chỉ trùng nhau
**{pt(E['07']['spanF1BetweenAnnotators'])}**.

## Trần của mô hình không phải 100

Nó là **mức đồng thuận giữa những người gán nhãn**. Vượt qua mức đó thì con số không còn nghĩa
gì, vì không còn một đáp án đúng để vượt.

Điều này có ba hệ quả thực dụng:

1. **Trước khi tối ưu mô hình, đo mức đồng thuận của người.** Nếu kappa là
   {pt(E['07']['annotatorKappa'])}, đừng đặt mục tiêu span F1 95.
2. **Tài liệu hướng dẫn gán nhãn quan trọng hơn kiến trúc mô hình** ở giai đoạn đầu. Một quy
   ước rõ ràng, viết ra, có ví dụ biên — đó là thứ nâng trần.
3. **Số công bố phải kèm quy ước gán nhãn.** So span F1 của hai hệ thống gán nhãn theo hai quy
   ước khác nhau là so hai thứ khác nhau.

## Bảy bài, bảy con số

| Bài | Con số | Nó nói gì |
|---|---|---|
| 1 | {pc(E['01']['allOAccuracy'])} | Mô hình trả `O` cho mọi token, lấy ra 0 thực thể |
| 2 | {E['02']['tokenErrors']} → {E['02']['wrongSpans']} | Token sai, và số đoạn sai chúng gây ra |
| 3 | {pt(E['03']['gap'])} điểm | Khoảng cách token F1 / span F1, lớn dần theo độ dài đoạn |
| 4 | {pc(E['04']['unseenRate'])} | Chuỗi ở tập kiểm chưa từng gặp — chỗ từ điển sập |
| 5 | {E['05']['invalidTransitions']} | Chuỗi nhãn không thể tồn tại, mà accuracy không thấy |
| 6 | +{pt(E['06']['spanF1Delta'])} | Đổi cách giải mã, không thêm gì vào mô hình |
| 7 | {pt(E['07']['modelSpanF1VsA'])} → {pt(E['07']['modelSpanF1VsB'])} | Cùng dự đoán, đổi người gán nhãn chuẩn |

Mọi con số ở đây đo lại được bằng một lệnh.

## Còn thiếu: so với gọi LLM

Series này không có bài đo việc gọi LLM với schema, vì môi trường dựng không có mạng và không
có khoá API — và bịa số ở đây là phá đúng cái làm nên series.

Nếu bạn có khoá, phần khung để tự đo nằm sẵn trong repo: cùng tập kiểm, cùng span F1, và nhớ
đo thêm chi phí mỗi 1 000 văn bản. Chỗ nào là số đo được, chỗ nào còn trống — bài này ghi rõ.
""",
    ),
]

CHAPTERS = [
    (1, "Phần 1: Đo cho đúng", "Ba bài về việc chọn độ đo — phần quyết định mọi thứ sau đó có nghĩa hay không."),
    (2, "Phần 2: Hai cách làm, hai cách gãy", "Từ điển, mô hình học, và chỗ mỗi cái sập."),
    (3, "Phần 3: Chỗ không sửa được bằng mô hình", "Giới hạn của cách gán nhãn, và trần do người đặt ra."),
]


VN = str.maketrans(
    "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ",
    "aaaaaaaaaaaaaaaaaeeeeeeeeeeeiiiiiooooooooooooooooouuuuuuuuuuuyyyyyd")


def slugify(text: str) -> str:
    """Bỏ dấu, bỏ mọi dấu câu, gộp gạch nối. Bản đầu chỉ thay khoảng trắng nên dấu phẩy
    của "hai cách làm, hai cách gãy" lọt vào tên thư mục."""
    ascii_text = text.lower().translate(VN)
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", ascii_text)).strip("-")


def yaml_escape(text: str) -> str:
    return text.replace("'", "''")


def video_block(video_id: str | None, title: str, minutes: int) -> str:
    if not video_id:
        return ""
    return f"""## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#0B1020;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/{video_id}"
    title="{title}"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

Bài viết dưới đây đi sâu hơn bản video và có code chạy được.

"""


def video_id_of(number: int) -> str | None:
    slugs = {
        1: "ner-16x9-01-accuracy", 2: "ner-16x9-02-token-vs-span", 3: "ner-16x9-03-hai-f1",
        4: "ner-16x9-04-tu-dien", 5: "ner-16x9-05-chuoi-bat-kha-thi",
        6: "ner-16x9-06-viterbi", 7: "ner-16x9-07-bio-sap",
    }
    path = VIDEOS / slugs[number] / "social/publish.json"
    if not path.exists():
        return None
    return json.loads(path.read_text()).get("youtube", {}).get("videoId")


def main() -> None:
    base = ROOT / "content/series/ai" / SERIES_SLUG
    images = ROOT / "public/images/blog" / SERIES_SLUG
    images.mkdir(parents=True, exist_ok=True)
    for png in (NER_REPO / ".out/png").glob("*.png"):
        shutil.copy2(png, images / png.name)

    written = 0
    for lesson in LESSONS:
        chapter_index, chapter_title, _ = next(c for c in CHAPTERS if c[0] == lesson["chapter"])
        chapter_slug = f"{chapter_index:02d}-{slugify(chapter_title)}"
        lesson_dir = base / "chapters" / chapter_slug / "lessons"
        lesson_dir.mkdir(parents=True, exist_ok=True)

        vid = video_id_of(lesson["n"])
        front = f"""---
id: {uid(lesson['slug'])}
title: '{yaml_escape(lesson['title'])}'
slug: {lesson['slug']}
description: >-
  {lesson['desc']}
duration_minutes: {lesson['minutes']}
is_free: true
{f'video_url: https://youtu.be/{vid}' if vid else '# video_url: chưa đăng'}
sort_order: {lesson['n'] - 1}
section_title: '{yaml_escape(chapter_title)}'
course:
  id: {uid(SERIES_SLUG)}
  title: 'Trích xuất nhìn là hiểu'
  slug: {SERIES_SLUG}
---

"""
        tail = f"""
## Chạy lại mọi con số

Repo Python thuần, không phụ thuộc ngoài, không cần cài gì:

```bash
git clone {REPO}
cd ner-nhin-la-hieu
python3 scratch/{lesson['script']}.py
```

![Kết quả chạy {lesson['script']}](/images/blog/{SERIES_SLUG}/{lesson['script']}.png)

Toàn bộ số của bảy bài: `python3 measure.py`. Khẳng định số không đổi: `python3 run_tests.py`.

{SYNTHETIC}
"""
        (lesson_dir / f"{lesson['n']:02d}-{lesson['slug']}.md").write_text(
            front + video_block(vid, lesson["title"], lesson["minutes"])
            + lesson["body"].strip() + "\n" + tail, encoding="utf8")
        written += 1

    sections = []
    for index, title, desc in CHAPTERS:
        items = [l for l in LESSONS if l["chapter"] == index]
        # PHẢI bọc nháy đơn cho description: trong dạng flow, dấu phẩy của số thập phân
        # tiếng Việt ("span F1 85,97") bị YAML hiểu là dấu ngăn mục, và build đổ với
        # "missed comma between flow collection entries".
        lessons_yaml = ", ".join(
            "{" + f"id: {uid(l['slug'])}, title: '{yaml_escape(l['title'])}', slug: {l['slug']}, "
            f"description: '{yaml_escape(l['desc'])}', duration_minutes: {l['minutes']}, is_free: true, "
            f"sort_order: {i}" + (f", video_url: https://youtu.be/{video_id_of(l['n'])}" if video_id_of(l["n"]) else "") + "}"
            for i, l in enumerate(items))
        sections.append("{" + f"id: section-{index:02d}, title: '{yaml_escape(title)}', "
                        f"description: '{yaml_escape(desc)}', sort_order: {index}, "
                        f"lessons: [{lessons_yaml}]" + "}")

    index_md = f"""---
id: {uid(SERIES_SLUG)}
title: 'Trích xuất nhìn là hiểu'
slug: {SERIES_SLUG}
description: >-
  Bảy bài về trích xuất thông tin từ văn bản tiếng Việt, NER là ca cụ thể. Mỗi bài một chỗ
  "tưởng đúng mà sai", và mọi con số đều đo được — kèm repo Python thuần chạy lại được từng
  con số xuất hiện trong video.
featured_image: images/blog/{SERIES_SLUG}/ep07_tran_cua_mo_hinh.png
level: intermediate
duration_hours: 2
lesson_count: {len(LESSONS)}
price: '0.00'
is_free: true
view_count: 0
average_rating: '0.00'
review_count: 0
enrollment_count: 0
meta: null
published_at: '2026-08-08T02:00:00.000000Z'
created_at: '2026-08-08T02:00:00.000000Z'
author: {{id: {AUTHOR[0]}, name: {AUTHOR[1]}, avatar: {AUTHOR[2]}}}
category: {{id: {CATEGORY[0]}, name: {CATEGORY[1]}, slug: {CATEGORY[2]}}}
tags: [{{name: NER, slug: ner}}, {{name: NLP, slug: nlp}}, {{name: trích xuất thông tin, slug: trich-xuat-thong-tin}}, {{name: tiếng Việt, slug: tieng-viet}}, {{name: Python, slug: python}}, {{name: span F1, slug: span-f1}}, {{name: BIO tagging, slug: bio-tagging}}, {{name: Viterbi, slug: viterbi}}, {{name: gán nhãn dữ liệu, slug: gan-nhan-du-lieu}}]
sections: [{", ".join(sections)}]
---

## Series này khác gì

Phần lớn tài liệu về NER bắt đầu bằng kiến trúc mô hình. Series này bắt đầu bằng **cách đo** —
vì ở bài toán trích xuất, chọn sai độ đo thì mọi thứ sau đó vô nghĩa.

Bài 1 dựng một mô hình không học gì và cho nó đạt **{pc(E['01']['allOAccuracy'])}** độ chính xác
trong khi lấy ra **0** thực thể. Bài cuối cho thấy con số **{pt(E['07']['modelSpanF1VsA'])}** của
một mô hình tốt tụt xuống **{pt(E['07']['modelSpanF1VsB'])}** chỉ vì đổi người viết nhãn chuẩn.

Ở giữa là năm bài về những chỗ bài toán này gãy: span so với token, từ điển so với mô hình học,
chuỗi nhãn không thể tồn tại, và cách sửa nó mà không cần mô hình to hơn.

## Mọi con số đều đo được

Repo kèm theo là **Python thuần, không phụ thuộc ngoài**. `python3 measure.py` in ra toàn bộ
bảng số của bảy bài trong dưới một giây, và `python3 run_tests.py` khẳng định chúng không đổi.

Con số trên khung video và con số trong bài viết đọc từ **cùng một file** do `measure.py` xuất
ra — nên chúng không thể lệch nhau.

## Về dữ liệu

{SYNTHETIC}

Bản đầu của corpus phải dựng lại: entity chiếm 48% token (corpus thật 2–5%) và mô hình đạt
điểm **1.0 tuyệt đối** ở mọi độ đo. Điểm tuyệt đối không phải tin tốt — nó là dấu hiệu dữ liệu
rò đáp án qua ngữ cảnh. Bản dùng thật cố ý có bốn thứ: chữ nền chiếm đa số, tên chưa từng gặp
ở tập kiểm, chuỗi vừa là địa điểm vừa là tên tổ chức, và bẫy viết hoa không phải thực thể.

## Bạn sẽ học được gì

- Chọn độ đo theo câu hỏi người dùng hỏi, không theo cái dễ tính
- Đọc khoảng cách giữa token F1 và span F1, và biết nó đến từ đâu
- Biết khi nào từ điển là lựa chọn đúng, và khi nào nó chắc chắn sập
- Phát hiện lỗi cấu trúc mà accuracy và F1 đều không thấy
- Sửa lỗi đó bằng cách giải mã, không bằng mô hình to hơn
- Đặt mục tiêu theo mức đồng thuận của người gán nhãn, không theo 100
"""
    base.mkdir(parents=True, exist_ok=True)
    (base / "index.md").write_text(index_md, encoding="utf8")
    print(f"{written} bài + index.md · ảnh terminal chép vào public/images/blog/{SERIES_SLUG}/")
    for lesson in LESSONS:
        vid = video_id_of(lesson["n"])
        print(f"  bài {lesson['n']}  {'video ' + vid if vid else 'CHƯA có video id'}")


if __name__ == "__main__":
    main()
