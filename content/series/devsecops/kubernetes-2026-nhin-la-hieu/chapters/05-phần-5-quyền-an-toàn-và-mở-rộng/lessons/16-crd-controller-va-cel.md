---
id: 9f8ab27f-f46e-5b97-a2a6-f9db029a6c8f
title: 'Bài 16: Mở rộng Kubernetes — và webhook giờ đã có cách thay'
slug: crd-controller-va-cel
description: >-
  CRD một mình không làm gì. Và từ 1.36, cả hai pha kiểm duyệt viết được bằng CEL trong API server.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/p-qr9IUXDrU
sort_order: 2
section_title: 'Phần 5: Quyền, an toàn, và mở rộng'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/p-qr9IUXDrU"
    title="Bài 16: Mở rộng Kubernetes — và webhook giờ đã có cách thay"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Vì sao ai cũng rùng mình

Nói tới mở rộng Kubernetes là nghĩ ngay tới webhook: phải dựng một dịch vụ riêng, phải lo chứng
chỉ, và nếu nó chết thì cả cụm đứng. Tin tốt: **từ 1.36, phần lớn nhu cầu không cần webhook nữa.**

## CRD cho bạn cả bộ đồ nghề miễn phí

```yaml
kind: CustomResourceDefinition
spec:
  group: congty.vn
  names:
    kind: HangDoi
```

Khai xong là được: API server phục vụ nó, etcd lưu nó, `kubectl get`/`describe` chạy được, RBAC
áp lên nó, và cả kiểm hợp lệ theo lược đồ bạn định nghĩa.

## Nhưng CRD một mình không làm gì

Tạo một đối tượng thuộc loại mới ấy → nó **nằm im trong etcd**. Muốn có tác dụng thì phải có
**controller** theo dõi loại tài nguyên đó rồi hành động.

Mà controller là gì? Đúng cái **vòng lặp điều hoà** ở bài 1: đọc mong muốn, nhìn hiện trạng, so,
sửa. Không có gì mới.

> **CRD + controller = Operator.** Operator không phải một công nghệ riêng.

## Hai pha kiểm duyệt

Mỗi request vào API server đi qua hai pha:

1. **mutating — SỬA**: thêm nhãn, gắn sidecar, điền giá trị mặc định
2. **validating — KIỂM**: hợp lệ thì cho qua, không thì từ chối

Thứ tự luôn là sửa trước, kiểm sau — vì phải kiểm **cái đã sửa xong**.

## Bốn cái giá của webhook

| | |
|---|---|
| 1 | một dịch vụ nữa phải chạy — thêm thứ để triển khai, giám sát, nâng cấp |
| 2 | chứng chỉ phải xoay định kỳ, và nó luôn hết hạn vào lúc bất tiện nhất |
| 3 | mỗi lệnh khớp tốn thêm một chặng mạng → API server chậm đi |
| 4 | **điểm chết đơn lẻ** — `Fail` thì webhook chết là API server từ chối luôn; `Ignore` thì mất tác dụng đúng lúc cần nhất |

## Đường thoát cho pha kiểm

`ValidatingAdmissionPolicy` — luật viết bằng **CEL**, chạy thẳng trong API server:

```yaml
kind: ValidatingAdmissionPolicy
spec:
  validations:
    - expression: >
        object.spec.containers.all(c,
          has(c.resources.requests.memory))
```

Không dịch vụ · không chứng chỉ · không chặng mạng.

## Và từ 1.36, pha sửa cũng có

`MutatingAdmissionPolicy`. Cũng CEL, cũng chạy trong API server. Mấy việc rất phổ thông mà trước
đây buộc phải dựng webhook — tự động gắn nhãn theo namespace, điền một giá trị mặc định nếu thiếu
— giờ chỉ là một đối tượng yaml. **Không có gì để chết, cũng không có chứng chỉ nào để hết hạn
lúc 3 giờ sáng.**

## Khi nào vẫn cần webhook

- luật phải **gọi ra ngoài** — ví dụ hỏi một hệ thống quản lý cấu hình khác
- cần **trạng thái không nằm trong chính request đó**
- phải chạy một thuật toán mà **CEL không diễn đạt nổi**

Nhưng phần lớn webhook đang chạy ngoài đời chỉ làm mấy việc đơn giản, và mấy việc đó giờ chuyển
sang chính sách CEL được hết.

**Nguồn:** [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
