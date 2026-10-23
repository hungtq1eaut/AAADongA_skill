"""
Cài đặt thuật toán Gale–Shapley theo Mục 2.3, sách Algorithm Design
(Kleinberg & Tardos). Thời gian chạy O(n^2), mỗi vòng lặp O(1).

Quy ước: nam và nữ được đánh số 0..n-1 (sách dùng 1..n).
"""
from collections import deque


def gale_shapley(man_pref, woman_pref):
    n = len(man_pref)

    # ----- Tiền xử lý: dựng mảng Ranking trong O(n^2) -----
    # ranking[w][m] = thứ hạng của m trong danh sách của w (số nhỏ = ưa thích hơn)
    ranking = [[0] * n for _ in range(n)]
    for w in range(n):
        for rank, m in enumerate(woman_pref[w]):
            ranking[w][m] = rank

    # ----- Các cấu trúc dữ liệu của Mục 2.3 -----
    free_men = deque(range(n))   # (1) danh sách các nam tự do: lấy/thêm ở đầu O(1)
    next_idx = [0] * n           # (2) Next[m]: vị trí người nữ kế tiếp m sẽ cầu hôn
    current = [None] * n         # (3) Current[w]: hôn phu hiện tại của w (None = tự do)

    while free_men:
        m = free_men[0]                      # (1) lấy một nam tự do: O(1)
        w = man_pref[m][next_idx[m]]         # (2) nữ cao nhất chưa cầu hôn: O(1)
        next_idx[m] += 1                     #     tăng Next[m] dù được nhận hay không

        if current[w] is None:               # (3) w đang tự do
            current[w] = m
            free_men.popleft()
        else:
            m2 = current[w]
            if ranking[w][m] < ranking[w][m2]:   # (4) so sánh bằng Ranking: O(1)
                current[w] = m
                free_men.popleft()
                free_men.appendleft(m2)          # m2 trở lại tự do, chèn vào đầu: O(1)
            # ngược lại: m vẫn tự do, ở nguyên đầu danh sách

    return [(current[w], w) for w in range(n)]


def is_stable(matching, man_pref, woman_pref):
    """Kiểm tra không có cặp bất ổn (dùng để thử nghiệm, O(n^2))."""
    n = len(man_pref)
    wife = {m: w for m, w in matching}
    husband = {w: m for m, w in matching}
    for m in range(n):
        for w in man_pref[m]:
            if w == wife[m]:
                break  # các nữ sau đó m thích kém hơn vợ hiện tại
            if woman_pref[w].index(m) < woman_pref[w].index(husband[w]):
                return False  # (m, w) là cặp bất ổn
    return True


if __name__ == "__main__":
    # Ví dụ thứ hai trong Chương 1: m=0, m'=1, w=0, w'=1
    # m thích w hơn w'; m' thích w' hơn w; w thích m' hơn m; w' thích m hơn m'
    man_pref = [[0, 1], [1, 0]]
    woman_pref = [[1, 0], [0, 1]]
    S = gale_shapley(man_pref, woman_pref)
    print("Ví dụ Chương 1:", S, "| ổn định:", is_stable(S, man_pref, woman_pref))

    # Thử ngẫu nhiên
    import random
    n = 200
    mp = [random.sample(range(n), n) for _ in range(n)]
    wp = [random.sample(range(n), n) for _ in range(n)]
    S = gale_shapley(mp, wp)
    print(f"Ngẫu nhiên n={n}: ổn định =", is_stable(S, mp, wp))