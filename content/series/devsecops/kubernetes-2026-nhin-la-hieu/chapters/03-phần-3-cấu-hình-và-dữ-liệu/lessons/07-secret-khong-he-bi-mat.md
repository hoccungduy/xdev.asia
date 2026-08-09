---
id: 46ad042b-9eb3-5213-af77-325c6fd980a6
title: 'Bài 7: Secret không hề bí mật'
slug: secret-khong-he-bi-mat
description: >-
  Mặc định chỉ là base64 trong etcd. Và quyền tạo Pod gần bằng quyền đọc mọi Secret trong namespace.
duration_minutes: 14
is_free: true
video_url: https://youtu.be/2CfCxFlKLJM
sort_order: 0
section_title: 'Phần 3: Cấu hình và dữ liệu'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/2CfCxFlKLJM"
    title="Bài 7: Secret không hề bí mật"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Tự gõ ba lệnh này

```
$ kubectl get secret db-cred -o yaml
data:
  password: c2lldUJhbWF0IUAyMDI2

$ echo 'c2lldUJhbWF0IUAyMDI2' | base64 -d
sieuBamat!@2026
```

Hai giây, từ lúc gõ tới lúc thấy mật khẩu nguyên văn.

## base64 không phải mã hoá

| Mã hoá | base64 |
|---|---|
| cần **khoá** mới đọc ngược lại được | **không có khoá nào cả** |
| không có khoá → chịu | sinh ra để nhét dữ liệu nhị phân vào một trường chữ |

Mặc định, Secret nằm trong etcd đúng ở dạng đó. Ai đọc được etcd là đọc được hết.

## Mã hoá lúc nghỉ — có, nhưng phải tự bật

Khai bằng một `EncryptionConfiguration` cho API server. Ở đây có một cái bẫy: nếu chọn kiểu đơn
giản nhất thì **khoá nằm ngay trên máy chạy control plane** — ai lấy được ổ đĩa máy đó thì có cả
hai thứ. Muốn chặt thì dùng nhà cung cấp KMS để khoá nằm ở chỗ khác.

## Chỗ làm tôi giật mình nhất

Bạn nghĩ chỉ người có quyền đọc Secret mới đọc được. Không hẳn.

**Ai tạo được Pod trong một namespace thì đọc được mọi Secret trong namespace đó.** Viết một Pod
gắn Secret ấy vào làm volume, rồi in ra. Hết.

```
create pods  ≈  get secrets (cả namespace)
```

Hệ quả cho cách chia quyền: **ranh giới tin cậy thật sự là namespace**, không phải loại tài
nguyên. Chia RBAC tinh vi trong cùng một namespace mà vẫn cho tạo Pod thì chỉ là cảm giác an toàn.

## ConfigMap so với Secret

Giống nhau nhiều hơn bạn tưởng: cùng cách gắn vào Pod, cùng giới hạn **1 MiB** (giới hạn của
etcd). Khác ở ba chỗ — Secret mã hoá base64, Secret không bị in ra ở một số chỗ, và **chúng là
hai loại tài nguyên riêng nên RBAC tách được**. Chỗ thứ ba mới là giá trị thật.

## Biến môi trường so với volume

Khác biệt này làm rất nhiều người mất buổi chiều:

- **biến môi trường** — đọc đúng một lần lúc container khởi động, sau đó không bao giờ đổi
- **volume** — kubelet đồng bộ lại, file trong container đổi theo, chỉ trễ một chút

Ngoại lệ phải nhớ: gắn bằng `subPath` thì **mất luôn** khả năng cập nhật đó.

## Một trường nhỏ đáng bật

```yaml
kind: ConfigMap
metadata:
  name: app-config-v7
immutable: true
```

Được hai thứ: không ai sửa nhầm một thứ đang có mười dịch vụ dùng, và kubelet thôi phải theo dõi
nó (đỡ tải cho API server ở cụm lớn). Muốn đổi thì tạo cái mới rồi trỏ Pod sang.

## Làm gì cho đúng

1. **Bật mã hoá lúc nghỉ** — và nếu được thì dùng KMS, đừng để khoá cạnh etcd
2. **Tách namespace theo ranh giới tin cậy**
3. **Cân nhắc để bí mật thật ở ngoài cụm**, trong một kho bí mật riêng, rồi đồng bộ vào — cách
   này còn được thêm hai thứ Kubernetes không có: xoay khoá tự động, và nhật ký ai đã đọc cái gì

## Mang gì đi

- Secret mặc định chỉ là base64 — đừng coi cái tên là một lời hứa
- Ranh giới thật là **namespace**
- Biến môi trường đọc một lần rồi thôi; muốn cập nhật thì gắn qua volume (và đừng dùng subPath)
