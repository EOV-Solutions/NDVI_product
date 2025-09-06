# 🌱 Triển khai Dự án tái tạo NDVI tại những vị trí bị mây che phủ

## 📌 Giới thiệu
Dự án này nhằm tái tạo chỉ số **NDVI (Normalized Difference Vegetation Index)** tại những khu vực ảnh viễn thám bị che phủ bởi mây.  
Mục tiêu chính:
- Bổ sung dữ liệu NDVI bị mất do mây.
- Cải thiện chất lượng chuỗi thời gian NDVI cho các nghiên cứu **nông nghiệp, lâm nghiệp và môi trường**.
- Ứng dụng ảnh **Sentinel-1 (SAR)** và **Sentinel-2 (quang học)** kết hợp với **Deep Learning**.

---

## ⚙️ Cách cài đặt

> ⚠️ Phần này sẽ cập nhật chi tiết sau.

```bash
# Clone repository
git clone https://github.com/EOV-Solutions/NDVI_product.git
cd NDVI_product

# Tạo môi trường (ví dụ với conda)
conda create -n ndvi_env python=3.10 -y
conda activate ndvi_env

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy thử pipeline
python main.py --config config.yaml
```

---

## 🗂️ Cấu trúc thư mục (dự kiến)

```plaintext
NDVI_product/
│── data/               # Dữ liệu đầu vào/đầu ra
│── notebooks/          # Notebook minh họa
│── src/                # Mã nguồn chính
│   ├── models/         # Mô hình ML/DL
│   ├── pipelines/      # Pipeline xử lý
│   └── utils/          # Hàm tiện ích
│── config.yaml         # File cấu hình
│── requirements.txt    # Danh sách dependencies
│── README.md           # Tài liệu dự án
```

---

## 🚀 Sử dụng

Ví dụ chạy train và infer:

```bash
# Train mô hình
python src/pipelines/train.py   

# Chạy dự đoán NDVI
python src/pipelines/infer.py   
```

---

## 🏗️ Kiến trúc hệ thống (dự kiến)

```plaintext
Sentinel-1/2 Data 
        │
        ▼
    STAC API 
        │
        ▼
      MinIO (S3)
        │
        ▼
   Pipeline xử lý
        │
        ├── Tiền xử lý dữ liệu
        ├── Training mô hình
        └── Inference NDVI tái tạo
        │
        ▼
   NDVI Reconstructed Output
```

---

## 📄 License

Dự án được phát triển nội bộ. License sẽ được cập nhật sau.
