import cv2  # xu li anh , mo webcam , hien thi video
import mediapipe as mp # nhan dien ban tay va  cac diem landmark (21 diem tren bang tay)
import requests # gui yeu cau http den esp 32

# ==== Cấu hình IP ESP32-C3 ====
ESP_IP = "192.168.1.43"  # thay IP ESP32-C3 hiện lên LCD

# ==== Khởi tạo MediaPipe ====
mp_hands = mp.solutions.hands #modun nhan dien ban tay 
mp_draw = mp.solutions.drawing_utils#vẽ 21 dấu chấm và nối chúng lại , tùy chỉnh độ dày kích thước chấm
#max_mun_hand số bàn tay nhận dạng được , min_detection : là ngưỡng tin cậy tối thiểu cho lần phát hiện đầu
hands = mp_hands.Hands(max_num_hands=2 ,min_detection_confidence=0.9)
# mở camera mặc định là cam máy tính (0 là ID của camera)
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        continue
    """
    OpenCV (cv2) khi đọc ảnh từ webcam (cap.read()) → trả về ảnh ở định dạng BGR (Blue, Green, Red).
    Nhưng MediaPipe lại yêu cầu ảnh đầu vào phải là RGB (Red, Green, Blue).
    """

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    count = 0
    #multi_hand_landmarks chứa danh sách 21 điểm tọa độ 
    """
    👉 Nếu không có bàn tay nào thì multi_hand_landmarks = None.
    👉 Nếu có 1 bàn tay thì nó là 1 list chứa 21 điểm.
    👉 Nếu cho phép 2 bàn tay (max_num_hands=2) thì sẽ có 2 list, mỗi list 21 điểm.
    """
    if results.multi_hand_landmarks:
        #in zip là làm việc song song , tay trái sao thì tay phải y vậy
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            is_right = (handedness.classification[0].label == "Right")
            # tọa độ x,y,z gốc 0 là ở cổ tay
            """
            wrist (ID = 0): điểm ở cổ tay.
            thumb_tip (ID = 4): điểm ở đầu ngón cái.
            thumb_ip (ID = 3): điểm ở đốt gần đầu ngón cái (khớp IP – Interphalangeal joint).
            middle_mcp (ID = 9): khớp gốc ngón giữa, dùng để xác định hướng lòng bàn tay (úp/ngửa).
            wrist (cổ tay) dùng để xác định hướng bàn tay (lòng bàn tay úp hay ngửa).

            thumb_tip và thumb_ip dùng để kiểm tra xem ngón cái đang giơ lên hay gập lại
            """
            wrist = hand_landmarks.landmark[0]
            thumb_tip = hand_landmarks.landmark[4]
            thumb_ip = hand_landmarks.landmark[3]
            middle_mcp = hand_landmarks.landmark[9]  # thêm điểm chuẩn để xác định palm up/down

            # Nếu palm up (wrist.y > middle_mcp.y)
            if wrist.y > middle_mcp.y:
                if is_right:
                    if thumb_tip.x < thumb_ip.x:  # ngón cái bên phải, giơ ra ngoài
                        count += 1
                else:
                    if thumb_tip.x > thumb_ip.x:  # ngón cái bên trái, giơ ra ngoài
                        count += 1
            # Nếu palm down (wrist.y < middle_mcp.y)
            else:
                if is_right:
                    if thumb_tip.x > thumb_ip.x:
                        count += 1
                else:
                    if thumb_tip.x < thumb_ip.x:
                        count += 1

            # 4 ngón còn lại
            finger_tips = [8, 12, 16, 20]
            for tip_id in finger_tips:
                if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id-2].y:
                    count += 1

            # Vẽ bàn tay
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Hiển thị số ngón trên PC
    cv2.putText(img, f"Fingers: {count}", (50,100),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3)

    # Gửi dữ liệu qua HTTP GET
    try:
        url = f"http://{ESP_IP}/update?fingers={count}"
        requests.get(url, timeout=0.1)
    except:
        pass

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
