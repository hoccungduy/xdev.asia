---
id: 7aff26ae-7927-5ef2-8daa-a64740d1c87e
title: 'Bài 9: StatefulSet — khi nào mới thật sự cần'
slug: statefulset
description: >-
  Nó cho bạn danh tính, đúng ba thứ. Không nhân bản, không bầu leader, không sao lưu.
duration_minutes: 14
is_free: true
video_url: https://youtu.be/AJ_nqHbdsg4
sort_order: 2
section_title: 'Phần 3: Cấu hình và dữ liệu'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/AJ_nqHbdsg4"
    title="Bài 9: StatefulSet — khi nào mới thật sự cần"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Một câu đã thành phản xạ

"Có cơ sở dữ liệu thì phải dùng StatefulSet." Tôi cũng từng tin thế, và đã dựng vài cái mà lẽ ra
chỉ cần Deployment. Sự thật là StatefulSet giải một bài toán **rất hẹp**, và cái tên của nó hứa
nhiều hơn cái nó làm.

## Nó cho bạn đúng ba thứ

| | |
|---|---|
| **tên ổn định** | `web-0`, `web-1`, `web-2` — chết đi dựng lại vẫn đúng tên đó |
| **DNS riêng từng pod** | gọi thẳng được, nhờ một Service kiểu headless |
| **đĩa riêng theo tên** | đĩa luôn quay lại đúng pod mang tên đó |

Gộp lại thành một chữ: **danh tính**. Chấm hết.

## Cái nó KHÔNG làm

- ✕ nhân bản dữ liệu
- ✕ bầu leader
- ✕ sao lưu
- ✕ chuyển đổi dự phòng khi một bản chết

Toàn bộ những việc khó ấy vẫn là việc của **ứng dụng bên trong**. Kubernetes chỉ đảm bảo pod số
0 luôn là pod số 0 và luôn tìm lại được ổ đĩa của nó.

## Cần và không cần

**Cần** khi ứng dụng thật sự dựa vào danh tính: cụm cơ sở dữ liệu mà các bản phải biết tên nhau
để đồng bộ, hoặc hệ đồng thuận kiểu etcd/Kafka/ZooKeeper nơi mỗi bản là một thành viên có số hiệu.

**Không cần** khi: chỉ có một bản duy nhất, các bản không cần biết nhau, hoặc dữ liệu để hết ở
ngoài cụm. Một bản duy nhất có đĩa riêng? **Deployment với một PVC là đủ**, và đơn giản hơn nhiều.

## Thứ tự — con dao hai lưỡi

| | |
|---|---|
| tạo | `0 → 1 → 2`, pod trước sẵn sàng thì pod sau mới được tạo |
| xoá | `2 → 1 → 0` |
| cập nhật | `2 → 1 → 0`, từ số cao nhất xuống |

Lưỡi thứ nhất: pod 0 kẹt không lên nổi thì **cả cụm đứng im chờ nó**. Lưỡi thứ hai: trường
`partition` cho thả bản mới từng phần kiểu canary, không cần công cụ gì thêm.

## Cái bẫy đáng nhớ

**Xoá StatefulSet thì mặc định các ổ đĩa không bị xoá theo.** Thu nhỏ số bản cũng vậy: pod biến
mất nhưng PVC vẫn nằm đó.

- *Mặt được:* xoá nhầm vẫn còn dữ liệu để gắn lại
- *Mặt trái:* hoá đơn cứ tăng vì đám đĩa mồ côi không ai dọn

Có một trường cấu hình để đổi hành vi này — nhưng nghĩ kỹ trước khi bật.

## Nói thẳng một chuyện thực tế

Định chạy cơ sở dữ liệu thật trên Kubernetes? **Đừng tự viết StatefulSet từ đầu.** Dùng Operator
do chính đội làm ra cơ sở dữ liệu đó viết — nó lo giúp những phần StatefulSet không lo: sao lưu,
nâng cấp phiên bản, chuyển đổi dự phòng, bầu leader. Hoặc thẳng thắn hơn: dùng dịch vụ quản lý
và dành sức cho phần ứng dụng của mình.

## Bảng quyết định

| Tình huống | Chọn |
|---|---|
| một bản, có đĩa riêng | Deployment + một PVC |
| nhiều bản, không cần biết nhau | Deployment |
| nhiều bản, phải biết tên nhau | StatefulSet |
| database thật — cần sao lưu, chuyển đổi dự phòng | Operator, hoặc dịch vụ quản lý |

Đừng chọn StatefulSet chỉ vì trong đầu có chữ "trạng thái".
