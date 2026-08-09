---
id: 1491ca18-a087-59c6-a891-d2965ea5e533
title: 'Bài 13: Cập nhật cuốn chiếu vẫn rơi request'
slug: rollout-va-pdb
description: >-
  Bốn chỗ rơi, và cả bốn đều là chỗ Kubernetes cố tình không tự lo.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/4UfzNkXfYWQ
sort_order: 3
section_title: 'Phần 4: Giữ cho nó không sập'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/4UfzNkXfYWQ"
    title="Bài 13: Cập nhật cuốn chiếu vẫn rơi request"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Thử đo trong lúc deploy mà xem

Cập nhật cuốn chiếu được quảng cáo là không rơi request. Nhưng đo thật thì gần như chắc chắn có
một nhúm `502`, `503`.

## Chuyện gì xảy ra khi một pod bị xoá

Có **hai luồng chạy song song**, và điều quan trọng nhất là chúng **không có thứ tự với nhau**:

| Luồng | Các bước |
|---|---|
| **1 — gỡ khỏi Service** | endpoint controller gỡ tên khỏi EndpointSlice → API server → kube-proxy trên **từng máy** cập nhật luật |
| **2 — tắt container** | kubelet chạy hook `preStop` → gửi tín hiệu tắt |

Luồng 2 thường nhanh hơn, vì nó chỉ là chuyện trên một máy. Luồng 1 phải lan ra mọi node.

Nghĩa là có một khoảng mà container **đã bắt đầu tắt** trong khi vài máy **vẫn còn luật cũ và vẫn
đang gửi request tới**. Request đó rơi. Đây là nguyên nhân số một, và nó không hiện ra khi bạn
thử trên máy cá nhân.

## Cách chữa: preStop ngủ vài giây

```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "10"]
```

Trong mấy giây đó container **vẫn phục vụ bình thường** (tín hiệu tắt chưa được gửi), còn luồng
gỡ khỏi Service thì kịp lan tới mọi node. Đây không phải mẹo bẩn — nó là cách chính thức để đợi
trạng thái mạng hội tụ.

## Chỗ rơi thứ hai: thời gian ân hạn

Mặc định 30 giây kể từ lúc gửi tín hiệu tắt, hết thì giết cứng. **Mấy giây ngủ của preStop cũng
tính vào 30 giây này.** Ứng dụng có request chạy lâu thì nới `terminationGracePeriodSeconds` lên
cho đủ: thời gian ngủ **cộng** thời gian xử lý nốt, rồi thêm một chút.

## Chỗ rơi thứ ba: pod mới

Không có `readinessProbe`, hoặc probe trả lời OK ngay khi tiến trình vừa lên, thì pod được ghi
vào EndpointSlice trong khi nó còn đang nạp cấu hình. Request đầu tiên vào và thất bại.

## Chỗ rơi thứ tư: PodDisruptionBudget

```yaml
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector:
    matchLabels: { app: web }
```

"Dịch vụ này lúc nào cũng phải còn ít nhất 2 bản." Ai muốn đuổi pod mà vi phạm thì bị từ chối.

Nó bảo vệ khỏi **gián đoạn tự nguyện**: rút một máy ra bảo trì, bộ tự mở rộng cụm gom máy lại.

## Hai hiểu nhầm về PDB

- ✕ **PDB không cứu khi máy chết đột ngột** — đó là gián đoạn *không* tự nguyện, chẳng ai hỏi PDB
- ✕ **PDB không chặn cập nhật cuốn chiếu của Deployment** — PDB được kiểm ở API `eviction`, còn
  Deployment controller **xoá pod thẳng**, không đi qua đường đó

Cái chặn cập nhật cuốn chiếu là `maxUnavailable`.

## Bốn dòng, đặt đúng một lần

1. Có `preStop` ngủ vài giây chưa?
2. `terminationGracePeriodSeconds` có đủ cho request dài nhất không?
3. `readinessProbe` có thật sự trả lời "chưa sẵn sàng" lúc đang nạp không?
4. Có PDB cho dịch vụ mà việc rút máy ra bảo trì không được phép làm gián đoạn không?
