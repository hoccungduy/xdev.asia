---
id: f52942bd-d92b-5147-b442-7f17c4430b10
title: 'Bài 1: Bản đồ thuật toán Machine Learning'
slug: bai-1-ban-do-thuat-toan-machine-learning
description: >-
  Chọn thuật toán từ loại câu hỏi dữ liệu cần trả lời, không từ danh sách tên.
duration_minutes: 12
is_free: true
video_url: https://youtu.be/8KmpWQjVqw0
sort_order: 0
section_title: 'Phần 1: Bản đồ và hai mô hình nền'
course:
  id: a4a5696c-4ff1-522b-9564-dd4ea1c0da57
  title: ML nhìn là hiểu
  slug: ml-nhin-la-hieu
---

## Xem bản video

<div style="position:relative;padding-top:56.25%;margin:1.25rem 0;border-radius:12px;overflow:hidden;background:#0B1020;">
  <iframe
    src="https://www.youtube-nocookie.com/embed/8KmpWQjVqw0"
    title="Bài 1: Bản đồ thuật toán Machine Learning"
    loading="lazy"
    style="position:absolute;inset:0;width:100%;height:100%;border:0;"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    allowfullscreen></iframe>
</div>

Bản video 3:21. Bài viết dưới đây đi sâu hơn và có code chạy được.
Cả 13 tập ở [playlist](https://www.youtube.com/playlist?list=PLe9eqdcVq_qU), xếp sẵn theo thứ tự 1 → 13.

## Vấn đề không phải trí nhớ

Danh sách thuật toán Machine Learning dài và nhìn thì rời rạc: Linear Regression,
Logistic Regression, KNN, Decision Tree, Random Forest, Naive Bayes, SVM, K-means,
PCA, Gradient Boosting, mạng nơ-ron. Học thuộc hai mươi cái tên không giúp bạn chọn
được cái nào cho bài toán trước mắt.

Chúng rời rạc vì bị xếp theo **tên**. Xếp theo **câu hỏi mà dữ liệu cần trả lời** thì
chúng gom lại thành bốn nhóm, và mỗi nhóm chỉ có một câu hỏi.

## Bốn câu hỏi

**Câu 1 — đầu ra là một con số?** Giá căn hộ này khoảng bao nhiêu. Đây là hồi quy:
Linear Regression, Ridge/Lasso, cây hồi quy, Gradient Boosting.

**Câu 2 — đầu ra là một nhãn?** Căn này bán nhanh hay bán chậm. Đây là phân loại:
Logistic Regression, KNN, Decision Tree, Random Forest, Naive Bayes, SVM, mạng nơ-ron.

**Câu 3 — không có cột nhãn?** Dữ liệu có tự chia thành nhóm không, và nhóm nào ra
nhóm nào. Đây là phân cụm: K-means, DBSCAN, hierarchical.

**Câu 4 — quá nhiều chiều để nhìn?** Năm cột thì không vẽ lên giấy được. Đây là giảm
chiều: PCA, t-SNE, UMAP.

Bốn câu hỏi này khác nhau ở **dữ liệu bạn có**, không ở thuật toán bạn thích. Có cột
nhãn hay không là chuyện của dữ liệu. Nhãn là số hay là hạng mục cũng là chuyện của
dữ liệu. Nên thứ tự đúng là: đọc dữ liệu, tìm ra câu hỏi, rồi mới mở danh sách.

## Vì sao "thuật toán mạnh nhất" là câu hỏi sai

Không có thuật toán mạnh nhất, vì bốn câu hỏi trên không so được với nhau. K-means
không "yếu hơn" Random Forest — nó trả lời một câu hỏi khác hẳn.

Kể cả trong cùng một câu hỏi thì vẫn không có cái mạnh nhất. Bài 5 của series này có
một kết quả đo được: trên bộ dữ liệu 200 căn hộ, một cây quyết định **tỉa gọn** đạt
85% trên tập kiểm tra, còn rừng 200 cây chỉ đạt 82%. Rừng phức tạp hơn nhiều và thắng
trong phần lớn trường hợp thực tế — nhưng không phải trường hợp này.

## Ví dụ xuyên suốt cả series

Mọi bài dùng chung một bộ dữ liệu căn hộ: diện tích, số phòng, khoảng cách tới trung
tâm, tầng, giá bán, và nhãn bán nhanh hay bán chậm. Nhờ vậy khi bài 4 nói KNN trả lời
"nhanh" và bài 6 nói Naive Bayes cũng trả lời "nhanh", bạn biết chúng đang nói về đúng
cùng một căn hộ.

## Đọc tiếp theo thứ tự nào

Bài 2 và 3 mở hộp hai mô hình tuyến tính — nền của gần như mọi thứ sau đó. Bài 4 tới 7
là bốn cách nghĩ khác nhau về phân loại. Bài 8 và 9 là hai việc làm được khi không có
nhãn. Bài 10 và 11 là hai mô hình mạnh nhất trong thực tế.

Bài 12 và 13 là hai bài quan trọng nhất, và cũng là hai bài dễ bị bỏ qua nhất: **đo
cho đúng**. Một mô hình đúng 99% có thể vô dụng hoàn toàn, và bài 13 chỉ ra bằng số.

## Code

Bài này là bản đồ tổng quan nên không có thuật toán riêng để chạy. Mười hai bài sau, mỗi bài một thư mục trong repo:

```bash
git clone https://github.com/tdduydev/ml-nhin-la-hieu
cd ml-nhin-la-hieu
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```
