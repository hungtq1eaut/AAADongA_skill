"""
Perceptron from Scratch
Bài toán: dự đoán khách hàng có mua xe hay không.
Đặc trưng: x1 = Tuổi, x2 = Thu nhập, x3 = Đã kết hôn (0/1), x4 = Có ô tô cũ (0/1)
"""
import numpy as np


# ============ 1. Bộ dữ liệu (Bảng 1.2) ============
customers = ["A", "B", "C", "D", "E", "F"]
X = np.array([
    [24,  8, 0, 0],   # A
    [29, 15, 1, 0],   # B
    [35, 22, 1, 1],   # C
    [27, 10, 0, 0],   # D
    [41, 30, 1, 1],   # E
    [33, 18, 1, 0],   # F
], dtype=float)
y = np.array([0, 1, 1, 0, 1, 1])


# ============ 2. Cài đặt Perceptron ============
class Perceptron:
    def __init__(self, learning_rate=0.1, epochs=20):
        self.lr = learning_rate
        self.epochs = epochs
        self.w = None
        self.b = 0.0

    @staticmethod
    def step(z):
        """Hàm bước: 1 nếu z >= 0, ngược lại 0."""
        return np.where(z >= 0, 1, 0)

    def forward(self, x):
        """Lan truyền xuôi: z = w·x + b, rồi ŷ = step(z)."""
        z = np.dot(x, self.w) + self.b
        return z, self.step(z)

    def fit(self, X, y, verbose=True):
        n_samples, n_features = X.shape
        self.w = np.zeros(n_features)          # Bước 1: khởi tạo
        self.b = 0.0

        for epoch in range(1, self.epochs + 1):
            errors = 0
            for xi, yi in zip(X, y):
                _, y_hat = self.forward(xi)    # Bước 2: dự đoán
                error = yi - y_hat             # Bước 3: sai số
                if error != 0:                 # Bước 4: cập nhật khi sai
                    self.w += self.lr * error * xi
                    self.b += self.lr * error
                    errors += 1
            if verbose:
                print(f"Epoch {epoch:2d} | số lần sai: {errors} | "
                      f"w = {np.round(self.w, 3)} | b = {self.b:.3f}")
            if errors == 0:                    # Bước 5: dừng khi không còn sai
                print(f"\n→ Hội tụ sau {epoch} epoch.")
                break
        return self

    def predict(self, X):
        return self.forward(X)[1]


# ============ 3. Huấn luyện ============
print("=" * 70)
print("HUẤN LUYỆN PERCEPTRON")
print("=" * 70)
model = Perceptron(learning_rate=0.1, epochs=20)
model.fit(X, y)


# ============ 4. Kiểm tra trên tập huấn luyện ============
print("\n" + "=" * 70)
print("KẾT QUẢ DỰ ĐOÁN")
print("=" * 70)
print(f"{'Khách hàng':<11}{'z':>9}{'ŷ (dự đoán)':>14}{'y (thực tế)':>14}   Kết quả")
for name, xi, yi in zip(customers, X, y):
    z, y_hat = model.forward(xi)
    print(f"{name:<11}{z:>9.2f}{y_hat:>14}{yi:>14}   {'Đúng' if y_hat == yi else 'Sai'}")

acc = np.mean(model.predict(X) == y) * 100
print(f"\nĐộ chính xác: {acc:.0f}%")
print(f"Trọng số cuối: w = {np.round(model.w, 3)}, b = {model.b:.3f}")


# ============ 5. Dự đoán khách hàng mới ============
print("\n" + "=" * 70)
print("DỰ ĐOÁN KHÁCH HÀNG MỚI")
print("=" * 70)
new_customers = {
    "G (30 tuổi, 20tr, đã kết hôn, chưa có xe)": [30, 20, 1, 0],
    "H (23 tuổi, 7tr, độc thân, chưa có xe)":    [23,  7, 0, 0],
}
for desc, x_new in new_customers.items():
    z, y_hat = model.forward(np.array(x_new, dtype=float))
    print(f"{desc}: z = {z:.2f} → {'MUA XE' if y_hat == 1 else 'KHÔNG MUA'}")