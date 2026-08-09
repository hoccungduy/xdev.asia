---
id: d81706c6-1e79-5399-9fa3-cdaf8c8be4ee
title: 'Bài 2: Pod không phải là container'
slug: pod-khong-phai-container
description: >-
  Pod là cái vỏ chia sẻ mạng, ổ đĩa và vòng đời. Và Pod trần thì không ai dựng lại.
duration_minutes: 15
is_free: true
video_url: https://youtu.be/0YqdGvhGzQM
sort_order: 1
section_title: 'Phần 1: Vì sao Kubernetes làm việc theo cách đó'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/0YqdGvhGzQM"
    title="Bài 2: Pod không phải là container"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Câu mở đầu của mọi hướng dẫn

"Pod là đơn vị nhỏ nhất của Kubernetes, và trong Pod có một container." Vế đầu đúng. Vế sau chỉ
là **trường hợp phổ biến**, không phải định nghĩa.

## Ba thứ dùng chung — đây mới là định nghĩa

| | |
|---|---|
| **một địa chỉ** | cả Pod chỉ có một IP; các container gọi nhau qua `localhost` |
| **một ổ đĩa** | khai một volume là cả hai cùng gắn được |
| **một vòng đời, một máy** | luôn xếp lên cùng một node, và cùng biến mất với nhau |

## Hệ quả bạn sẽ gặp ngay

Hai container trong cùng Pod **không thể cùng mở cổng 80**. Không phải Kubernetes cấm — chúng
nằm chung một không gian mạng, y như hai tiến trình trên cùng một máy.

```
listen tcp :80: bind: address already in use
```

## Khi nào mới nên cho ở ghép

Khi tách ra thì cả hai đều vô nghĩa. Ba khuôn mẫu:

- **init container** — chạy trước, xong hẳn rồi container chính mới khởi động
- **sidecar** — chạy song song suốt đời container chính
- **ambassador** — proxy cho mọi kết nối đi ra ngoài

Sidecar từng chỉ là một quy ước, và nó vỡ đúng lúc tắt: container chính xong việc mà sidecar
vẫn chạy thì Pod không bao giờ kết thúc. Từ Kubernetes 1.28 mới có sidecar thật — khai trong
`initContainers` với `restartPolicy: Always`; bật sẵn từ 1.29 và ổn định từ 1.33.

## Khuôn mẫu ngược lại

Hai container cần mở rộng theo hai nhịp khác nhau thì **đừng nhét chung**. Pod là đơn vị nhân
bản, nên nhân ba Pod là nhân ba mọi thứ bên trong. Không thể có ba bản web mà một bản sidecar.

## Vì sao gần như không ai viết `kind: Pod`

Pod tạo bằng tay là Pod **không có ai sở hữu**. Không vòng lặp nào ghi nó vào mong muốn của
mình, nên máy chết là nó chết theo và không có gì dựng lại.

Thêm một điều hay bị hiểu nhầm: **Pod không bao giờ chuyển sang máy khác**. Nó gắn vào một node
ngay lúc được xếp, và gắn là vĩnh viễn. Cái bạn thấy khi máy chết là Pod cũ mất hẳn và một Pod
hoàn toàn mới ra đời — tên khác, IP khác.

## Mang gì đi

- Pod là **cái vỏ**, không phải tên gọi khác của container
- Ghép chung chỉ khi tách ra thì vô nghĩa — và không bao giờ khi hai bên khác nhịp mở rộng
- Luôn để Deployment, Job hoặc DaemonSet đứng tên Pod

**Nguồn:** [Sidecar Containers](https://www.kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
