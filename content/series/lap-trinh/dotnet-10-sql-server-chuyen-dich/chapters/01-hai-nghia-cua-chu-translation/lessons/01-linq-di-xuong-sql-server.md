---
id: da3557cb-45dd-5f26-a925-c5f859b9b9b2
title: 'Bài 1: LINQ đi xuống SQL Server bằng đường nào'
slug: linq-di-xuong-sql-server
description: >-
  EF không gửi LINQ xuống database. Nó dịch — và bản dịch đó quyết định SQL Server có tái dùng được kế hoạch thực thi hay không.
duration_minutes: 13
is_free: true
video_url: https://youtu.be/wmBW12ShbS8
sort_order: 0
section_title: 'Hai nghĩa của chữ translation'
course:
  id: 575460f7-881d-59ea-9452-15ced18c53b5
  title: '.NET 10 × SQL Server — chuyện dịch'
  slug: dotnet-10-sql-server-chuyen-dich
---
## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/wmBW12ShbS8"
    title="Bài 1: LINQ đi xuống SQL Server bằng đường nào"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Thứ đi xuống dây không phải LINQ

Database không biết LINQ là gì. Thứ duy nhất đi xuống là một chuỗi T-SQL và một mớ tham số.
Đường đi của một câu truy vấn, theo [tài liệu EF Core](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works):

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
[Tài liệu EF](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew) ghi rằng issue này từng là issue được bình chọn nhiều nhất trong repo.

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

Chỗ này hay bị kể sai, nên trích cho rõ. [Tài liệu breaking changes](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes) nói rằng ứng
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

- [What's New in EF Core 10](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew) — Microsoft Learn
- [Breaking changes in EF Core 10](https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes) — Microsoft Learn
- [How Queries Work](https://learn.microsoft.com/en-us/ef/core/querying/how-query-works) — Microsoft Learn
