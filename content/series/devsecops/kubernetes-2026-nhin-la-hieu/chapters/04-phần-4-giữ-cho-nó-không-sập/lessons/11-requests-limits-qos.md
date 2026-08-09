---
id: 4395e690-7912-5e3d-a2d0-bac1ca8d62b3
title: 'Bài 11: requests, limits, và ai bị giết trước'
slug: requests-limits-qos
description: >-
  CPU nén được nên vượt limit là bị bóp; bộ nhớ không nén được nên vượt là bị giết.
duration_minutes: 16
is_free: true
video_url: null
sort_order: 1
section_title: 'Phần 4: Giữ cho nó không sập'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Một thói quen nghe rất vô hại

"Đặt limit cao lên cho chắc — thừa còn hơn thiếu."

Với **CPU**, cái "chắc" đó làm ứng dụng chậm đi ngay cả khi máy đang rảnh. Với **bộ nhớ**, nó
quyết định pod nào bị giết trước lúc máy hết chỗ.

## Hai con số, hai thế giới

```yaml
resources:
  requests:      # scheduler nhìn con số này
    cpu: 200m    # → để quyết pod này bỏ lên MÁY NÀO
    memory: 256Mi
  limits:        # nhân hệ điều hành nhìn con số này
    cpu: 1       # → để CHẶN CONTAINER LẠI lúc đang chạy
    memory: 512Mi
```

Một cái quyết định bạn **ngồi ở đâu**. Một cái quyết định bạn **được ăn bao nhiêu**.

## Hệ quả hay bị bỏ qua

Scheduler chỉ cộng `requests`, nó không quan tâm `limits`. Nên requests thấp mà limits cao thì
trên giấy máy còn rất nhiều chỗ, nhưng thực tế đám container đang chạy có thể ăn nhiều hơn hẳn
cái máy có. Đó là **cam kết vượt mức** — không sai, nhiều nơi cố tình làm vậy để tiết kiệm, nhưng
phải *biết* là mình đang làm.

## Chỗ quan trọng nhất

| | Vượt limit thì sao |
|---|---|
| **CPU** — nén được | bị **bóp lại**, bị bắt ngồi chờ. Container không chết |
| **Bộ nhớ** — không nén được | bị **giết ngay**. Mã thoát `137`, dòng chữ `OOMKilled` |

Cùng một chữ `limit` trong YAML, hai hậu quả khác nhau hoàn toàn.

## Vì sao limit CPU cao lại làm chậm

Vì nhân hệ điều hành không tính trung bình cả giây. Nó chia thời gian thành **từng chu kỳ rất
ngắn** (cỡ 1/10 giây), và trong mỗi chu kỳ bạn chỉ được dùng đúng phần đã khai. Dùng hết là ngồi
chờ tới chu kỳ sau.

Nên một ứng dụng có nhịp **giật cục** — nhận một request rồi xử lý dồn một cái — hoàn toàn có thể
vừa bị bóp liên tục vừa hiện mức sử dụng trung bình rất thấp. Thấy biểu đồ báo CPU 20% mà độ trễ
đuôi xấu thì hãy nghi ngay chỗ này.

## Ba lớp QoS, và thứ tự bị đuổi

| Lớp | Điều kiện | Bị đuổi |
|---|---|---|
| `Guaranteed` | requests = limits, cho **cả** cpu lẫn bộ nhớ, ở **mọi** container | đi sau cùng |
| `Burstable` | có khai, nhưng không bằng nhau | đi thứ hai — nếu đang dùng quá phần đã khai |
| `BestEffort` | **không khai gì cả** | đi **đầu tiên** |

Nói cho gọn: mấy pod bạn quên khai tài nguyên chính là mấy pod chết đầu tiên.

## Bộ quy tắc thực dụng

| | |
|---|---|
| bộ nhớ · requests | luôn khai |
| bộ nhớ · limits | đặt **bằng** requests — bộ nhớ không nén được, để hở chỉ chuốc bất ngờ |
| cpu · requests | luôn khai — đó là thứ giữ chỗ cho bạn |
| cpu · limits | cân nhắc kỹ; nhiều đội chọn **không đặt** để ứng dụng mượn được lúc rảnh |

Chọn không đặt limit CPU thì đổi lại: cụm phải có chỗ đệm và phải theo dõi được. Không có đáp án
đúng cho mọi nơi, nhưng có một đáp án chắc chắn sai: **đặt bừa một con số rồi quên nó đi**.

## Đọc dấu hiệu lúc có sự cố

| Triệu chứng | Nguyên nhân | Làm gì |
|---|---|---|
| bị giết đột ngột · mã 137 · log cụt ngang | bộ nhớ | tăng limit bộ nhớ, hoặc tìm chỗ rò |
| không chết · độ trễ đuôi xấu · CPU trung bình thấp | bị bóp CPU | nhìn số đo throttling của cgroup, **đừng nhìn mức sử dụng** |

Nhầm giữa hai cái này thì bạn sửa nhầm chỗ cả buổi.
