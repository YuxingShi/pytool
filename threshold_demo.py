# coding:utf-8
import cv2


# thresh值变化
def thresh_modify(event):
    pass


cv2.namedWindow('Threshold', 0)
cv2.createTrackbar('ThreshValue', 'Threshold', 0, 255, thresh_modify)
file_name = "xwh.jpg"
image = cv2.imread(file_name, 0)


while True:
    thresh_value = cv2.getTrackbarPos('ThreshValue', 'Threshold')
    ret, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_BINARY)
    # ret, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_BINARY_INV)
    # ret, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_TRUNC)
    # ret, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_TOZERO)
    # ret, thresh = cv2.threshold(image, thresh_value, 255, cv2.THRESH_TOZERO_INV)
    cv2.imshow("Threshold", thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif cv2.waitKey(1) & 0xFF == ord('s'):
        save_name = 'threshold_{}'.format(file_name)
        cv2.imwrite(save_name, thresh)
cv2.destroyAllWindows()
