#!/usr/bin/env python3
"""Sinh series "Kubernetes 2026 nhìn là hiểu" — 17 bài — cho xdev.asia.

    python3 build-k8s-series.py

Id của series và từng bài suy ra bằng uuid5 từ slug, nên chạy lại không đổi id. Video id đọc
từ ``k8s-video-ids.json`` nếu có; chưa có thì bỏ khối nhúng chứ không để link chết.

Mọi khẳng định về phiên bản trong bài đều có nguồn dẫn ở cuối bài — đây là series về một thứ
đang đổi nhanh, nên chỗ nào là mốc phiên bản thì phải chỉ được ra ai công bố.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NS = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")
uid = lambda s: str(uuid.uuid5(NS, s))  # noqa: E731

SERIES_SLUG = "kubernetes-2026-nhin-la-hieu"
SERIES_TITLE = "Kubernetes 2026 nhìn là hiểu"
CATEGORY_DIR = "devsecops"
AUTHOR = ("019c9616-d2b4-713f-9b2c-40e2e92a05cf", "Duy Tran",
          "avatars/7e8eb5c6-4cac-455b-a701-4060f085d501.jpeg")
CATEGORY = ("019c9617-faa6-70d6-8679-ee4de1f177b3", "DevOps", "devops")
WHEN = "2026-08-09T02:00:00.000000Z"

SRC = {
    "v136": "[Kubernetes v1.36 “Haru”](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)",
    "nginx": "[Thông báo của Steering & Security Response Committee](https://www.kubernetes.io/blog/2026/01/29/ingress-nginx-statement/)",
    "google": "[Google Open Source — The End of an Era](https://opensource.googleblog.com/2026/02/the-end-of-an-era-transitioning-away-from-ingress-nginx.html)",
    "aws": "[AWS — hướng dẫn di trú khỏi NGINX Ingress](https://aws.amazon.com/blogs/networking-and-content-delivery/navigating-the-nginx-ingress-retirement-a-practical-guide-to-migration-on-aws)",
    "i2g": "[ingress2gateway 1.0](https://kubernetes.io/blog/2026/03/20/ingress2gateway-1-0-release)",
    "gw14": "[Gateway API 1.4](https://kubernetes.io/blog/2025/11/06/gateway-api-v1-4/)",
    "gw15": "[Gateway API 1.5](https://kubernetes.io/blog/2026/04/21/gateway-api-v1-5/)",
    "nft": "[nftables mode cho kube-proxy](https://kubernetes.io/blog/2025/02/28/nftables-kube-proxy/)",
    "sidecar": "[Sidecar Containers](https://www.kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)",
    "dra": "[Understanding Dynamic Resource Allocation — CNCF](https://www.cncf.io/blog/2026/07/01/understanding-dynamic-resource-allocation-in-kubernetes/)",
}

CHAPTERS = [
    ("Phần 1: Vì sao Kubernetes làm việc theo cách đó",
     "Ba tập nền. Hiểu sai chỗ này thì mọi thứ sau đó đều đọc nhầm."),
    ("Phần 2: Đưa lưu lượng vào cụm",
     "Phần gấp nhất của năm 2026 — ingress-nginx đã ngừng phát triển."),
    ("Phần 3: Cấu hình và dữ liệu",
     "Secret, ổ đĩa, và những chỗ mất dữ liệu mà không ai báo."),
    ("Phần 4: Giữ cho nó không sập",
     "Probe, tài nguyên, tự mở rộng, và bốn chỗ rơi request khi deploy."),
    ("Phần 5: Quyền, an toàn, và mở rộng",
     "RBAC, cách ly container, CEL thay webhook, và cách xin GPU đã đổi."),
]


def L(n, ch, slug, title, desc, minutes, body):
    return dict(n=n, ch=ch, slug=slug, title=title, desc=desc, minutes=minutes, body=body)


LESSONS = [
    L(1, 1, "vong-lap-dieu-hoa", "Bài 1: kubectl apply không ra lệnh cho cụm",
      "Câu lệnh chỉ ghi mong muốn vào sổ. Việc tạo container do một vòng lặp khác làm, và nó chạy mãi mãi.",
      14, """
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
"""),
    L(2, 1, "pod-khong-phai-container", "Bài 2: Pod không phải là container",
      "Pod là cái vỏ chia sẻ mạng, ổ đĩa và vòng đời. Và Pod trần thì không ai dựng lại.",
      15, """
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

**Nguồn:** {sidecar}
"""),
    L(3, 1, "deployment-va-replicaset", "Bài 3: Đổi một dòng image thì chuyện gì xảy ra",
      "Pod là bất biến. Deployment đẻ ra ReplicaSet mới, và hai cái sống song song lúc chuyển.",
      15, """
## Pod là bất biến

Sửa một dòng `image` trong yaml, apply, và pod chạy phiên bản mới. Nghe như Kubernetes vào tận
nơi thay ruột cái pod. Không phải. **Pod sinh ra với image nào thì chết với image đó.**

## Ba tầng, và chữ "duy nhất"

- **Deployment** giữ mong muốn: image nào, mấy bản, nhịp cập nhật ra sao
- **ReplicaSet** giữ đủ số pod khớp với **một khuôn duy nhất**
- **Pod** là cái chạy thật

Một ReplicaSet chỉ biết đúng một khuôn. Nên **đổi khuôn là phải đổi ReplicaSet**.

## Hai ReplicaSet sống song song

Khi bạn đổi image, Deployment không sửa ReplicaSet đang có — nó đẻ ra một cái mới. Rồi trong
mấy chục giây sau đó, cụm có hai ReplicaSet cùng lúc:

```
$ kubectl get rs
NAME        DESIRED   CURRENT   READY   AGE
web-7d4b          1         1       1    9d
web-9f2c          3         3       2    24s
```

Cột `DESIRED` của cái cũ tụt dần về 0, của cái mới bò lên.

## Hai nút vặn quyết định nhịp

| Trường | Mặc định | Nó nói gì |
|---|---|---|
| `maxSurge` | 25% | được phép **vượt** mức mong muốn bao nhiêu |
| `maxUnavailable` | 25% | được phép **thiếu** bao nhiêu |

`maxUnavailable: 0` thì không bao giờ tụt dưới mức đang có — đổi lại cụm phải còn chỗ trống.
`maxSurge: 0` thì không tốn thêm tài nguyên — đổi lại phải chịu thiếu người một lúc.

## Vì sao giữ ReplicaSet cũ

Vì đó là **nút quay lui**. `kubectl rollout undo` nghe rất oai, nhưng việc nó làm đơn giản đến
bất ngờ: co ReplicaSet mới về 0, phình ReplicaSet cũ trở lại. Không tải lại image, không dựng
gì mới. Vì thế quay lui nhanh hơn hẳn cập nhật — đừng ngại dùng.

Mặc định giữ 10 bản, chỉnh bằng `revisionHistoryLimit`.

## Hai chi tiết hay vấp

**`pod-template-hash`** — nhãn mà Deployment tự dán, là mã băm của khuôn pod. Khuôn đổi một ký
tự thì mã băm đổi, thành một ReplicaSet khác. Đừng tự đặt nhãn này bằng tay.

**`selector` là bất biến.** Từ `apps/v1` không sửa được. Lý do rất thực tế: đổi selector thì đám
pod đang chạy thành mồ côi, không ReplicaSet nào nhận, và nằm lại ăn tài nguyên mãi mãi. Muốn
đổi thì chỉ có một đường — xoá Deployment rồi tạo lại. Nên nghĩ kỹ nhãn ngay từ ngày đầu.

## Mang gì đi

- Đổi image nghĩa là **thay pod**, không phải sửa pod
- Mỗi khuôn có một ReplicaSet riêng; lúc chuyển thì hai cái sống song song
- Quay lui chỉ là phình lại cái cũ — nhanh, và nên dùng
"""),
    L(4, 2, "service-khong-phai-load-balancer", "Bài 4: Service không phải là load balancer",
      "Không có tiến trình nào tên là Service. Nó là luật trên từng máy — và IPVS đã bị gỡ ở 1.36.",
      16, """
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

**Nguồn:** {nft} · {v136}
"""),
    L(5, 2, "ingress-nginx-da-dong-bang", "Bài 5: ingress-nginx đã đóng băng — việc phải làm",
      "Tháng 3/2026 dự án ngừng phát triển, repo chỉ đọc, không còn vá bảo mật. Và nó đứng ngay ở cửa vào.",
      13, """
> **Bài này giao việc, không dạy lý thuyết.** Nếu cụm của bạn đang chạy ingress-nginx thì đây
> là thứ nên đọc trước mọi thứ khác trong series.

## Chuyện đã xảy ra

Tháng 3 năm 2026, dự án `ingress-nginx` ngừng phát triển. Repo chuyển sang **chỉ đọc**:

- không bản phát hành mới
- không sửa lỗi
- **không vá bảo mật**

Theo hướng dẫn di trú của AWS, nó đang đứng ở cửa của **khoảng một nửa** số cụm Kubernetes.
(Con số này là ước tính trong tài liệu đó, không phải phép đo của tôi.)

## Nói cho rõ: cái gì ngừng, cái gì không

| Vẫn còn | Đã ngừng |
|---|---|
| **đối tượng Ingress** — không bị xoá khỏi API, cụm vẫn chấp nhận | **ingress-nginx**, cái controller đọc nó |

Nhưng bản thân Ingress cũng đã **đóng băng tính năng** từ lâu — mọi thứ mới đều đi vào Gateway
API. Nói cách khác: bản mô tả vẫn còn, người thi hành thì nghỉ.

## Vì sao phải dừng

Theo thông báo của Steering Committee và Security Response Committee, lý do rất đời: dự án chạy
gần như hoàn toàn bằng **tình nguyện**, trong khi bề mặt tấn công của nó rất rộng — nó nhận
annotation do người dùng viết rồi sinh ra file cấu hình nginx thật để chạy, ở đúng cửa vào cụm.
Số người bảo trì không đủ để canh một thứ như thế. Ngừng có kiểm soát vẫn hơn để nó mục dần.

## Rủi ro của việc ngồi yên

Hôm nay cụm vẫn chạy bình thường — đó là sự thật. Nhưng **lỗ hổng tiếp theo sẽ không có bản
vá**. Và vì nó nằm ở cửa vào, nó là thứ người ngoài chạm tới đầu tiên, trước cả tường lửa ứng
dụng và trước cả mã của bạn.

Đây không phải chuyện thiếu tính năng. Đây là **một bề mặt tấn công không còn ai canh**.

## Ba đường ra

| | Đường | Cái giá |
|---|---|---|
| 1 | **Chuyển sang Gateway API** *(khuyến nghị)* | công sức lớn nhất, nhưng là đường duy nhất đi tới đâu đó |
| 2 | Đổi sang một ingress controller khác còn được bảo trì | nhẹ hơn, nhưng vẫn ở trên một API đã đóng băng |
| 3 | Mua hỗ trợ thương mại cho bản đã đóng băng | mua thêm thời gian, không giải quyết gì |

Không chọn cũng là một lựa chọn — và là lựa chọn tệ nhất trong bốn cái.

## Công cụ dịch sẵn

`ingress2gateway` bản 1.0 ra tháng 3/2026, dịch được hơn 30 annotation. Nó đọc đám Ingress đang
có rồi sinh ra HTTPRoute tương ứng. **Nhưng nó không phải nút bấm một phát là xong**: nó dịch
phần cấu trúc — host, path, backend. Còn chỗ nào bạn dùng annotation riêng của nginx (rewrite,
auth, rate limit, snippet) thì vẫn phải xem lại bằng mắt.

## Việc làm ngay tuần này

```bash
# 1. đếm xem cụm đang có bao nhiêu Ingress
kubectl get ingress -A --no-headers | wc -l

# 2. chạy thử bản dịch, chỉ in ra màn hình
ingress2gateway print --input-file ingress.yaml
```

3. Chọn đường đi và **ghi hẳn một cái ngày vào lịch**.

Việc tệ nhất lúc này là không làm gì rồi quên nó đi.

**Nguồn:** {nginx} · {google} · {aws} · {i2g}
"""),
    L(6, 2, "gateway-api", "Bài 6: Gateway API không phải Ingress viết lại",
      "Điểm chính không nằm ở cú pháp mà ở chỗ chia việc cho ai — ba tài nguyên cho ba vai.",
      16, """
## Hiểu nhầm tốn kém nhất

Nếu bạn nghĩ Gateway API chỉ là Ingress viết lại cho đẹp thì sẽ di trú sai ngay từ đầu: dịch
xong cú pháp mà giữ nguyên cách chia quyền. **Điểm chính của nó là chia việc cho ba người khác
nhau.**

## Vấn đề thật của Ingress

Đối tượng Ingress chỉ mô tả được những thứ cơ bản: tên miền, đường dẫn, tới Service nào. Mọi thứ
nhỉnh hơn đều phải nhét vào annotation:

```yaml
metadata:
  annotations:
    nginx.ingress.k8s.io/rewrite-target: /$2
    nginx.ingress.k8s.io/canary-weight: "10"
    nginx.ingress.k8s.io/limit-rps: "20"
```

Mà annotation là **chữ tự do**: cụm không kiểm tra được gì (sai chính tả thì im lặng bỏ qua),
mỗi controller hiểu một kiểu, và đổi controller là viết lại từ đầu.

## Ba tài nguyên, ba chủ sở hữu

| Tài nguyên | Nó khai gì | Ai sở hữu |
|---|---|---|
| `GatewayClass` | loại hạ tầng nào sẽ chạy — y như StorageClass | bên cung cấp hạ tầng |
| `Gateway` | mở cổng nào, chứng chỉ nào, cho ai gắn route vào | đội vận hành cụm |
| `HTTPRoute` | đường dẫn của tôi đi tới Service của tôi | **đội ứng dụng** |

## Vì sao đó là chỗ đáng tiền

Đây là chuyện tổ chức, không phải chuyện kỹ thuật. Với Ingress, muốn đổi một đường dẫn thì phải
sửa cái đối tượng nằm chung với cấu hình TLS và cửa vào. Nên hoặc đội ứng dụng được quyền động
vào cửa vào (đáng sợ), hoặc mọi thay đổi nhỏ đều xếp hàng qua đội hạ tầng (nút thắt cổ chai).
Gateway API cắt đúng chỗ đó.

## Cú pháp: từ chuỗi sang trường có kiểu

```yaml
rules:
  - backendRefs:
      - name: web-v1
        weight: 90
      - name: web-v2
        weight: 10
```

Chia tải theo trọng số, khớp header, chuyển hướng, viết lại đường dẫn, nhân bản request — tất cả
là **trường có kiểu**, API server từ chối ngay nếu sai. Không còn chuỗi ký tự cầu may.

## Chỗ bạn sẽ vấp: đi qua namespace

Gateway thường nằm ở namespace của đội hạ tầng, HTTPRoute nằm ở namespace ứng dụng. Muốn gắn
được thì phải có **cả hai phía đồng ý**: Gateway khai `allowedRoutes`, và nếu route trỏ tới
Service ở namespace khác nữa thì cần thêm `ReferenceGrant`. Nghe phiền, nhưng đó đúng là cái
ngăn một đội vô tình cướp tên miền của đội khác.

## Phiên bản và hai kênh

Gateway API **không nằm sẵn** trong Kubernetes — nó là một bộ CRD phải tự cài.

- **v1.4** — GA 06/10/2025, đưa `BackendTLSPolicy` vào kênh chuẩn (trước đó không có cách khai
  báo chặng từ Gateway xuống pod phải mã hoá)
- **v1.5** — ra năm 2026, chủ yếu đẩy tính năng thử nghiệm sang kênh chuẩn

Hai kênh: **Standard** ổn định, **Experimental** còn đổi được. Đừng đem Experimental lên môi
trường thật.

## Di trú thế nào

Đừng đổi hết trong một đêm. Dựng Gateway **bên cạnh** Ingress đang chạy, chuyển từng tên miền
một, theo dõi vài ngày, rồi mới gỡ cái cũ. Chuyển từng host thì lúc có chuyện bạn biết ngay là
host nào.

## Mang gì đi

- Điểm chính là **ba tài nguyên cho ba vai**
- Annotation thành trường có kiểu — cụm kiểm tra được, và không dính vào một bản hiện thực
- Là CRD phải tự cài; chỉ dùng Standard cho môi trường thật

**Nguồn:** {gw14} · {gw15}
"""),
    L(7, 3, "secret-khong-he-bi-mat", "Bài 7: Secret không hề bí mật",
      "Mặc định chỉ là base64 trong etcd. Và quyền tạo Pod gần bằng quyền đọc mọi Secret trong namespace.",
      14, """
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
"""),
    L(8, 3, "volume-pv-pvc", "Bài 8: Volume, PV, PVC — ai mới là bên cấp",
      "PVC là đơn xin, StorageClass là bên cấp, PV là cái được cấp. Và xoá PVC là mất luôn đĩa.",
      15, """
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

**Nguồn:** {v136}
"""),
    L(9, 3, "statefulset", "Bài 9: StatefulSet — khi nào mới thật sự cần",
      "Nó cho bạn danh tính, đúng ba thứ. Không nhân bản, không bầu leader, không sao lưu.",
      14, """
## Một câu đã thành phản xạ

"Có cơ sở dữ liệu thì phải dùng StatefulSet." Tôi cũng từng tin thế, và đã dựng vài cái mà lẽ ra
chỉ cần Deployment. Sự thật là StatefulSet giải một bài toán **rất hẹp**, và cái tên của nó hứa
nhiều hơn cái nó làm.

## Nó cho bạn đúng ba thứ

| | |
|---|---|
| **tên ổn định** | `web-0`, `web-1`, `web-2` — chết đi dựng lại vẫn đúng tên đó |
| **DNS riêng từng pod** | gọi thẳng được, nhờ một Service kiểu headless |
| **đĩa riêng theo tên** | đĩa luôn quay lại đúng pod mang tên đó |

Gộp lại thành một chữ: **danh tính**. Chấm hết.

## Cái nó KHÔNG làm

- ✕ nhân bản dữ liệu
- ✕ bầu leader
- ✕ sao lưu
- ✕ chuyển đổi dự phòng khi một bản chết

Toàn bộ những việc khó ấy vẫn là việc của **ứng dụng bên trong**. Kubernetes chỉ đảm bảo pod số
0 luôn là pod số 0 và luôn tìm lại được ổ đĩa của nó.

## Cần và không cần

**Cần** khi ứng dụng thật sự dựa vào danh tính: cụm cơ sở dữ liệu mà các bản phải biết tên nhau
để đồng bộ, hoặc hệ đồng thuận kiểu etcd/Kafka/ZooKeeper nơi mỗi bản là một thành viên có số hiệu.

**Không cần** khi: chỉ có một bản duy nhất, các bản không cần biết nhau, hoặc dữ liệu để hết ở
ngoài cụm. Một bản duy nhất có đĩa riêng? **Deployment với một PVC là đủ**, và đơn giản hơn nhiều.

## Thứ tự — con dao hai lưỡi

| | |
|---|---|
| tạo | `0 → 1 → 2`, pod trước sẵn sàng thì pod sau mới được tạo |
| xoá | `2 → 1 → 0` |
| cập nhật | `2 → 1 → 0`, từ số cao nhất xuống |

Lưỡi thứ nhất: pod 0 kẹt không lên nổi thì **cả cụm đứng im chờ nó**. Lưỡi thứ hai: trường
`partition` cho thả bản mới từng phần kiểu canary, không cần công cụ gì thêm.

## Cái bẫy đáng nhớ

**Xoá StatefulSet thì mặc định các ổ đĩa không bị xoá theo.** Thu nhỏ số bản cũng vậy: pod biến
mất nhưng PVC vẫn nằm đó.

- *Mặt được:* xoá nhầm vẫn còn dữ liệu để gắn lại
- *Mặt trái:* hoá đơn cứ tăng vì đám đĩa mồ côi không ai dọn

Có một trường cấu hình để đổi hành vi này — nhưng nghĩ kỹ trước khi bật.

## Nói thẳng một chuyện thực tế

Định chạy cơ sở dữ liệu thật trên Kubernetes? **Đừng tự viết StatefulSet từ đầu.** Dùng Operator
do chính đội làm ra cơ sở dữ liệu đó viết — nó lo giúp những phần StatefulSet không lo: sao lưu,
nâng cấp phiên bản, chuyển đổi dự phòng, bầu leader. Hoặc thẳng thắn hơn: dùng dịch vụ quản lý
và dành sức cho phần ứng dụng của mình.

## Bảng quyết định

| Tình huống | Chọn |
|---|---|
| một bản, có đĩa riêng | Deployment + một PVC |
| nhiều bản, không cần biết nhau | Deployment |
| nhiều bản, phải biết tên nhau | StatefulSet |
| database thật — cần sao lưu, chuyển đổi dự phòng | Operator, hoặc dịch vụ quản lý |

Đừng chọn StatefulSet chỉ vì trong đầu có chữ "trạng thái".
"""),
    L(10, 4, "ba-loai-probe", "Bài 10: Ba loại probe, và cách đặt sai làm sập chính mình",
      "Đặt liveness giống readiness là cách kinh điển tự tạo ra một vòng xoáy chết.",
      15, """
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
"""),
    L(11, 4, "requests-limits-qos", "Bài 11: requests, limits, và ai bị giết trước",
      "CPU nén được nên vượt limit là bị bóp; bộ nhớ không nén được nên vượt là bị giết.",
      16, """
## Một thói quen nghe rất vô hại

"Đặt limit cao lên cho chắc — thừa còn hơn thiếu."

Với **CPU**, cái "chắc" đó làm ứng dụng chậm đi ngay cả khi máy đang rảnh. Với **bộ nhớ**, nó
quyết định pod nào bị giết trước lúc máy hết chỗ.

## Hai con số, hai thế giới

```yaml
resources:
  requests:      # scheduler nhìn con số này
    cpu: 200m    # → để quyết pod này bỏ lên MÁY NÀO
    memory: 256Mi
  limits:        # nhân hệ điều hành nhìn con số này
    cpu: 1       # → để CHẶN CONTAINER LẠI lúc đang chạy
    memory: 512Mi
```

Một cái quyết định bạn **ngồi ở đâu**. Một cái quyết định bạn **được ăn bao nhiêu**.

## Hệ quả hay bị bỏ qua

Scheduler chỉ cộng `requests`, nó không quan tâm `limits`. Nên requests thấp mà limits cao thì
trên giấy máy còn rất nhiều chỗ, nhưng thực tế đám container đang chạy có thể ăn nhiều hơn hẳn
cái máy có. Đó là **cam kết vượt mức** — không sai, nhiều nơi cố tình làm vậy để tiết kiệm, nhưng
phải *biết* là mình đang làm.

## Chỗ quan trọng nhất

| | Vượt limit thì sao |
|---|---|
| **CPU** — nén được | bị **bóp lại**, bị bắt ngồi chờ. Container không chết |
| **Bộ nhớ** — không nén được | bị **giết ngay**. Mã thoát `137`, dòng chữ `OOMKilled` |

Cùng một chữ `limit` trong YAML, hai hậu quả khác nhau hoàn toàn.

## Vì sao limit CPU cao lại làm chậm

Vì nhân hệ điều hành không tính trung bình cả giây. Nó chia thời gian thành **từng chu kỳ rất
ngắn** (cỡ 1/10 giây), và trong mỗi chu kỳ bạn chỉ được dùng đúng phần đã khai. Dùng hết là ngồi
chờ tới chu kỳ sau.

Nên một ứng dụng có nhịp **giật cục** — nhận một request rồi xử lý dồn một cái — hoàn toàn có thể
vừa bị bóp liên tục vừa hiện mức sử dụng trung bình rất thấp. Thấy biểu đồ báo CPU 20% mà độ trễ
đuôi xấu thì hãy nghi ngay chỗ này.

## Ba lớp QoS, và thứ tự bị đuổi

| Lớp | Điều kiện | Bị đuổi |
|---|---|---|
| `Guaranteed` | requests = limits, cho **cả** cpu lẫn bộ nhớ, ở **mọi** container | đi sau cùng |
| `Burstable` | có khai, nhưng không bằng nhau | đi thứ hai — nếu đang dùng quá phần đã khai |
| `BestEffort` | **không khai gì cả** | đi **đầu tiên** |

Nói cho gọn: mấy pod bạn quên khai tài nguyên chính là mấy pod chết đầu tiên.

## Bộ quy tắc thực dụng

| | |
|---|---|
| bộ nhớ · requests | luôn khai |
| bộ nhớ · limits | đặt **bằng** requests — bộ nhớ không nén được, để hở chỉ chuốc bất ngờ |
| cpu · requests | luôn khai — đó là thứ giữ chỗ cho bạn |
| cpu · limits | cân nhắc kỹ; nhiều đội chọn **không đặt** để ứng dụng mượn được lúc rảnh |

Chọn không đặt limit CPU thì đổi lại: cụm phải có chỗ đệm và phải theo dõi được. Không có đáp án
đúng cho mọi nơi, nhưng có một đáp án chắc chắn sai: **đặt bừa một con số rồi quên nó đi**.

## Đọc dấu hiệu lúc có sự cố

| Triệu chứng | Nguyên nhân | Làm gì |
|---|---|---|
| bị giết đột ngột · mã 137 · log cụt ngang | bộ nhớ | tăng limit bộ nhớ, hoặc tìm chỗ rò |
| không chết · độ trễ đuôi xấu · CPU trung bình thấp | bị bóp CPU | nhìn số đo throttling của cgroup, **đừng nhìn mức sử dụng** |

Nhầm giữa hai cái này thì bạn sửa nhầm chỗ cả buổi.
"""),
    L(12, 4, "ba-tang-tu-mo-rong", "Bài 12: Ba tầng tự mở rộng, và cái bẫy ở mức 0",
      "HPA về 0 bật sẵn từ 1.36 — nhưng ở mức 0 thì HPA mù, và không thể tự bật lại bằng CPU.",
      15, """
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

**Nguồn:** {v136}
"""),
    L(13, 4, "rollout-va-pdb", "Bài 13: Cập nhật cuốn chiếu vẫn rơi request",
      "Bốn chỗ rơi, và cả bốn đều là chỗ Kubernetes cố tình không tự lo.",
      15, """
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
"""),
    L(14, 5, "rbac-va-serviceaccount", "Bài 14: RBAC — tai nạn đến từ ServiceAccount",
      "Mỗi pod cũng là một danh tính. Và động từ list gần bằng quyền đọc nội dung.",
      14, """
## Chỗ tai nạn thật sự xảy ra

Nhắc tới RBAC là mọi người nghĩ tới phân quyền cho **người**. Nhưng phần lớn tai nạn về quyền
trong Kubernetes đến từ **ServiceAccount** — danh tính mà chính mấy cái pod của bạn đang mang.

## Bốn đối tượng = tích của hai trục

| | Định nghĩa quyền | Gắn quyền |
|---|---|---|
| trong **một namespace** | `Role` | `RoleBinding` |
| phạm vi **cả cụm** | `ClusterRole` | `ClusterRoleBinding` |

Có chữ `Cluster` ở đầu thì phạm vi cả cụm. Không có thì gói trong một namespace.

**Cách kết hợp ít người để ý:** `RoleBinding` hoàn toàn được phép trỏ vào một `ClusterRole`. Định
nghĩa quyền đúng một lần ở mức cụm, rồi gắn vào từng namespace riêng lẻ — quyền chỉ có hiệu lực
trong namespace đó.

## Token nằm sẵn trong container

Mỗi pod chạy dưới một ServiceAccount; không khai thì dùng `default`. Và mặc định, Kubernetes gắn
sẵn một token của tài khoản ấy vào container:

```
/var/run/secrets/kubernetes.io/serviceaccount/token
```

Nghĩa là mã của bạn — hoặc **bất cứ thứ gì chạy trong container đó** — đều gọi được API server
với danh tính ấy. Pod không cần gọi API server thì tắt đi:

```yaml
spec:
  automountServiceAccountToken: false
```

Một dòng, và nó bỏ hẳn một đường tấn công.

## Chỗ tai nạn 1: động từ `list`

Bạn nghĩ `list` chỉ liệt kê tên? Không. Khi API server trả về danh sách, nó trả về **nguyên cả
đối tượng, kèm toàn bộ nội dung**. Nên cho quyền `list` trên secret, trên thực tế, gần bằng cho
quyền đọc nội dung mọi secret trong phạm vi đó. Muốn cho xem tên thôi thì RBAC không làm được.

## Chỗ tai nạn 2: RBAC chỉ cộng

Không tồn tại quy tắc kiểu "cho phép mọi thứ **trừ** cái này". Chỉ cần **một binding rộng tay** ở
đâu đó là mọi quy tắc siết chặt bạn viết chỗ khác đều thành vô nghĩa. Và cái binding đó thường
không phải do bạn viết, mà do một biểu đồ Helm nào đó cài vào từ năm ngoái.

## Chỗ tai nạn 3: `cluster-admin` gắn vào ServiceAccount

Rất nhiều bản cài mặc định làm thế cho tiện. Hậu quả: chỉ cần **một lỗ hổng thực thi mã** trong
đúng cái pod đó là người tấn công có ngay quyền quản trị toàn cụm. Không có bước leo thang nào —
token đã nằm sẵn trong container, và nó đã là quyền cao nhất.

Đây là chỗ đầu tiên tôi nhìn khi rà một cụm lạ.

## Lệnh nên thuộc

```bash
kubectl auth can-i --list \
  --as=system:serviceaccount:thanh-toan:api-worker
```

Đừng đọc YAML rồi tự suy ra — quyền cộng dồn từ nhiều binding và bạn sẽ bỏ sót, nhất là mấy cái
do công cụ cài vào. Hỏi thẳng API server thì nó trả lời thật.

## Danh sách siết

1. Có ServiceAccount nào đang gắn `cluster-admin` không — và nó có thật sự cần không?
2. Pod nào không gọi API server thì tắt automount token đi
3. Soi lại mấy động từ rộng như `list`, `watch` trên secret
4. **Mỗi ứng dụng một ServiceAccount riêng** — dùng chung `default` thì không bao giờ siết được
"""),
    L(15, 5, "pod-security-va-networkpolicy", "Bài 15: Container tưởng đã cách ly",
      "root trong container là root thật, cho tới khi bật user namespace. Và NetworkPolicy có thể im lặng không chặn gì.",
      16, """
## Container không phải máy ảo

Nó **không có nhân riêng**. Nó dùng chung đúng cái nhân của máy chủ, chỉ được cho nhìn thấy một
góc hẹp hơn.

| | Máy ảo | Container |
|---|---|---|
| nhân | **riêng** | **của máy chủ — dùng chung** |

## Hệ quả đáng sợ

Nếu tiến trình trong container chạy bằng root thì cái root đó, ở góc nhìn của nhân, chính là
**uid 0** — cùng một con số với root của máy chủ. Chỉ cần một lỗ hổng cho phép thoát ra khỏi
container là có ngay quyền root **trên chính cái máy đó**. Không phải root giả. Root thật.

## Cách chữa gốc rễ: user namespace

Vừa lên ổn định ở **1.36**. Ý tưởng rất gọn — **ánh xạ lại mã người dùng**: bên trong container
vẫn là 0, vẫn là root, mọi thứ chạy bình thường; nhưng ở ngoài, nhân nhìn thấy nó là một mã người
dùng thường không có quyền gì.

```yaml
spec:
  hostUsers: false
```

## Tầng chặn phía trên: Pod Security Admission

`PodSecurityPolicy` đã bị gỡ khỏi Kubernetes từ lâu. Thay vào đó là **nhãn trên namespace**:

```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

Ba mức: `privileged` (không chặn gì) · `baseline` (chặn những thứ nguy hiểm rõ ràng) ·
`restricted` (siết chặt, buộc chạy không phải root).

Ba chế độ: `enforce` (chặn thật) · `audit` (ghi lại) · `warn` (cảnh báo lúc apply).

**Mẹo dùng:** bật `warn` và `audit` ở mức `restricted` trước, xem log vài tuần, rồi mới bật
`enforce`.

## Còn mạng thì sao

Mặc định trong Kubernetes, **mọi pod nói chuyện được với mọi pod** — không chỉ trong cùng
namespace mà là toàn bộ cụm. Cái pod nhỏ xíu chạy công việc định kỳ, về mặt mạng, gọi thẳng được
vào cơ sở dữ liệu của hệ thống thanh toán.

## NetworkPolicy hoạt động hơi ngược trực giác

- Chưa có policy nào chọn tới một pod → pod đó **mở toang**
- Có một policy chọn nó → pod đó lập tức **từ chối mặc định** cho chiều được chọn

Nghĩa là viết policy **đầu tiên** cho một pod là một hành động khá lớn — nó lật cả trạng thái mặc
định của pod đó, chứ không phải thêm một luật nhỏ.

## Cái bẫy lớn nhất

NetworkPolicy chỉ là một **bản mô tả**. Thứ thi hành nó là **plugin mạng** của cụm. Nếu plugin
không hỗ trợ thì policy vẫn tạo được:

```
$ kubectl apply -f deny-all.yaml
networkpolicy.networking.k8s.io/deny-all created
```

…và nó **không chặn một gói tin nào**. Không lỗi, không cảnh báo, hoàn toàn im lặng.

**Việc bắt buộc sau khi viết policy đầu tiên:** mở một pod, thử gọi sang chỗ lẽ ra phải bị chặn,
xem nó có bị chặn thật không. Kiểm bằng cách thử, đừng đọc tài liệu.

## Năm dòng nên là mặc định

```yaml
securityContext:
  runAsNonRoot: true
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

Năm dòng này chặn phần lớn những đường tấn công phổ thông, và với ứng dụng viết tử tế thì gần như
không phải sửa gì.

**Nguồn:** {v136}
"""),
    L(16, 5, "crd-controller-va-cel", "Bài 16: Mở rộng Kubernetes — và webhook giờ đã có cách thay",
      "CRD một mình không làm gì. Và từ 1.36, cả hai pha kiểm duyệt viết được bằng CEL trong API server.",
      15, """
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

**Nguồn:** {v136}
"""),
    L(17, 5, "dra-xin-gpu-theo-thuoc-tinh", "Bài 17: DRA — cách xin GPU đã đổi hẳn",
      "Xin bằng một con số nguyên là xin mù. DRA xin theo thuộc tính — nhưng ổn định ≠ driver sẵn sàng.",
      15, """
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

**Nguồn:** {dra} · {v136}
"""),
]


def video_ids():
    path = ROOT / "k8s-video-ids.json"
    return json.loads(path.read_text()) if path.exists() else {}


def embed(vid, title):
    if not vid:
        return ""
    return f"""## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#080C18;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/{vid}"
    title="{title}"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

"""


def main():
    ids = video_ids()
    base = ROOT / "content" / "series" / CATEGORY_DIR / SERIES_SLUG
    sections = []

    for ci, (ch_title, ch_desc) in enumerate(CHAPTERS, start=1):
        lessons = [x for x in LESSONS if x["ch"] == ci]
        ch_slug = f"{ci:02d}-" + ch_title.lower().replace(":", "").replace(" ", "-").replace(",", "")
        for ci_l, lesson in enumerate(lessons):
            vid = ids.get(str(lesson["n"]), "")
            body = lesson["body"]
            for k, v in SRC.items():
                body = body.replace("{" + k + "}", v)
            md = f"""---
id: {uid(lesson['slug'])}
title: '{lesson['title']}'
slug: {lesson['slug']}
description: >-
  {lesson['desc']}
duration_minutes: {lesson['minutes']}
is_free: true
{f'video_url: https://youtu.be/{vid}' if vid else 'video_url: null'}
sort_order: {ci_l}
section_title: '{ch_title}'
course:
  id: {uid(SERIES_SLUG)}
  title: '{SERIES_TITLE}'
  slug: {SERIES_SLUG}
---

{embed(vid, lesson['title'])}{body.strip()}
"""
            out = base / "chapters" / ch_slug / "lessons" / f"{lesson['n']:02d}-{lesson['slug']}.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf8")

        rows = ", ".join(
            "{" + f"id: {uid(x['slug'])}, title: '{x['title']}', slug: {x['slug']}, "
            f"description: '{x['desc']}', duration_minutes: {x['minutes']}, is_free: true, "
            f"sort_order: {i}"
            + (f", video_url: https://youtu.be/{ids[str(x['n'])]}" if ids.get(str(x["n"])) else "")
            + "}"
            for i, x in enumerate(lessons)
        )
        sections.append(
            "{" + f"id: section-{ci:02d}, title: '{ch_title}', description: '{ch_desc}', "
            f"sort_order: {ci}, lessons: [{rows}]" + "}"
        )

    index_md = f"""---
id: {uid(SERIES_SLUG)}
title: '{SERIES_TITLE}'
slug: {SERIES_SLUG}
description: >-
  Mười bảy bài về Kubernetes, dựng lại theo đúng tình hình 2026 — vì ba mốc trong năm nay làm
  phần lớn giáo trình đang lưu hành trở thành sai. Mỗi bài đúng một chỗ "tưởng đúng mà sai".
featured_image: images/blog/{SERIES_SLUG}/cover.png
level: intermediate
duration_hours: 4
lesson_count: {len(LESSONS)}
price: '0.00'
is_free: true
view_count: 0
average_rating: '0.00'
review_count: 0
enrollment_count: 0
meta: null
published_at: '{WHEN}'
created_at: '{WHEN}'
author: {{id: {AUTHOR[0]}, name: {AUTHOR[1]}, avatar: {AUTHOR[2]}}}
category: {{id: {CATEGORY[0]}, name: {CATEGORY[1]}, slug: {CATEGORY[2]}}}
tags: [{{name: Kubernetes, slug: kubernetes}}, {{name: DevOps, slug: devops}}, {{name: Gateway API, slug: gateway-api}}, {{name: Hạ tầng, slug: ha-tang}}, {{name: Container, slug: container}}, {{name: SRE, slug: sre}}, {{name: bảo mật, slug: bao-mat}}, {{name: DRA, slug: dra}}]
sections: [{", ".join(sections)}]
---

## Vì sao làm lại, không chép giáo trình cũ

Ba mốc trong năm 2026 làm phần lớn hướng dẫn Kubernetes đang lưu hành trở thành sai:

| Mốc | Việc | Hệ quả |
|---|---|---|
| tháng 3/2026 | **ingress-nginx ngừng phát triển**, repo chỉ đọc, không còn vá bảo mật | Mọi bài dạy "cài ingress-nginx" giờ dạy người ta cài một thứ không ai vá nữa |
| tháng 3/2026 | **ingress2gateway 1.0**, dịch được hơn 30 annotation | Đường di trú đã có, không còn cớ hoãn |
| 22/04/2026 | **Kubernetes v1.36 "Haru"** | Gỡ `gitRepo` volume, gỡ **chế độ IPVS của kube-proxy**; DRA, User Namespaces, MutatingAdmissionPolicy, OCI volume, HPA scale-to-zero lên ổn định |

## Series này khác gì

Mỗi bài xoay quanh **đúng một chỗ "tưởng đúng mà sai"** — thứ mà đọc tài liệu chính thức thì
đúng, nhưng dùng thật thì vấp:

- `kubectl apply` không ra lệnh cho cụm, nó chỉ ghi vào sổ
- Service không phải load balancer — không có tiến trình nào tên là Service
- Secret không hề bí mật, và quyền tạo Pod gần bằng quyền đọc mọi Secret
- `ReadWriteOnce` là một **node**, không phải một pod
- PDB **không** chặn cập nhật cuốn chiếu
- HPA về 0 đã bật sẵn ở 1.36 — nhưng ở mức 0 thì nó **mù**

## Chỗ nào là mốc phiên bản thì có nguồn

Đây là series về một thứ đang đổi nhanh. Nên mọi khẳng định về phiên bản đều dẫn được tới nơi
công bố, và chỗ nào là **ước tính của người khác** thì ghi rõ là của ai — không trộn vào như thể
tôi đo được.

## Bạn sẽ học được gì

- Đọc mọi thứ trong Kubernetes qua một khuôn duy nhất: vòng lặp so mong muốn với hiện trạng
- Biết chỗ nào mất dữ liệu mà không ai báo lỗi
- Đặt probe, requests và limits mà không tự tạo ra sự cố cho chính mình
- Nhận ra mấy chỗ bảo mật chỉ *trông như* đã siết
- Biết cái gì ở 2026 đã đổi, và việc phải làm trước khi nâng cụm lên 1.36
"""
    base.mkdir(parents=True, exist_ok=True)
    (base / "index.md").write_text(index_md, encoding="utf8")

    print(f"{len(LESSONS)} bài + index.md → content/series/{CATEGORY_DIR}/{SERIES_SLUG}/")
    missing = [x["n"] for x in LESSONS if not ids.get(str(x["n"]))]
    if missing:
        print(f"  chưa có video id: {missing}")


if __name__ == "__main__":
    main()
