#!/usr/bin/env python3
"""Sinh series ".NET 10 × SQL Server — chuyện dịch" trên xdev.asia.

    python3 build-net-series.py

Hai bài, mỗi bài ứng với một tập video. Video id đọc từ net-video-ids.json nếu có —
cùng nguồn với social/publish.json bên repo dựng video, nên bài viết và mô tả YouTube
không thể trỏ lệch nhau. Chưa có file đó thì bài vẫn sinh, chỉ thiếu khối nhúng video.

Không dùng str.format cho phần thân bài: thân bài đầy dấu ngoặc nhọn của C# và JSON,
format() sẽ nổ KeyError ngay dòng đầu tiên. Thay bằng replace theo đúng khoá cần.
"""
import json
import os
import uuid
from pathlib import Path

ROOT = Path(__file__).parent
SERIES_SLUG = "dotnet-10-sql-server-chuyen-dich"
SERIES_TITLE = ".NET 10 × SQL Server — chuyện dịch"
CATEGORY = "lap-trinh"
NS = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")

ids_path = ROOT / "net-video-ids.json"
VIDEO = json.loads(ids_path.read_text(encoding="utf8")) if ids_path.exists() else {}

SRC = {
    "whatsnew": "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew",
    "breaking": "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes",
    "howquery": "https://learn.microsoft.com/en-us/ef/core/querying/how-query-works",
    "collation": "https://learn.microsoft.com/en-us/ef/core/miscellaneous/collations-and-case-sensitivity",
    "sqlcollation": "https://learn.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support",
}

LESSONS = [
    {
        "n": 1,
        "slug": "linq-di-xuong-sql-server",
        "title": "Bài 1: LINQ đi xuống SQL Server bằng đường nào",
        "description": "EF không gửi LINQ xuống database. Nó dịch — và bản dịch đó quyết định SQL Server có tái dùng được kế hoạch thực thi hay không.",
        "minutes": 13,
        "body": """## Xem bản video

{VIDEO_1}

## Thứ đi xuống dây không phải LINQ

Database không biết LINQ là gì. Thứ duy nhất đi xuống là một chuỗi T-SQL và một mớ tham số.
Đường đi của một câu truy vấn, theo [tài liệu EF Core]({howquery}):

1. Câu LINQ được xử lý thành một dạng biểu diễn sẵn sàng cho provider — **và kết quả đó được cache lại**, để lần sau không phải dịch lại.
2. Provider quyết định phần nào chạy được dưới database, dịch phần đó sang SQL, gửi đi, nhận về **result set thô** — là giá trị, chưa phải entity.
3. EF nặn giá trị thành object; nếu là truy vấn có theo dõi thì gắn vào change tracker.

Chặng số 2 là chỗ cả bài này xoay quanh.

Một chi tiết hay bị bỏ qua: **viết xong câu LINQ thì database vẫn chưa biết gì**. `Where`,
`OrderBy`, `Select` chỉ bồi thêm vào cây biểu thức trong bộ nhớ. SQL chỉ bay xuống khi kết quả
bị tiêu thụ — `ToListAsync`, `Count`, `Single`, hay một vòng `foreach`.

## Vì sao phải tham số hoá

Khi bạn viết `Where(b => b.City == city)`, EF không nhét giá trị vào giữa chuỗi SQL. Nó sinh
một tham số. Hai lý do:

- **Chống SQL injection.** Cái này ai cũng biết.
- **Plan cache.** SQL Server băm nguyên chuỗi SQL để tra kế hoạch thực thi. Chuỗi giống hệt thì
  tra ra plan cũ, khỏi biên dịch. Lệch một ký tự là câu mới: biên dịch lại, và nhét thêm một
  plan vào cache.

Ghi nhớ vế thứ hai. Nó là gốc của mọi thứ còn lại trong bài.

## Ba lần đổi cách dịch cho `Contains`

```csharp
int[] ids = [1, 2, 3];
var blogs = await context.Blogs.Where(b => ids.Contains(b.Id)).ToListAsync();
```

Câu này trông vô hại, và nó là chỗ EF đã đổi cách dịch **ba lần trong ba bản liên tiếp**.

### EF ≤ 7 — nội suy thành hằng

```sql
SELECT [b].[Id], [b].[Name]
FROM [Blogs] AS [b]
WHERE [b].[Id] IN (1, 2, 3)
```

Chạy được, nhưng mỗi danh sách sinh một chuỗi SQL khác nhau → plan cache trượt và phình.
[Tài liệu EF]({whatsnew}) ghi rằng issue này từng là issue được bình chọn nhiều nhất trong repo.

### EF 8–9 — một tham số JSON, bung bằng `OPENJSON`

```sql
@__ids_0='[1,2,3]'

SELECT [b].[Id], [b].[Name]
FROM [Blogs] AS [b]
WHERE [b].[Id] IN (
    SELECT [i].[value]
    FROM OPENJSON(@__ids_0) WITH ([value] int '$') AS [i]
)
```

Danh sách nào cũng ra đúng một chuỗi SQL. Đổi lại, bộ lập kế hoạch **mất thông tin về số phần
tử** — nó không biết trong tham số đó có 3 hay 30.000 giá trị, mà kế hoạch tốt cho hai trường
hợp đó là hai thứ khác nhau.

### EF 10 — mỗi giá trị một tham số

```sql
SELECT [b].[Id], [b].[Name]
FROM [Blogs] AS [b]
WHERE [b].[Id] IN (@ids1, @ids2, @ids3)
```

Planner đếm được số phần tử, mà SQL vẫn tham số hoá. Và EF còn **đệm** danh sách tham số: 8 giá
trị thì sinh 10 tham số, hai cái cuối lặp lại giá trị của cái thứ 8 — để 8, 9, 10 phần tử dùng
chung một chuỗi SQL thay vì ba chuỗi. Lặp một giá trị đã có trong tập hợp thì kết quả `IN`
không đổi.

### Ba chế độ, và quyền chọn thuộc về bạn

Tài liệu nói thẳng: EF không thể lúc nào cũng chọn đúng, vì chọn đúng thì phải biết dữ liệu
trong database của bạn. Nên nó giao lại công tắc.

```csharp
// mức toàn cục
optionsBuilder.UseSqlServer(conn,
    o => o.UseParameterizedCollectionMode(ParameterTranslationMode.Constant));
```

```csharp
// mức từng câu
await context.Blogs.Where(b => EF.Constant(ids).Contains(b.Id)).ToListAsync();
await context.Blogs.Where(b => EF.Parameter(ids).Contains(b.Id)).ToListAsync();
await context.Blogs.Where(b => EF.MultipleParameters(ids).Contains(b.Id)).ToListAsync();
```

- `MultipleParameters` — mặc định mới của EF 10.
- `Parameter` — kiểu JSON của EF 8–9.
- `Constant` — kiểu nội suy hằng thời trước.

## Nâng cấp không hứa nhanh hơn

Chỗ này hay bị kể sai, nên trích cho rõ. [Tài liệu breaking changes]({breaking}) nói rằng ứng
dụng được xây trên EF 8 hoặc 9 và dựa vào đặc tính hiệu năng của bản dịch JSON — **nhất là các
câu truy vấn với danh sách lớn** — có thể gặp khác biệt hiệu năng khi lên EF 10, và đưa sẵn
đường lui. Đó không phải câu nói cho có: nó chỉ đích danh trường hợp có nguy cơ.

## Hai cái bẫy lúc nâng cấp

### Tên tham số đổi → plan cache dựng lại

EF 10 rút gọn tên tham số từ `@__city_0` thành `@city`. Đọc log dễ hơn hẳn. Nhưng tên tham số
**nằm trong chuỗi SQL**, mà SQL Server băm cả chuỗi để tra plan cache. Tài liệu ghi thẳng: nâng
cấp có thể làm **gần như toàn bộ plan đã cache phải biên dịch lại**, và hệ thống lớn nên tính
trước một đợt biên dịch tăng vọt ngay sau khi triển khai.

Không phải sự cố. Nhưng biết trước thì đỡ hoảng.

### `Application Name` bị chèn vào chuỗi kết nối

Từ EF 10, nếu chuỗi kết nối không có `Application Name`, EF tự chèn một cái chứa thông tin ẩn
danh về phiên bản EF và SqlClient. Phần lớn trường hợp vô hại. Nhưng nếu ứng dụng vừa nối bằng
EF vừa nối bằng Dapper/ADO.NET tới cùng database, thì hai bên giờ có **hai chuỗi kết nối khác
nhau** → SqlClient tách thành **hai connection pool**. Nếu chuyện đó xảy ra trong một
`TransactionScope`, giao dịch có thể **leo thang thành giao dịch phân tán** ở chỗ trước đây
không cần.

Chữa: tự đặt `Application Name` trong chuỗi kết nối. EF thấy có rồi thì không đụng vào.

## Hai thay đổi về an toàn

**Log che giá trị nội suy.** Trước đây, chỗ nào EF nội suy thẳng giá trị vào SQL thì giá trị đó
nằm nguyên trong log. EF 10 vẫn gửi SQL thật xuống database, nhưng ghi log thành:

```sql
SELECT [b].[Id], [b].[Role]
FROM [Blogs] AS [b]
WHERE [b].[Role] IN (?, ?)
```

Muốn thấy đủ thì bật `EnableSensitiveDataLogging` — tức là bạn cố ý bật, chứ không bị rò.

**Analyzer cảnh báo nối chuỗi trong SQL thô.** `FromSql` nhận `FormattableString` nên an toàn
sẵn. `FromSqlRaw` thì đúng như tên. Từ EF 10, nối chuỗi ngay trong lời gọi SQL thô sẽ bị cảnh
báo; nếu mảnh nối vào là thứ bạn kiểm soát thì tắt cảnh báo được.

## Hai thứ mới nên dùng ngay

**`LeftJoin` / `RightJoin` là toán tử LINQ bậc một trong .NET 10.** Trước đây phải xếp
`SelectMany` + `GroupJoin` + `DefaultIfEmpty` đúng một thứ tự nhất định.

```csharp
var query = context.Students
    .LeftJoin(
        context.Departments,
        student => student.DepartmentID,
        department => department.ID,
        (student, department) => new
        {
            student.FirstName,
            student.LastName,
            Department = department.Name ?? "[NONE]"
        });
```

**Split query hết lệch thứ tự.** Trước EF 10, câu con bên trong bị rụng cột `Id` khỏi mệnh đề
`ORDER BY`, nghĩa là hai câu truy vấn có thể sắp xếp lệch nhau và trả về **dữ liệu ghép sai —
không có lỗi nào được ném ra**. EF 10 vá chỗ đó. Riêng cái này đã đủ lý do để nâng cấp.

## Cách tự kiểm

Không đoán. Hai việc, làm được trong một buổi chiều:

1. Bật log SQL của EF và **nhìn chuỗi thật** mà nó gửi xuống — nhất là mấy câu có `Contains`.
2. Mở execution plan bên SQL Server và đối chiếu: câu đó đang seek hay scan, plan có bị biên
   dịch lại mỗi lần chạy không.

Kết quả của hai việc đó nói về **database của bạn**, thứ mà không bài viết nào trả lời hộ được.

## Nguồn

- [What's New in EF Core 10]({whatsnew}) — Microsoft Learn
- [Breaking changes in EF Core 10]({breaking}) — Microsoft Learn
- [How Queries Work]({howquery}) — Microsoft Learn
""",
    },
    {
        "n": 2,
        "slug": "chuoi-va-collation",
        "title": "Bài 2: Cùng một phép so chuỗi, hai kết quả",
        "description": "name == \"duy\" chạy trong bộ nhớ ra một dòng, chạy trên SQL Server ra ba dòng. EF dịch thẳng == thành =, và đó là cố ý.",
        "minutes": 12,
        "body": """## Xem bản video

{VIDEO_2}

## Cùng một biểu thức, hai kết quả

```csharp
var found = people.Where(x => x.Name == "duy");
```

Chạy trên một `List<Person>` trong bộ nhớ, với dữ liệu `duy`, `Duy`, `DUY`: ra **một dòng**.
Đưa đúng biểu thức đó cho EF chạy xuống SQL Server: ra **ba dòng**. Không có lỗi nào.

Thủ phạm là **collation**.

## Collation là gì

Collation là bộ luật quy định hai chuỗi được **so sánh** và **sắp xếp** như thế nào. Cả hai vế.
Mọi phép xử lý chuỗi trong database đều dùng một collation nào đó, dù bạn có khai báo hay không.

### Đọc tên một cái collation

`SQL_Latin1_General_CP1_CI_AS` — phần đuôi mới là phần quyết định hành vi:

| Hậu tố | Nghĩa |
|---|---|
| `CI` / `CS` | không / có phân biệt hoa thường |
| `AI` / `AS` | không / có phân biệt dấu |
| `KS` | phân biệt kana (tiếng Nhật) |
| `WS` | phân biệt độ rộng ký tự |
| `VSS` | phân biệt variation selector |
| `SC` | hỗ trợ ký tự bổ sung |
| `UTF8` | lưu bằng mã hoá UTF-8 (từ SQL Server 2019) |

Ví dụ trong [tài liệu SQL Server]({sqlcollation}): `Japanese_Bushu_Kakusu_100_CS_AS_KS_WS_SC_UTF8`
là case-sensitive, accent-sensitive, kana-sensitive, width-sensitive, và mã hoá UTF-8.

### Hai mặc định đã lệch nhau

- **.NET**: `s1 == s2` là so ordinal — **phân biệt hoa thường** tuyệt đối.
- **SQL Server**: collation mặc định cho locale "English (United States)" là
  `SQL_Latin1_General_CP1_CI_AS` — **không** phân biệt hoa thường, **có** phân biệt dấu.

Hai đầu dây nghĩ khác nhau trước khi bạn viết dòng code nào.

## Cái bẫy nằm ngay lúc cài

[Tài liệu SQL Server]({sqlcollation}) viết: collation mặc định lúc cài được xác định theo locale
của hệ điều hành — và **vì lý do tương thích ngược, mặc định được đặt về phiên bản cũ nhất còn
tồn tại ứng với locale đó**. Rồi nói tiếp: cho nên đây không phải lúc nào cũng là collation được
khuyến nghị.

Nói cách khác: database production của bạn có thể đang chạy một bộ luật so chuỗi từ rất lâu,
chỉ vì hồi cài ai đó bấm Next.

## EF cố tình không hoà giải

EF dịch `==` của C# thành `=` của SQL, thẳng, không thêm gì. [Tài liệu EF]({collation}) nói rõ
đây là **cố ý**, với hai lý do:

1. EF không biết bạn muốn collation nào — và "không phân biệt hoa thường" có nhiều biến thể,
   vì chuyện hoa thường phụ thuộc ngôn ngữ.
2. Áp collation vào mọi phép so sánh sẽ khiến phần lớn câu truy vấn **mất index**.

Hệ quả: gọi `string.Equals(a, b, StringComparison.OrdinalIgnoreCase)` trong LINQ-to-Entities thì
EF **ném lỗi**, cũng có chủ ý, cũng vì đúng hai lý do trên.

## Hoa thường và thứ tự đều theo văn hoá

- Trong tiếng Thổ Nhĩ Kỳ, `i` và `I` là **hai chữ cái khác nhau** — nên không tồn tại một khái
  niệm "không phân biệt hoa thường" chung cho cả nhân loại.
- `ä` xếp ngay sau `a` trong tiếng Đức, nhưng xếp **cuối bảng chữ cái** trong tiếng Thuỵ Điển.
- Tiếng Đức đôi khi (không phải luôn luôn) coi `ä` và `ae` là như nhau.

Còn **collation nhị phân** (đuôi `BIN`) thì so thẳng bằng điểm mã và bỏ qua locale — tới mức
`Latin1_General_BIN` và `Japanese_BIN` cho kết quả sắp xếp **y hệt nhau** trên dữ liệu Unicode.
Hợp cho mã định danh, khoá kỹ thuật, chữ ký băm.

## Tiếng Việt: dấu là một phần của chữ

`hoà` và `hoa` là hai từ khác nghĩa. Nên hậu tố `AS` — có phân biệt dấu — với dữ liệu tiếng Việt
không phải một lựa chọn kỹ thuật, mà là điều kiện để dữ liệu có nghĩa.

Cảnh báo thực tế: nếu ai đó đổi cột sang `AI` để "gõ không dấu vẫn tìm ra", bạn vừa mất khả năng
phân biệt `hoà` với `hoa` trong toàn bộ cột đó. Nhu cầu tìm không dấu nên giải bằng **một cột
phụ đã bỏ dấu**, không nên giải bằng cách làm hỏng cột chính.

## Ba tầng đặt collation

```csharp
// tầng database
modelBuilder.UseCollation("SQL_Latin1_General_CP1_CS_AS");
```

```csharp
// tầng cột
modelBuilder.Entity<Customer>().Property(c => c.Name)
    .UseCollation("SQL_Latin1_General_CP1_CI_AS");
```

```csharp
// tầng câu truy vấn
var customers = await context.Customers
    .Where(c => EF.Functions.Collate(c.Name, "SQL_Latin1_General_CP1_CS_AS") == "John")
    .ToListAsync();
```

Câu cuối sinh ra:

```sql
SELECT [c].[Id], [c].[Name]
FROM [Customers] AS [c]
WHERE [c].[Name] COLLATE SQL_Latin1_General_CP1_CS_AS = N'John'
```

Hẹp đè rộng. Nhưng tầng ba đắt nhất.

## Cái giá của tầng ba: mất index

Index **thừa hưởng collation của cột** nó nằm trên. Mọi câu truy vấn dùng đúng collation đó thì
tự động xài được index. Nhét một `COLLATE` khác vào câu truy vấn thì luật so sánh không còn khớp
với luật mà index đã dựng theo, và câu đó **không dùng được index nữa**.

Gọi `ToLower()` trong `Where` dính đúng cái bẫy đó, vì lý do y hệt.

Tài liệu EF có cảnh báo riêng cho chuyện này: luôn kiểm tra execution plan, và việc ghi đè
case-sensitivity bằng `EF.Functions.Collate` hoặc `string.ToLower` có thể ảnh hưởng rất lớn tới
hiệu năng.

## Làm đúng thì làm thế nào

Quyết collation ở **tầng cột hoặc tầng database**, càng sớm càng tốt, rồi để mọi câu truy vấn
hưởng chung index. Tài liệu khuyên chọn collation **trước khi tạo database**, vì đổi collation
của một database đang sống dễ sinh rắc rối.

### Ba phép tự kiểm, mười phút

1. Tìm theo tên bằng chữ hoa và chữ thường. Ra cùng kết quả → cột đang `CI`.
2. Tìm bằng chuỗi có dấu và không dấu. Ra cùng kết quả → cột đang `AI`; với dữ liệu tiếng Việt,
   đó là chuyện phải xem lại.
3. Mở execution plan của câu truy vấn quan trọng nhất. Nếu bạn vừa thêm `COLLATE` hoặc
   `ToLower()` vào đó, rất có thể nó vừa tụt từ Index Seek xuống Index Scan.

## Nguồn

- [Collations and case sensitivity]({collation}) — EF Core, Microsoft Learn
- [Collation and Unicode Support]({sqlcollation}) — SQL Server, Microsoft Learn
""",
    },
]

EMBED = """<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/VIDEO_ID"
    title="TITLE"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>"""


def embed(n, title):
    vid = VIDEO.get(str(n))
    if not vid:
        return "_Video sẽ được gắn vào sau khi tập này lên sóng._"
    return EMBED.replace("VIDEO_ID", vid).replace("TITLE", title)


course_id = uuid.uuid5(NS, SERIES_SLUG)
base = ROOT / "content" / "series" / CATEGORY / SERIES_SLUG
chapter = base / "chapters" / "01-hai-nghia-cua-chu-translation" / "lessons"
chapter.mkdir(parents=True, exist_ok=True)

entries = []
for lesson in LESSONS:
    lid = uuid.uuid5(NS, f"{SERIES_SLUG}/{lesson['slug']}")
    vid = VIDEO.get(str(lesson["n"]))

    body = lesson["body"]
    for key, url in SRC.items():
        body = body.replace("{" + key + "}", url)
    body = body.replace("{VIDEO_%d}" % lesson["n"], embed(lesson["n"], lesson["title"]))

    front = [
        "---",
        f"id: {lid}",
        f"title: '{lesson['title']}'",
        f"slug: {lesson['slug']}",
        "description: >-",
        f"  {lesson['description']}",
        f"duration_minutes: {lesson['minutes']}",
        "is_free: true",
    ]
    if vid:
        front.append(f"video_url: https://youtu.be/{vid}")
    front += [
        f"sort_order: {lesson['n'] - 1}",
        "section_title: 'Hai nghĩa của chữ translation'",
        "course:",
        f"  id: {course_id}",
        f"  title: '{SERIES_TITLE}'",
        f"  slug: {SERIES_SLUG}",
        "---",
        "",
    ]
    path = chapter / f"{lesson['n']:02d}-{lesson['slug']}.md"
    path.write_text("\n".join(front) + body, encoding="utf8")

    entry = (f"{{id: {lid}, title: '{lesson['title']}', slug: {lesson['slug']}, "
             f"description: '{lesson['description']}', duration_minutes: {lesson['minutes']}, "
             f"is_free: true, sort_order: {lesson['n'] - 1}")
    if vid:
        entry += f", video_url: https://youtu.be/{vid}"
    entries.append(entry + "}")

index = f"""---
id: {course_id}
title: '{SERIES_TITLE}'
slug: {SERIES_SLUG}
description: >-
  Chữ "translation" trong .NET có hai nghĩa, và cả hai đều dẫn tới cùng một chỗ: SQL Server.
  Một là EF Core dịch cây biểu thức LINQ thành T-SQL. Hai là dịch nghĩa của phép so chuỗi giữa
  hai bên — chỗ mà cùng một dòng code cho hai kết quả khác nhau mà không ai báo lỗi.
featured_image: images/blog/dotnet-10-sql-server-chuyen-dich/cover.png
level: intermediate
duration_hours: 1
lesson_count: 2
price: '0.00'
is_free: true
view_count: 0
average_rating: '0.00'
review_count: 0
enrollment_count: 0
meta: null
published_at: '2026-08-09T14:00:00.000000Z'
created_at: '2026-08-09T14:00:00.000000Z'
author: {{id: 019c9616-d2b4-713f-9b2c-40e2e92a05cf, name: Duy Tran, avatar: avatars/7e8eb5c6-4cac-455b-a701-4060f085d501.jpeg}}
category: {{id: 019c9617-facb-72da-8191-e6d44b88fb3e, name: Lập Trình, slug: lap-trinh}}
tags:
  - name: .NET
    slug: dotnet
  - name: EF Core
    slug: ef-core
  - name: SQL Server
    slug: sql-server
is_published: true
sections: [{{id: section-01, title: 'Hai nghĩa của chữ translation', description: 'Hai bài độc lập, đọc bài nào trước cũng được.', sort_order: 1, lessons: [{', '.join(entries)}]}}]
---

# {SERIES_TITLE}

EF Core không phải hộp đen dịch LINQ ra SQL cho vui. Nó thay bạn ra một quyết định đánh đổi giữa
việc cho SQL Server tái dùng kế hoạch thực thi, và việc cho SQL Server biết đủ thông tin để lập
kế hoạch cho tốt. EF 10 vừa chọn lại điểm cân bằng đó — lần thứ ba trong ba bản liên tiếp.

Series dựng theo **EF Core 10 / .NET 10**. Mọi khẳng định đều dẫn được về tài liệu Microsoft;
nguồn nằm ở cuối mỗi bài.
"""
(base / "index.md").write_text(index, encoding="utf8")

print(f"{len(LESSONS)} bài + index.md → {base.relative_to(ROOT)}")
