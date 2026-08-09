---
id: 49767adf-82f1-5303-b2a7-b9915b42bbe8
title: 'Bài 6: Gateway API không phải Ingress viết lại'
slug: gateway-api
description: >-
  Điểm chính không nằm ở cú pháp mà ở chỗ chia việc cho ai — ba tài nguyên cho ba vai.
duration_minutes: 16
is_free: true
video_url: https://youtu.be/mq7sdWZLgvU
sort_order: 2
section_title: 'Phần 2: Đưa lưu lượng vào cụm'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/mq7sdWZLgvU"
    title="Bài 6: Gateway API không phải Ingress viết lại"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Hiểu nhầm tốn kém nhất

Nếu bạn nghĩ Gateway API chỉ là Ingress viết lại cho đẹp thì sẽ di trú sai ngay từ đầu: dịch
xong cú pháp mà giữ nguyên cách chia quyền. **Điểm chính của nó là chia việc cho ba người khác
nhau.**

## Vấn đề thật của Ingress

Đối tượng Ingress chỉ mô tả được những thứ cơ bản: tên miền, đường dẫn, tới Service nào. Mọi thứ
nhỉnh hơn đều phải nhét vào annotation:

```yaml
metadata:
  annotations:
    nginx.ingress.k8s.io/rewrite-target: /$2
    nginx.ingress.k8s.io/canary-weight: "10"
    nginx.ingress.k8s.io/limit-rps: "20"
```

Mà annotation là **chữ tự do**: cụm không kiểm tra được gì (sai chính tả thì im lặng bỏ qua),
mỗi controller hiểu một kiểu, và đổi controller là viết lại từ đầu.

## Ba tài nguyên, ba chủ sở hữu

| Tài nguyên | Nó khai gì | Ai sở hữu |
|---|---|---|
| `GatewayClass` | loại hạ tầng nào sẽ chạy — y như StorageClass | bên cung cấp hạ tầng |
| `Gateway` | mở cổng nào, chứng chỉ nào, cho ai gắn route vào | đội vận hành cụm |
| `HTTPRoute` | đường dẫn của tôi đi tới Service của tôi | **đội ứng dụng** |

## Vì sao đó là chỗ đáng tiền

Đây là chuyện tổ chức, không phải chuyện kỹ thuật. Với Ingress, muốn đổi một đường dẫn thì phải
sửa cái đối tượng nằm chung với cấu hình TLS và cửa vào. Nên hoặc đội ứng dụng được quyền động
vào cửa vào (đáng sợ), hoặc mọi thay đổi nhỏ đều xếp hàng qua đội hạ tầng (nút thắt cổ chai).
Gateway API cắt đúng chỗ đó.

## Cú pháp: từ chuỗi sang trường có kiểu

```yaml
rules:
  - backendRefs:
      - name: web-v1
        weight: 90
      - name: web-v2
        weight: 10
```

Chia tải theo trọng số, khớp header, chuyển hướng, viết lại đường dẫn, nhân bản request — tất cả
là **trường có kiểu**, API server từ chối ngay nếu sai. Không còn chuỗi ký tự cầu may.

## Chỗ bạn sẽ vấp: đi qua namespace

Gateway thường nằm ở namespace của đội hạ tầng, HTTPRoute nằm ở namespace ứng dụng. Muốn gắn
được thì phải có **cả hai phía đồng ý**: Gateway khai `allowedRoutes`, và nếu route trỏ tới
Service ở namespace khác nữa thì cần thêm `ReferenceGrant`. Nghe phiền, nhưng đó đúng là cái
ngăn một đội vô tình cướp tên miền của đội khác.

## Phiên bản và hai kênh

Gateway API **không nằm sẵn** trong Kubernetes — nó là một bộ CRD phải tự cài.

- **v1.4** — GA 06/10/2025, đưa `BackendTLSPolicy` vào kênh chuẩn (trước đó không có cách khai
  báo chặng từ Gateway xuống pod phải mã hoá)
- **v1.5** — ra năm 2026, chủ yếu đẩy tính năng thử nghiệm sang kênh chuẩn

Hai kênh: **Standard** ổn định, **Experimental** còn đổi được. Đừng đem Experimental lên môi
trường thật.

## Di trú thế nào

Đừng đổi hết trong một đêm. Dựng Gateway **bên cạnh** Ingress đang chạy, chuyển từng tên miền
một, theo dõi vài ngày, rồi mới gỡ cái cũ. Chuyển từng host thì lúc có chuyện bạn biết ngay là
host nào.

## Mang gì đi

- Điểm chính là **ba tài nguyên cho ba vai**
- Annotation thành trường có kiểu — cụm kiểm tra được, và không dính vào một bản hiện thực
- Là CRD phải tự cài; chỉ dùng Standard cho môi trường thật

**Nguồn:** [Gateway API 1.4](https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/) · [Gateway API 1.5](https://kubernetes.io/blog/2026/04/21/gateway-api-v1-5/)
