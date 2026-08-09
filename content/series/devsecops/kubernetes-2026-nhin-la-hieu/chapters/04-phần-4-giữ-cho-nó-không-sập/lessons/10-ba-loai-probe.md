---
id: cb1a2cdd-4230-56ed-b1a7-10c048afe86e
title: 'Bài 10: Ba loại probe, và cách đặt sai làm sập chính mình'
slug: ba-loai-probe
description: >-
  Đặt liveness giống readiness là cách kinh điển tự tạo ra một vòng xoáy chết.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/41F723tTS1g
sort_order: 0
section_title: 'Phần 4: Giữ cho nó không sập'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/41F723tTS1g"
    title="Bài 10: Ba loại probe, và cách đặt sai làm sập chính mình"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Cách nhanh nhất, và cũng là cách sai nhất

```yaml
startupProbe:
  httpGet: { path: /healthz }
readinessProbe:
  httpGet: { path: /healthz }
livenessProbe:
  httpGet: { path: /healthz }
```

Cùng một đường dẫn cho **ba câu hỏi khác nhau**. Tôi từng làm đúng thế.

## Ba câu hỏi, ba hậu quả

| Probe | Câu hỏi | Hỏng thì sao |
|---|---|---|
| `startupProbe` | nó khởi động xong chưa? | trong lúc chưa xong → hai probe kia bị tạm tắt |
| `readinessProbe` | nó có sẵn sàng nhận request không? | **gỡ tên khỏi Service** — pod vẫn sống |
| `livenessProbe` | nó còn cứu được không? | **giết container và dựng lại** |

readiness là *bước sang một bên*. liveness là *bắn bỏ*. Hai chuyện hoàn toàn khác nhau.

## Vòng xoáy chết

Kịch bản này xảy ra nhiều hơn bạn nghĩ:

1. Bạn cho `/healthz` thử luôn kết nối tới cơ sở dữ liệu — nghe rất hợp lý
2. Một ngày DB chậm đi vài giây
3. Cả hai probe cùng hỏng, **trên tất cả các pod, cùng một lúc**
4. readiness rút hết pod khỏi Service — *cái này đúng*
5. liveness **giết sạch pod và dựng lại** — *đây là chỗ hỏng*
6. Pod mới khởi động lại đồng loạt, cùng lúc đập vào DB đang yếu, làm nó chậm thêm

Và vòng đó tự quay.

## Quy tắc để thoát ra

**`livenessProbe` chỉ được hỏi đúng một câu: tiến trình này còn tự cứu được không.**

- ✓ vòng lặp sự kiện còn chạy không, có bị khoá chết không
- ✕ cơ sở dữ liệu, dịch vụ khác, mạng

Vì **khởi động lại không sửa được** mấy thứ đó.

`readinessProbe` thì ngược lại — nó *nên* hỏi phụ thuộc, vì rút khỏi Service đúng là việc cần
làm khi phụ thuộc chết.

## startupProbe để làm gì

Cho ứng dụng khởi động chậm. Không có nó, bạn buộc phải nới `initialDelaySeconds` của liveness
lên thật to để nó đừng giết pod lúc đang nạp — nhưng nới to thì suốt phần đời còn lại của pod,
liveness phản ứng chậm hẳn. startupProbe tách hai chuyện đó ra.

## Bốn con số, và phép nhân phải thuộc

| Trường | Nó nói gì |
|---|---|
| `initialDelaySeconds` | chờ bao lâu trước lần thử đầu |
| `periodSeconds` | cách nhau bao lâu giữa hai lần thử |
| `timeoutSeconds` | chờ bao lâu thì coi một lần thử là hỏng |
| `failureThreshold` | hỏng mấy lần liên tiếp mới tính là hỏng thật |

`periodSeconds × failureThreshold` = thời gian tệ nhất trước khi Kubernetes hành động. 10 giây ×
3 lần = **30 giây**. Đặt số nào cũng được, miễn biết mình vừa đặt ra bao nhiêu giây.

## Bộ ba đặt đúng

```yaml
startupProbe:
  httpGet:  { path: /startup }
  periodSeconds: 5      failureThreshold: 30

readinessProbe:
  httpGet:  { path: /ready }     # CÓ hỏi phụ thuộc
  periodSeconds: 5      failureThreshold: 2

livenessProbe:
  httpGet:  { path: /alive }     # KHÔNG hỏi phụ thuộc
  periodSeconds: 20     failureThreshold: 3
```

Ba đường dẫn khác nhau, ba nhịp khác nhau. liveness có chu kỳ dài hơn và ngưỡng cao hơn vì hậu
quả của nó nặng hơn nhiều.
