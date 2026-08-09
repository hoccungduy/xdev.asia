---
id: 27e7592c-b7a5-5235-9258-738744b31e0a
title: 'Bài 1: kubectl apply không ra lệnh cho cụm'
slug: vong-lap-dieu-hoa
description: >-
  Câu lệnh chỉ ghi mong muốn vào sổ. Việc tạo container do một vòng lặp khác làm, và nó chạy mãi mãi.
duration_minutes: 14
is_free: true
video_url: null
sort_order: 0
section_title: 'Phần 1: Vì sao Kubernetes làm việc theo cách đó'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Cái ai cũng nghĩ

Gõ `kubectl apply -f app.yaml`, ứng dụng chạy. Nên gần như ai cũng hiểu rằng câu lệnh đó **ra
lệnh** cho cụm triển khai. Hiểu vậy là sai, và nó sai theo cách chỉ lộ ra lúc có sự cố.

## Cái thật sự xảy ra

Câu lệnh không chạy gì cả. Nó gửi một bản mô tả tới API server, và API server ghi bản mô tả ấy
vào etcd. Hết. **Không container nào được tạo ở bước này.** Cái bạn vừa làm chỉ là ghi vào sổ
rằng bạn muốn có ba bản sao.

## Việc tạo container do một vòng lặp làm

1. Đọc mong muốn trong sổ
2. Nhìn hiện trạng thật của cụm
3. So hai cái với nhau
4. Lệch thì hành động cho bớt lệch — rồi quay lại bước 1

Vòng lặp này **không có chặng cuối**. Nó chạy mãi.

## Ai chạy vòng lặp đó

Không phải một, mà rất nhiều vòng lặp chạy song song:

| Thành phần | Việc của nó |
|---|---|
| `etcd` | cuốn sổ — chỉ nó giữ trạng thái |
| `API server` | cửa duy nhất ra vào sổ |
| `scheduler` | thấy pod chưa có máy → chọn máy |
| `controller-manager` | vài chục vòng lặp nhỏ, mỗi cái một loại tài nguyên |
| `kubelet` | trên từng máy: hỏi sổ xem máy này chạy pod nào |

Điểm hay bị vẽ sai: **scheduler và controller-manager không biết nhau**. Cả hai chỉ nói chuyện
riêng với API server. Sơ đồ đúng là hình sao, không phải một chuỗi chuyền tay.

## Ba hệ quả

**Xoá pod bằng tay thì nó mọc lại.** Bạn xoá cái đang chạy, nhưng sổ vẫn ghi 3. Vòng lặp thấy
lệch và dựng lại ngay. Muốn nó biến mất thật thì phải sửa Deployment.

**Sửa tay ở tầng dưới thì bị ghi đè.** Deployment sở hữu ReplicaSet, ReplicaSet sở hữu Pod. Sửa
thẳng ReplicaSet thì vòng lặp của Deployment kéo về. Ai sở hữu thì người đó thắng.

**Cụm không bao giờ ở trạng thái "xong".** Nó ở trạng thái đang được sửa, liên tục. Khả năng tự
lành không phải một tính năng ai đó bật lên — nó là hệ quả trực tiếp của việc mọi thứ đều là
vòng lặp.

## Mang gì đi

- Câu lệnh của bạn **ghi mong muốn**, không thi hành
- Mọi thành phần đều là vòng lặp: đọc, so, sửa
- Khi có sự cố, hỏi **sổ đang ghi gì** trước khi hỏi cái gì đang chạy
