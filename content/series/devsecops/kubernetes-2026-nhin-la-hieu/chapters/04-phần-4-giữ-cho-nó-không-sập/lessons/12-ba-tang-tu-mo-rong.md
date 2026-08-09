---
id: d57cc7cc-7d55-5ef0-b3ad-6006b81a00b6
title: 'Bài 12: Ba tầng tự mở rộng, và cái bẫy ở mức 0'
slug: ba-tang-tu-mo-rong
description: >-
  HPA về 0 bật sẵn từ 1.36 — nhưng ở mức 0 thì HPA mù, và không thể tự bật lại bằng CPU.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/KA-znkQPlGw
sort_order: 2
section_title: 'Phần 4: Giữ cho nó không sập'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/KA-znkQPlGw"
    title="Bài 12: Ba tầng tự mở rộng, và cái bẫy ở mức 0"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Không chỉ có HPA

Có **ba tầng**, ba đơn vị khác nhau:

| Tầng | Nó đổi cái gì |
|---|---|
| `HPA` | **số pod** |
| `VPA` | **kích thước pod** — sửa requests và limits |
| Cluster Autoscaler | **số máy** |

Nhớ đúng ba đơn vị này thì phần còn lại rất dễ.

## HPA quyết số pod bằng gì

```
số pod mới = ⌈ số pod hiện tại × số đo hiện tại ÷ mục tiêu ⌉
```

Đang chạy 4 pod, CPU trung bình 80%, mục tiêu 50%:
`80 ÷ 50 = 1,6` → `1,6 × 4 = 6,4` → làm tròn lên → **7 pod**.

Không có phép màu nào, chỉ có phép nhân này.

## Tầng máy vào việc khi nào

HPA tạo thêm pod → pod đó phải có chỗ ngồi → cụm hết chỗ thì pod nằm `Pending` → Cluster
Autoscaler thấy vậy và thêm máy.

Chú ý: nó nhìn **`requests`**. Nên requests đặt sai thì cả tầng máy cũng quyết sai theo.

## HPA về 0 — và cái bẫy quan trọng hơn tính năng

Khả năng cho HPA về 0 có từ **1.16**, nhưng suốt hai mươi bản vẫn là tính năng phải tự bật. Từ
**1.36 nó bật sẵn**: ghi `minReplicas: 0` trong HPA gốc là chạy, không cần công cụ ngoài nào.

**Nhưng ở mức 0, HPA bị mù.** Nó tính số pod dựa trên số đo lấy từ chính đám pod đó — mà giờ
không còn pod nào. Vậy lấy đâu ra số đo để biết là cần bật lên lại?

Kết luận rất rõ: muốn đi từ **0 lên 1** thì phải dùng một số đo **nằm ngoài khối lượng công
việc** — độ sâu hàng đợi, số request đang đứng ở cửa. Dựa vào CPU thì nó nằm ở 0 mãi mãi.

## HPA và VPA đánh nhau

CPU lên cao → HPA thêm pod → CPU trung bình tụt. Cùng lúc VPA thấy CPU cao → tăng requests → mẫu
số đổi → HPA lại tính ra một con số khác. **Hai anh cùng vặn một cái núm theo hai hướng.**

Cách dùng an toàn: để VPA lo **bộ nhớ**, HPA lo **CPU**. Hoặc chạy VPA ở chế độ chỉ khuyến nghị.

## Lên nhanh, xuống chậm — có chủ ý

HPA mở rộng lên thì nhanh, nhưng thu hẹp xuống thì cố tình chậm (mặc định chờ một cửa sổ ổn định
vài phút). Lý do rất thực tế: **mở rộng nhầm chỉ tốn tiền, thu hẹp nhầm thì mất dịch vụ**.

Tải lên xuống theo nhịp ngắn? Hãy **nới** cửa sổ đó ra chứ đừng bóp lại.

## Danh sách kiểm tra

- Cụm đã có `metrics-server` chưa? Không có thì HPA không đọc được gì
- Có đang bật **cả HPA lẫn VPA** trên cùng một loại tài nguyên không?
- Dùng `minReplicas: 0` thì **số đo để bật lại lấy từ đâu**, và nó có sống khi không còn pod nào?
- `requests` đặt đã sát thực tế chưa? Cả HPA lẫn tầng máy đều tính từ đó

**Nguồn:** [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
