import cv2
import json

# 전역 변수 설정
drawing = False  # 드래그 상태 여부
ix, iy = -1, -1  # 시작 좌표
rect = (0, 0, 0, 0)  # 선택된 영역 좌표 (x1, y1, x2, y2)
cropped_regions = []  # 크롭된 영역 저장 리스트
frame_count = 0  # 현재 프레임 번호

# 마우스 이벤트 콜백 함수
def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, rect

    if event == cv2.EVENT_LBUTTONDOWN:  # 마우스 왼쪽 버튼 누름
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:  # 마우스 이동
        if drawing:
            rect = (ix, iy, x, y)

    elif event == cv2.EVENT_LBUTTONUP:  # 마우스 왼쪽 버튼 뗌
        drawing = False
        rect = (ix, iy, x, y)

# 동영상 파일 경로
video_path = '1.mp4'
output_json_path = 'cropped.json'

# 동영상 캡처 객체 생성
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Unable to open video file.")
    exit()

# FPS 값 가져오기
fps = int(cap.get(cv2.CAP_PROP_FPS))  # FPS 값 정의

# OpenCV 창 생성 및 마우스 콜백 함수 등록
cv2.namedWindow('Video')
cv2.setMouseCallback('Video', draw_rectangle)

# 비디오 루프
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    x1, y1, x2, y2 = rect
    if x1 != x2 and y1 != y2:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow('Video', frame)
    key = cv2.waitKey(100) & 0xFF

    if key == ord('c'):  # 'c' 키로 크롭 저장
        if x1 != x2 and y1 != y2:
            cropped = frame[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
            cropped_image_path = f'cropped_time_{frame_count // fps:02}_{frame_count % fps:02}.jpg'
            cv2.imwrite(cropped_image_path, cropped)
            print(f"Cropped image saved: {cropped_image_path}")

            cropped_regions.append({
                'frame': frame_count,
                'coordinates': {'x1': min(x1, x2), 'y1': min(y1, y2), 'x2': max(x1, x2), 'y2': max(y1, y2)},
                'image_path': cropped_image_path
            })
        else:
            print("No region selected for cropping.")

    elif key == ord('q'):  # 'q' 키로 종료
        print("Exiting...")
        break

    frame_count += 1

# JSON 파일로 저장
with open(output_json_path, 'w') as json_file:
    json.dump(cropped_regions, json_file, indent=4)
    print(f"Coordinates and cropped image data saved to {output_json_path}")

delay = int(1000 / fps)  # FPS에 따른 대기 시간(ms)
key = cv2.waitKey(delay) & 0xFF


# 리소스 해제
cap.release()
cv2.destroyAllWindows()
