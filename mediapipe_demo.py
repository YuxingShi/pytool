# coding:utf-8
import time
import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
cv2.namedWindow("Camera", 0)  # 0可调整窗口大小，1，默认窗口
mp_draw = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)
draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1)
p_time = 0
while True:  # 主程序
    ret1, frame1 = cap.read()  # get a frame
    if not ret1:
        break
    img_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(img_rgb)
    if results.multi_face_landmarks:
        for face_lms in results.multi_face_landmarks:
            mp_draw.draw_landmarks(frame1, face_lms, mp_face_mesh.FACE_CONNECTIONS, draw_spec, draw_spec)
    c_time = time.time()
    fps = 1 / (c_time - p_time)
    p_time = c_time
    cv2.putText(frame1, 'fps:{}'.format(fps), (10, 25), cv2.FONT_ITALIC, 1.0, (0, 255, 0), thickness=2)
    cv2.imshow("Camera", frame1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
