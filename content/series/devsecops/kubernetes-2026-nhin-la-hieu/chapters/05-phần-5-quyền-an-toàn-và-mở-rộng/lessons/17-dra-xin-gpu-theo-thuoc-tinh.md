---
id: 8f58dc85-e48c-51bb-9acc-2f7ca7808d4f
title: 'Bài 17: DRA — cách xin GPU đã đổi hẳn'
slug: dra-xin-gpu-theo-thuoc-tinh
description: >-
  Xin bằng một con số nguyên là xin mù. DRA xin theo thuộc tính — nhưng ổn định ≠ driver sẵn sàng.
duration_minutes: 15
is_free: true
video_url: null
sort_order: 3
section_title: 'Phần 5: Quyền, an toàn, và mở rộng'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Một con số mờ đục

Cách xin GPU suốt bao năm là một dòng: `nvidia.com/gpu: 1`. Nghe thì gọn. Nhưng con số `1` đó
**không nói được gì** về cái GPU bạn sắp nhận.

Nó không nói được:

- tôi cần GPU có **ít nhất 40Gi** bộ nhớ
- tôi cần **dòng chip** nào
- tôi cần **hai GPU nằm cạnh nhau, nối trực tiếp**
- tôi cần driver có **tính năng này**

Cách cũ chỉ có một chỗ để nhét mấy điều kiện đó: đặt tên node rồi dùng `nodeSelector`. Tức là
quay về **xếp chỗ bằng tay**.

## DRA đổi hẳn câu hỏi

| Cách cũ | DRA |
|---|---|
| "cho tôi **một cái**" | "cho tôi một thiết bị **khớp mấy điều kiện này**" |
| scheduler **đếm số** | scheduler **đi tìm cái khớp** |

Điều kiện viết bằng biểu thức — đúng ngôn ngữ **CEL** ở bài trước.

## Bốn khái niệm

| | |
|---|---|
| `DeviceClass` | loại thiết bị — giống `StorageClass` ở bài 8 |
| `ResourceClaim` | cái đơn xin: tôi cần thiết bị thế nào |
| `ResourceClaimTemplate` | khuôn đơn — mỗi pod tự sinh một đơn riêng khi được nhân bản |
| `ResourceSlice` | do driver trên từng máy công bố: máy này có thiết bị gì, thuộc tính ra sao |

Scheduler đọc đám slice đó rồi **ghép đơn với thiết bị**.

## Một ví dụ rất đời

Cụm có ba loại GPU mua ở ba thời điểm: 16Gi, 24Gi, 80Gi. Mô hình cần **40Gi**.

- **Cách cũ:** xin "1 GPU" → nhận cái 16Gi → pod lên, mô hình nạp → hết bộ nhớ, container chết.
  Bạn chỉ biết **sau khi nó đã chết**.
- **Với DRA:** điều kiện 40Gi nằm ngay trong đơn → scheduler không xếp pod lên máy không đáp ứng.
  Sai thì **không bao giờ chạy**, chứ không phải chạy rồi chết.

## Chia nhỏ GPU

Một GPU lớn chia được thành nhiều lát, mỗi lát có bộ nhớ và sức tính riêng. Nhưng với mô hình cũ,
mọi lát quy về **cùng một con số nguyên**, nên bạn không nói được "tôi cần lát cỡ này chứ không
phải cỡ kia". Với DRA, mỗi lát là một thiết bị có thuộc tính riêng.

## Đánh dấu thiết bị

Bôi bẩn một cái GPU đang có vấn đề hoặc đang bảo trì, thế là scheduler thôi xếp việc mới lên đó —
y hệt cơ chế taint trên node, chỉ khác là ở mức **từng thiết bị**. Trước đây muốn làm việc này thì
phải rút cả cái máy ra, dù chỉ một trong tám cái GPU bị lỗi.

## Nói cho chính xác về trạng thái

Phần lõi của DRA lên ổn định ở **1.34**, được khoá lại ở **1.35**, và **1.36** bổ sung thêm mấy
phần nữa.

Nhưng đây là chỗ phải cẩn thận: **Kubernetes ổn định không có nghĩa là mọi thứ đã sẵn sàng**.
Driver của từng hãng và mức hỗ trợ của từng dịch vụ quản lý vẫn khác nhau khá nhiều. Trước khi
dựa vào nó, hãy **kiểm đúng cụm của bạn chứ đừng kiểm tài liệu**.

## Việc nên làm

1. Xem cụm đã có driver DRA cho loại thiết bị đang dùng chưa, và nó công bố những thuộc tính gì
2. Thử một khối lượng công việc **nhỏ** trước — loại mà chạy sai cũng không sao
3. Đang phải đặt tên node rồi dùng `nodeSelector` để chọn GPU? Đó chính là chỗ nên chuyển trước tiên

**Nguồn:** [Understanding Dynamic Resource Allocation — CNCF](https://www.cncf.io/blog/2026/07/01/understanding-dynamic-resource-allocation-in-kubernetes/) · [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
