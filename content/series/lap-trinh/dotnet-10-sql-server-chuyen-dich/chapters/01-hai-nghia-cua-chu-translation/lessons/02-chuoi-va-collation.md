---
id: aa49abe6-bb5c-5935-80ad-7407dd28d6d1
title: 'Bài 2: Cùng một phép so chuỗi, hai kết quả'
slug: chuoi-va-collation
description: >-
  name == "duy" chạy trong bộ nhớ ra một dòng, chạy trên SQL Server ra ba dòng. EF dịch thẳng == thành =, và đó là cố ý.
duration_minutes: 12
is_free: true
video_url: https://youtu.be/XpZCh57MbAo
sort_order: 1
section_title: 'Hai nghĩa của chữ translation'
course:
  id: 575460f7-881d-59ea-9452-15ced18c53b5
  title: '.NET 10 × SQL Server — chuyện dịch'
  slug: dotnet-10-sql-server-chuyen-dich
---
## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/XpZCh57MbAo"
    title="Bài 2: Cùng một phép so chuỗi, hai kết quả"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

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

Ví dụ trong [tài liệu SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support): `Japanese_Bushu_Kakusu_100_CS_AS_KS_WS_SC_UTF8`
là case-sensitive, accent-sensitive, kana-sensitive, width-sensitive, và mã hoá UTF-8.

### Hai mặc định đã lệch nhau

- **.NET**: `s1 == s2` là so ordinal — **phân biệt hoa thường** tuyệt đối.
- **SQL Server**: collation mặc định cho locale "English (United States)" là
  `SQL_Latin1_General_CP1_CI_AS` — **không** phân biệt hoa thường, **có** phân biệt dấu.

Hai đầu dây nghĩ khác nhau trước khi bạn viết dòng code nào.

## Cái bẫy nằm ngay lúc cài

[Tài liệu SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support) viết: collation mặc định lúc cài được xác định theo locale
của hệ điều hành — và **vì lý do tương thích ngược, mặc định được đặt về phiên bản cũ nhất còn
tồn tại ứng với locale đó**. Rồi nói tiếp: cho nên đây không phải lúc nào cũng là collation được
khuyến nghị.

Nói cách khác: database production của bạn có thể đang chạy một bộ luật so chuỗi từ rất lâu,
chỉ vì hồi cài ai đó bấm Next.

## EF cố tình không hoà giải

EF dịch `==` của C# thành `=` của SQL, thẳng, không thêm gì. [Tài liệu EF](https://learn.microsoft.com/en-us/ef/core/miscellaneous/collations-and-case-sensitivity) nói rõ
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

- [Collations and case sensitivity](https://learn.microsoft.com/en-us/ef/core/miscellaneous/collations-and-case-sensitivity) — EF Core, Microsoft Learn
- [Collation and Unicode Support](https://learn.microsoft.com/en-us/sql/relational-databases/collations/collation-and-unicode-support) — SQL Server, Microsoft Learn
