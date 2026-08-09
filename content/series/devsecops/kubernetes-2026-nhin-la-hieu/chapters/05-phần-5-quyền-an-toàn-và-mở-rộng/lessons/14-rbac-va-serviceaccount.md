---
id: ff900748-bf72-56bd-b77a-7479a2722e0a
title: 'Bài 14: RBAC — tai nạn đến từ ServiceAccount'
slug: rbac-va-serviceaccount
description: >-
  Mỗi pod cũng là một danh tính. Và động từ list gần bằng quyền đọc nội dung.
duration_minutes: 14
is_free: true
video_url: null
sort_order: 0
section_title: 'Phần 5: Quyền, an toàn, và mở rộng'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Chỗ tai nạn thật sự xảy ra

Nhắc tới RBAC là mọi người nghĩ tới phân quyền cho **người**. Nhưng phần lớn tai nạn về quyền
trong Kubernetes đến từ **ServiceAccount** — danh tính mà chính mấy cái pod của bạn đang mang.

## Bốn đối tượng = tích của hai trục

| | Định nghĩa quyền | Gắn quyền |
|---|---|---|
| trong **một namespace** | `Role` | `RoleBinding` |
| phạm vi **cả cụm** | `ClusterRole` | `ClusterRoleBinding` |

Có chữ `Cluster` ở đầu thì phạm vi cả cụm. Không có thì gói trong một namespace.

**Cách kết hợp ít người để ý:** `RoleBinding` hoàn toàn được phép trỏ vào một `ClusterRole`. Định
nghĩa quyền đúng một lần ở mức cụm, rồi gắn vào từng namespace riêng lẻ — quyền chỉ có hiệu lực
trong namespace đó.

## Token nằm sẵn trong container

Mỗi pod chạy dưới một ServiceAccount; không khai thì dùng `default`. Và mặc định, Kubernetes gắn
sẵn một token của tài khoản ấy vào container:

```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

Nghĩa là mã của bạn — hoặc **bất cứ thứ gì chạy trong container đó** — đều gọi được API server
với danh tính ấy. Pod không cần gọi API server thì tắt đi:

```yaml
spec:
  automountServiceAccountToken: false
```

Một dòng, và nó bỏ hẳn một đường tấn công.

## Chỗ tai nạn 1: động từ `list`

Bạn nghĩ `list` chỉ liệt kê tên? Không. Khi API server trả về danh sách, nó trả về **nguyên cả
đối tượng, kèm toàn bộ nội dung**. Nên cho quyền `list` trên secret, trên thực tế, gần bằng cho
quyền đọc nội dung mọi secret trong phạm vi đó. Muốn cho xem tên thôi thì RBAC không làm được.

## Chỗ tai nạn 2: RBAC chỉ cộng

Không tồn tại quy tắc kiểu "cho phép mọi thứ **trừ** cái này". Chỉ cần **một binding rộng tay** ở
đâu đó là mọi quy tắc siết chặt bạn viết chỗ khác đều thành vô nghĩa. Và cái binding đó thường
không phải do bạn viết, mà do một biểu đồ Helm nào đó cài vào từ năm ngoái.

## Chỗ tai nạn 3: `cluster-admin` gắn vào ServiceAccount

Rất nhiều bản cài mặc định làm thế cho tiện. Hậu quả: chỉ cần **một lỗ hổng thực thi mã** trong
đúng cái pod đó là người tấn công có ngay quyền quản trị toàn cụm. Không có bước leo thang nào —
token đã nằm sẵn trong container, và nó đã là quyền cao nhất.

Đây là chỗ đầu tiên tôi nhìn khi rà một cụm lạ.

## Lệnh nên thuộc

```bash
kubectl auth can-i --list   --as=system:serviceaccount:thanh-toan:api-worker
```

Đừng đọc YAML rồi tự suy ra — quyền cộng dồn từ nhiều binding và bạn sẽ bỏ sót, nhất là mấy cái
do công cụ cài vào. Hỏi thẳng API server thì nó trả lời thật.

## Danh sách siết

1. Có ServiceAccount nào đang gắn `cluster-admin` không — và nó có thật sự cần không?
2. Pod nào không gọi API server thì tắt automount token đi
3. Soi lại mấy động từ rộng như `list`, `watch` trên secret
4. **Mỗi ứng dụng một ServiceAccount riêng** — dùng chung `default` thì không bao giờ siết được
