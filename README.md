# 🧬 AgriGene Explorer

**AgriGene Explorer** là ứng dụng web tương tác được xây dựng bằng [Streamlit](https://streamlit.io/) giúp các nhà nghiên cứu sinh học nông nghiệp dễ dàng tìm kiếm, tra cứu và phân tích các trình tự gen từ cơ sở dữ liệu quốc gia về thông tin công nghệ sinh học (NCBI).

---

## 🚀 Tính năng nổi bật

1. **🔍 Tìm kiếm Gen Nông Nghiệp**
   - Tìm kiếm trình tự gen theo từ khóa (VD: *rbcL*, *matK*) và tên loài (VD: *Oryza sativa*, *Zea mays*).
   - Truy vấn trực tiếp từ cơ sở dữ liệu NCBI Entrez.
   - Hỗ trợ tải xuống siêu dữ liệu (metadata) dưới dạng tệp `.csv`.

2. **🧬 Phân tích Trình tự**
   - Hỗ trợ nhập chuỗi định dạng FASTA thủ công hoặc tải trực tiếp bằng Accession ID (VD: `NM_001159351`).
   - Cung cấp thống kê cơ bản: Chiều dài (bp), hàm lượng GC (GC Content), tỉ lệ AT/GC.
   - Truy xuất khung đọc mở (ORF - Open Reading Frames).
   - Dễ dàng dịch mã DNA sang trình tự Axit Amin (Protein).

3. **📊 Thống kê & Trực quan hoá dữ liệu (Visualize)**
   - Phân tích trực quan thông qua các biểu đồ đa dạng (Plotly):
     - Biểu đồ phân bố độ dài trình tự gen.
     - Biểu đồ tròn hiển thị thành phần loài.
     - Dòng thời gian submission.
     - Heatmap biểu diễn hàm lượng GC.

4. **⚙️ Quản lý & Cấu hình**
   - Cấu hình Email để đáp ứng chính sách E-utilities của NCBI.
   - Thêm API Key NCBI (tùy chọn) để tăng giới hạn truy vấn (từ 3 requests/s lên 10 requests/s).

---

## 🛠️ Công nghệ sử dụng

- **Ngôn ngữ:** Python 3
- **Web Framework:** Streamlit
- **Tin sinh học:** Biopython
- **Xử lý Dữ liệu:** Pandas, NumPy
- **Trực quan hoá:** Plotly
- **API Call & Requests:** Requests

---

## 💻 Cài đặt & Chạy ứng dụng (Local)

### Yêu cầu hệ thống
- Đã cài đặt **Python 3.8+**

### Các bước cài đặt

**1. Clone dự án (hoặc tải trực tiếp mã nguồn)**
```bash
git clone https://github.com/your-username/AgriGene-Explorer.git
cd AgriGene-Explorer
```

**2. Tạo môi trường ảo (Khuyến nghị)**
```bash
python -m venv venv
# Active môi trường:
# - Window: venv\Scripts\activate
# - macOS/Linux: source venv/bin/activate
```

**3. Cài đặt các thư viện phụ thuộc**
```bash
pip install -r requirements.txt
```

**4. Khởi chạy ứng dụng**
```bash
streamlit run app.py
```

Ứng dụng sẽ tự động mở trên trình duyệt tại địa chỉ: `http://localhost:8501`

---

## 🚨 Các lưu ý khi sử dụng

- **Yêu cầu NCBI Email:** Khi khởi động ứng dụng lần đầu, bạn cần điền địa chỉ **Email** tại tab `⚙️ Cài đặt` để tránh việc IP bị block bởi server NCBI.
- Nếu bạn có sử dụng thường xuyên hoặc tra cứu số lượng lớn, bạn nên đăng ký [NCBI API Key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) để tăng giới hạn truy vấn.

---

## 🤝 Đóng góp (Contributing)

Mọi đóng góp nhằm hoàn thiện dự án đều được hoan nghênh báo cáo lỗi, mở issues hoặc gửi Pull Requests.

1. Fork dự án
2. Tạo nhánh tính năng (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Đẩy (Push) lên nhánh (`git push origin feature/AmazingFeature`)
5. Mở một **Pull Request**

---

## 📄 Giấy phép (License)

Dự án này được phân phối dưới giấy phép **MIT**. Xem tệp `LICENSE` để biết thêm chi tiết.
