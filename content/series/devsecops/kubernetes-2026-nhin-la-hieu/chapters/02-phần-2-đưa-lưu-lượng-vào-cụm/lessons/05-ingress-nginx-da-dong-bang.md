---
id: f0ab9f24-8d93-52bf-bb90-5d58491b5d9e
title: 'Bài 5: ingress-nginx đã đóng băng — việc phải làm'
slug: ingress-nginx-da-dong-bang
description: >-
  Tháng 3/2026 dự án ngừng phát triển, repo chỉ đọc, không còn vá bảo mật. Và nó đứng ngay ở cửa vào.
duration_minutes: 13
is_free: true
video_url: https://youtu.be/ac8x0L-7zss
sort_order: 1
section_title: 'Phần 2: Đưa lưu lượng vào cụm'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/ac8x0L-7zss"
    title="Bài 5: ingress-nginx đã đóng băng — việc phải làm"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

> **Bài này giao việc, không dạy lý thuyết.** Nếu cụm của bạn đang chạy ingress-nginx thì đây
> là thứ nên đọc trước mọi thứ khác trong series.

## Chuyện đã xảy ra

Tháng 3 năm 2026, dự án `ingress-nginx` ngừng phát triển. Repo chuyển sang **chỉ đọc**:

- không bản phát hành mới
- không sửa lỗi
- **không vá bảo mật**

Theo hướng dẫn di trú của AWS, nó đang đứng ở cửa của **khoảng một nửa** số cụm Kubernetes.
(Con số này là ước tính trong tài liệu đó, không phải phép đo của tôi.)

## Nói cho rõ: cái gì ngừng, cái gì không

| Vẫn còn | Đã ngừng |
|---|---|
| **đối tượng Ingress** — không bị xoá khỏi API, cụm vẫn chấp nhận | **ingress-nginx**, cái controller đọc nó |

Nhưng bản thân Ingress cũng đã **đóng băng tính năng** từ lâu — mọi thứ mới đều đi vào Gateway
API. Nói cách khác: bản mô tả vẫn còn, người thi hành thì nghỉ.

## Vì sao phải dừng

Theo thông báo của Steering Committee và Security Response Committee, lý do rất đời: dự án chạy
gần như hoàn toàn bằng **tình nguyện**, trong khi bề mặt tấn công của nó rất rộng — nó nhận
annotation do người dùng viết rồi sinh ra file cấu hình nginx thật để chạy, ở đúng cửa vào cụm.
Số người bảo trì không đủ để canh một thứ như thế. Ngừng có kiểm soát vẫn hơn để nó mục dần.

## Rủi ro của việc ngồi yên

Hôm nay cụm vẫn chạy bình thường — đó là sự thật. Nhưng **lỗ hổng tiếp theo sẽ không có bản
vá**. Và vì nó nằm ở cửa vào, nó là thứ người ngoài chạm tới đầu tiên, trước cả tường lửa ứng
dụng và trước cả mã của bạn.

Đây không phải chuyện thiếu tính năng. Đây là **một bề mặt tấn công không còn ai canh**.

## Ba đường ra

| | Đường | Cái giá |
|---|---|---|
| 1 | **Chuyển sang Gateway API** *(khuyến nghị)* | công sức lớn nhất, nhưng là đường duy nhất đi tới đâu đó |
| 2 | Đổi sang một ingress controller khác còn được bảo trì | nhẹ hơn, nhưng vẫn ở trên một API đã đóng băng |
| 3 | Mua hỗ trợ thương mại cho bản đã đóng băng | mua thêm thời gian, không giải quyết gì |

Không chọn cũng là một lựa chọn — và là lựa chọn tệ nhất trong bốn cái.

## Công cụ dịch sẵn

`ingress2gateway` bản 1.0 ra tháng 3/2026, dịch được hơn 30 annotation. Nó đọc đám Ingress đang
có rồi sinh ra HTTPRoute tương ứng. **Nhưng nó không phải nút bấm một phát là xong**: nó dịch
phần cấu trúc — host, path, backend. Còn chỗ nào bạn dùng annotation riêng của nginx (rewrite,
auth, rate limit, snippet) thì vẫn phải xem lại bằng mắt.

## Việc làm ngay tuần này

```bash
# 1. đếm xem cụm đang có bao nhiêu Ingress
kubectl get ingress -A --no-headers | wc -l

# 2. chạy thử bản dịch, chỉ in ra màn hình
ingress2gateway print --input-file ingress.yaml
```

3. Chọn đường đi và **ghi hẳn một cái ngày vào lịch**.

Việc tệ nhất lúc này là không làm gì rồi quên nó đi.

**Nguồn:** [Thông báo của Steering & Security Response Committee](https://www.kubernetes.io/blog/2026/01/29/ingress-nginx-statement/) · [Google Open Source — The End of an Era](https://opensource.googleblog.com/2026/02/the-end-of-an-era-transitioning-away-from-ingress-nginx.html) · [AWS — hướng dẫn di trú khỏi NGINX Ingress](https://aws.amazon.com/blogs/networking-and-content-delivery/navigating-the-nginx-ingress-retirement-a-practical-guide-to-migration-on-aws) · [ingress2gateway 1.0](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release)
