---
id: 1ce87a92-bfe7-584b-a2a2-484152e54980
title: 'Bài 3: Đổi một dòng image thì chuyện gì xảy ra'
slug: deployment-va-replicaset
description: >-
  Pod là bất biến. Deployment đẻ ra ReplicaSet mới, và hai cái sống song song lúc chuyển.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/YY9BjHCddLs
sort_order: 2
section_title: 'Phần 1: Vì sao Kubernetes làm việc theo cách đó'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/YY9BjHCddLs"
    title="Bài 3: Đổi một dòng image thì chuyện gì xảy ra"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Pod là bất biến

Sửa một dòng `image` trong yaml, apply, và pod chạy phiên bản mới. Nghe như Kubernetes vào tận
nơi thay ruột cái pod. Không phải. **Pod sinh ra với image nào thì chết với image đó.**

## Ba tầng, và chữ "duy nhất"

- **Deployment** giữ mong muốn: image nào, mấy bản, nhịp cập nhật ra sao
- **ReplicaSet** giữ đủ số pod khớp với **một khuôn duy nhất**
- **Pod** là cái chạy thật

Một ReplicaSet chỉ biết đúng một khuôn. Nên **đổi khuôn là phải đổi ReplicaSet**.

## Hai ReplicaSet sống song song

Khi bạn đổi image, Deployment không sửa ReplicaSet đang có — nó đẻ ra một cái mới. Rồi trong
mấy chục giây sau đó, cụm có hai ReplicaSet cùng lúc:

```
$ kubectl get rs
NAME        DESIRED   CURRENT   READY   AGE
web-7d4b          1         1       1    9d
web-9f2c          3         3       2    24s
```

Cột `DESIRED` của cái cũ tụt dần về 0, của cái mới bò lên.

## Hai nút vặn quyết định nhịp

| Trường | Mặc định | Nó nói gì |
|---|---|---|
| `maxSurge` | 25% | được phép **vượt** mức mong muốn bao nhiêu |
| `maxUnavailable` | 25% | được phép **thiếu** bao nhiêu |

`maxUnavailable: 0` thì không bao giờ tụt dưới mức đang có — đổi lại cụm phải còn chỗ trống.
`maxSurge: 0` thì không tốn thêm tài nguyên — đổi lại phải chịu thiếu người một lúc.

## Vì sao giữ ReplicaSet cũ

Vì đó là **nút quay lui**. `kubectl rollout undo` nghe rất oai, nhưng việc nó làm đơn giản đến
bất ngờ: co ReplicaSet mới về 0, phình ReplicaSet cũ trở lại. Không tải lại image, không dựng
gì mới. Vì thế quay lui nhanh hơn hẳn cập nhật — đừng ngại dùng.

Mặc định giữ 10 bản, chỉnh bằng `revisionHistoryLimit`.

## Hai chi tiết hay vấp

**`pod-template-hash`** — nhãn mà Deployment tự dán, là mã băm của khuôn pod. Khuôn đổi một ký
tự thì mã băm đổi, thành một ReplicaSet khác. Đừng tự đặt nhãn này bằng tay.

**`selector` là bất biến.** Từ `apps/v1` không sửa được. Lý do rất thực tế: đổi selector thì đám
pod đang chạy thành mồ côi, không ReplicaSet nào nhận, và nằm lại ăn tài nguyên mãi mãi. Muốn
đổi thì chỉ có một đường — xoá Deployment rồi tạo lại. Nên nghĩ kỹ nhãn ngay từ ngày đầu.

## Mang gì đi

- Đổi image nghĩa là **thay pod**, không phải sửa pod
- Mỗi khuôn có một ReplicaSet riêng; lúc chuyển thì hai cái sống song song
- Quay lui chỉ là phình lại cái cũ — nhanh, và nên dùng
