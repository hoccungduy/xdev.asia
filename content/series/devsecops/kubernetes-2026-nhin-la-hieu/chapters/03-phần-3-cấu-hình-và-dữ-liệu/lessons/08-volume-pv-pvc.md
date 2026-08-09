---
id: d2f08279-c4fc-5b53-9a32-d61d42fab0af
title: 'Bài 8: Volume, PV, PVC — ai mới là bên cấp'
slug: volume-pv-pvc
description: >-
  PVC là đơn xin, StorageClass là bên cấp, PV là cái được cấp. Và xoá PVC là mất luôn đĩa.
duration_minutes: 15
is_free: true
video_url: null
sort_order: 1
section_title: 'Phần 3: Cấu hình và dữ liệu'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Chuyện đã xảy ra với khá nhiều người

Khai một volume kiểu `emptyDir`, ghi dữ liệu vào, chạy ngon lành cả tuần. Rồi một hôm máy cần
bảo trì, pod được dựng lại ở máy khác, và toàn bộ dữ liệu biến mất. **Không lỗi nào được báo** —
vì nó chạy đúng như thiết kế.

## Vòng đời từng loại

| Loại | Sống bao lâu | Ghi chú |
|---|---|---|
| `emptyDir` | đúng bằng vòng đời Pod | pod chết là hết |
| `hostPath` | gắn vào một thư mục trên máy | dính chặt một máy + mở lỗ bảo mật khá to |
| ConfigMap / Secret | chỉ đọc | không phải chỗ chứa dữ liệu |
| **PersistentVolumeClaim** | **lâu hơn Pod** | đây mới là chỗ để dữ liệu thật |

## Ba tên gọi, hiểu theo kiểu hành chính

- **PersistentVolumeClaim** — cái **đơn xin**: tôi cần 20Gi, kiểu truy cập thế này
- **StorageClass** — **bên cấp**: nó biết gọi ai để tạo đĩa thật
- **PersistentVolume** — **cái được cấp**: một mẩu lưu trữ có thật

```yaml
kind: PersistentVolumeClaim
spec:
  accessModes: [ ReadWriteOnce ]
  storageClassName: ssd
  resources:
    requests: { storage: 20Gi }
```

Bạn viết đơn, hệ thống lo phần còn lại. Đó là **cấp phát động**.

## Một cái tên gây hiểu lầm nhiều năm

`ReadWriteOnce` **là một NODE**, không phải một pod. Hai pod cùng nằm trên một máy vẫn dùng chung
được cái đĩa đó — và có thể ghi đè lên nhau lúc nào không biết. Muốn đúng nghĩa một pod thì dùng
`ReadWriteOncePod`, có từ 1.29.

## Chỗ nguy hiểm nhất: chính sách thu hồi

Với cấp phát động, mặc định là **`Delete`**. Xoá PVC thì đĩa thật bên dưới bị xoá theo, cùng toàn
bộ dữ liệu. Mà xoá PVC thì dễ lắm: xoá nhầm namespace, gỡ nhầm một bản Helm, dọn dẹp cuối tuần.

StorageClass nào chứa **dữ liệu thật** thì đặt `reclaimPolicy: Retain`. Dọn tay tốn công hơn,
nhưng dọn tay thì còn cứu được.

## Một trường hay bị bỏ qua

`volumeBindingMode`. Để `Immediate` thì đĩa được tạo ngay lúc bạn viết đơn — trước khi ai biết
pod sẽ chạy ở máy nào. Với đĩa của nhà cung cấp đám mây thì đĩa gắn theo vùng, và nếu nó rơi vào
vùng khác với chỗ còn máy trống thì pod nằm `Pending` mãi. Đặt `WaitForFirstConsumer` thì hệ
thống chờ tới khi biết pod đi đâu rồi mới tạo đĩa đúng chỗ.

## Hai điều thực tế

- **Nới rộng được** — nếu StorageClass bật `allowVolumeExpansion`, chỉ cần sửa con số trong PVC
- **Thu nhỏ thì không.** Không có đường nào cả. Nên lúc chọn dung lượng ban đầu đừng chọn kiểu
  "cho chắc" — cái chắc đó bạn trả tiền hàng tháng, mãi mãi

## Hai thay đổi ở 1.36

- Volume kiểu **`gitRepo` đã bị gỡ hẳn** — còn dùng thì phải đổi sang init container tự clone
- **OCI volume đã ổn định** — gắn thẳng một image OCI vào pod như một volume chỉ đọc:

```yaml
volumes:
  - name: model
    image:
      reference: registry.congty.vn/models/rerank:2.1
```

Rất hợp cho mô hình, tập dữ liệu, bộ quy tắc — đổi mô hình là đổi một dòng tag, không phải dựng
lại image ứng dụng.

## Mang gì đi

- Nhớ đúng ba vai: **đơn xin · bên cấp · cái được cấp**
- Cấp phát động mặc định là **xoá đơn thì xoá luôn đĩa**
- `ReadWriteOnce` là **một node**, không phải một pod

**Nguồn:** [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
