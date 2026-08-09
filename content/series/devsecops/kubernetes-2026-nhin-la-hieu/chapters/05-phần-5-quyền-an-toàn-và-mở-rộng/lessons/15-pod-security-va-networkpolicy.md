---
id: 1ed5e177-a77e-5995-af2e-661de23a177b
title: 'Bài 15: Container tưởng đã cách ly'
slug: pod-security-va-networkpolicy
description: >-
  root trong container là root thật, cho tới khi bật user namespace. Và NetworkPolicy có thể im lặng không chặn gì.
duration_minutes: 16
is_free: true
video_url: null
sort_order: 1
section_title: 'Phần 5: Quyền, an toàn, và mở rộng'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Container không phải máy ảo

Nó **không có nhân riêng**. Nó dùng chung đúng cái nhân của máy chủ, chỉ được cho nhìn thấy một
góc hẹp hơn.

| | Máy ảo | Container |
|---|---|---|
| nhân | **riêng** | **của máy chủ — dùng chung** |

## Hệ quả đáng sợ

Nếu tiến trình trong container chạy bằng root thì cái root đó, ở góc nhìn của nhân, chính là
**uid 0** — cùng một con số với root của máy chủ. Chỉ cần một lỗ hổng cho phép thoát ra khỏi
container là có ngay quyền root **trên chính cái máy đó**. Không phải root giả. Root thật.

## Cách chữa gốc rễ: user namespace

Vừa lên ổn định ở **1.36**. Ý tưởng rất gọn — **ánh xạ lại mã người dùng**: bên trong container
vẫn là 0, vẫn là root, mọi thứ chạy bình thường; nhưng ở ngoài, nhân nhìn thấy nó là một mã người
dùng thường không có quyền gì.

```yaml
spec:
  hostUsers: false
```

## Tầng chặn phía trên: Pod Security Admission

`PodSecurityPolicy` đã bị gỡ khỏi Kubernetes từ lâu. Thay vào đó là **nhãn trên namespace**:

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

Ba mức: `privileged` (không chặn gì) · `baseline` (chặn những thứ nguy hiểm rõ ràng) ·
`restricted` (siết chặt, buộc chạy không phải root).

Ba chế độ: `enforce` (chặn thật) · `audit` (ghi lại) · `warn` (cảnh báo lúc apply).

**Mẹo dùng:** bật `warn` và `audit` ở mức `restricted` trước, xem log vài tuần, rồi mới bật
`enforce`.

## Còn mạng thì sao

Mặc định trong Kubernetes, **mọi pod nói chuyện được với mọi pod** — không chỉ trong cùng
namespace mà là toàn bộ cụm. Cái pod nhỏ xíu chạy công việc định kỳ, về mặt mạng, gọi thẳng được
vào cơ sở dữ liệu của hệ thống thanh toán.

## NetworkPolicy hoạt động hơi ngược trực giác

- Chưa có policy nào chọn tới một pod → pod đó **mở toang**
- Có một policy chọn nó → pod đó lập tức **từ chối mặc định** cho chiều được chọn

Nghĩa là viết policy **đầu tiên** cho một pod là một hành động khá lớn — nó lật cả trạng thái mặc
định của pod đó, chứ không phải thêm một luật nhỏ.

## Cái bẫy lớn nhất

NetworkPolicy chỉ là một **bản mô tả**. Thứ thi hành nó là **plugin mạng** của cụm. Nếu plugin
không hỗ trợ thì policy vẫn tạo được:

```
$ kubectl apply -f deny-all.yaml
networkpolicy.networking.k8s.io/deny-all created
```

…và nó **không chặn một gói tin nào**. Không lỗi, không cảnh báo, hoàn toàn im lặng.

**Việc bắt buộc sau khi viết policy đầu tiên:** mở một pod, thử gọi sang chỗ lẽ ra phải bị chặn,
xem nó có bị chặn thật không. Kiểm bằng cách thử, đừng đọc tài liệu.

## Năm dòng nên là mặc định

```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

Năm dòng này chặn phần lớn những đường tấn công phổ thông, và với ứng dụng viết tử tế thì gần như
không phải sửa gì.

**Nguồn:** [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
