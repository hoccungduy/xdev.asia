---
id: f08e4158-d4d3-51aa-bcf8-d23dace7fbce
title: 'Bài 4: Service không phải là load balancer'
slug: service-khong-phai-load-balancer
description: >-
  Không có tiến trình nào tên là Service. Nó là luật trên từng máy — và IPVS đã bị gỡ ở 1.36.
duration_minutes: 16
is_free: true
video_url: https://youtu.be/IqDjlnDBr3g
sort_order: 0
section_title: 'Phần 2: Đưa lưu lượng vào cụm'
course:
  id: 96d6e32d-791d-5d45-a901-e5a66dd85ee9
  title: 'Kubernetes 2026 nhìn là hiểu'
  slug: kubernetes-2026-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/IqDjlnDBr3g"
    title="Bài 4: Service không phải là load balancer"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

## Cái hộp không tồn tại

Tạo một Service, `curl` vào tên nó, request tới được pod. Nên ai cũng vẽ trong đầu một cái hộp
đứng giữa nhận request rồi chia cho các pod. **Cái hộp đó không tồn tại.** Không có tiến trình
nào tên là Service chạy ở bất cứ đâu trong cụm.

## Tự kiểm chứng

```
$ kubectl get svc web
NAME   TYPE        CLUSTER-IP    PORT(S)
web    ClusterIP   10.96.0.31    80/TCP

$ ping 10.96.0.31        # không ai trả lời
$ ss -ltn | grep 10.96   # không có gì nghe ở đây
```

ClusterIP là một **địa chỉ ảo**. Không ai lắng nghe, không máy nào mang nó. Nó chỉ là cái đích
để viết luật.

## Ai làm việc thật

`kube-proxy` chạy trên **từng máy**. Nó theo dõi API server, thấy Service nào có pod nào đứng
sau, rồi ghi vào bảng lọc gói tin của nhân:

```
-d 10.96.0.31 --dport 80  -j KUBE-SVC-WEB
KUBE-SVC-WEB  --probability 0.33  -j DNAT --to 10.42.1.7:8080
```

Việc đổi địa chỉ đích xảy ra **ngay trên máy nguồn**, trước khi gói tin rời máy. Không có chặng
trung gian nào. Điều này giải thích luôn ba chuyện: vì sao ping ClusterIP không được, vì sao
chẳng thấy log ở đâu, và vì sao gói tin không chậm thêm.

## Ai được đứng sau một Service

`endpoint controller` khớp selector với nhãn pod và ghi kết quả vào **EndpointSlice**. Chỉ pod
đang **Ready** mới được ghi vào. Đây mới là chỗ `readinessProbe` thật sự có tác dụng.

## Bốn loại, chồng lên nhau

- **ClusterIP** — chỉ dùng trong cụm
- **NodePort** — mở thêm một cổng trên mọi node
- **LoadBalancer** — nhờ nhà cung cấp dựng bộ cân tải bên ngoài trỏ vào NodePort đó
- **ExternalName** — không tạo luật nào, chỉ là một bản ghi CNAME

Và `clusterIP: None` → **headless**: DNS trả thẳng danh sách IP của pod. Đây là loại StatefulSet
dùng.

## Tin cần biết ngay: IPVS đã bị gỡ

Chế độ IPVS của kube-proxy bị đánh dấu lỗi thời ở **1.35** và **gỡ hẳn ở 1.36**. Một node chạy
kube-proxy 1.36 mà cấu hình vẫn ghi `mode: ipvs` thì Service **không định tuyến được gì**.
Không phải chậm — là không chạy.

```bash
kubectl -n kube-system get cm kube-proxy -o yaml | grep mode
```

Đường ra là chế độ **nftables**: ổn định từ 1.33, nhanh hơn iptables khi cụm lớn. Nhưng nó
**không phải mặc định**, và không có kế hoạch làm mặc định — mặc định vẫn là iptables. Sửa
ConfigMap của kube-proxy cho `mode: nftables` rồi khởi động lại lần lượt DaemonSet đó, **trước**
khi nâng lên 1.36.

## Một điều hay bị bỏ qua

Cân tải của kube-proxy là **ngẫu nhiên theo kết nối**, không phải luân phiên, và nó không biết
pod nào đang bận. Với HTTP/1.1 thì tạm ổn. Với kết nối giữ lâu — gRPC, WebSocket, HTTP/2 — thì
một kết nối dính một pod mãi mãi và tải lệch hẳn. Đó mới là lý do người ta đưa service mesh
hoặc cân tải phía client vào.

## Mang gì đi

- Service là **luật trên từng máy**, không phải một tiến trình
- Chỉ pod sẵn sàng mới có tên trong EndpointSlice
- Còn chạy IPVS thì chuyển sang nftables **trước khi** nâng lên 1.36

**Nguồn:** [nftables mode cho kube-proxy](https://kubernetes.io/blog/2025/02/28/nftables-kube-proxy/) · [Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)
