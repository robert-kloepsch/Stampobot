import cv2

from settings import STAMP_AREA_THRESH

def estimate_multi_single_stamp(frame):
    ret_val = "Multi"
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, thresh_frame = cv2.threshold(gray_frame, 200, 255, cv2.THRESH_BINARY)
    gs_contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    glass_contour = sorted(gs_contours, key=cv2.contourArea, reverse=True)[0]
    gs_left, gs_top, gs_right, gs_bottom = cv2.boundingRect(glass_contour)
    # cv2.rectangle(frame, (glass_rect[0], glass_rect[1]), (glass_rect[2], glass_rect[3]), (0, 0, 255), 5)
    # cv2.imshow("Gray frame", gray_frame)
    # cv2.imshow("Thresh Frame", thresh_frame)
    # cv2.imshow("Glass Region", frame)
    # cv2.waitKey()
    glass_frame = thresh_frame[gs_top:gs_bottom, gs_left:gs_right]
    glass_frame_inv = cv2.bitwise_not(glass_frame)
    # cv2.imshow("Glass Inv Frame", glass_frame_inv)
    # cv2.waitKey()
    st_contours, _ = cv2.findContours(glass_frame_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    stamp_contours = []
    for s_cnt in st_contours:
        if cv2.contourArea(s_cnt) < (gs_bottom - gs_top) * (gs_right - gs_left) * STAMP_AREA_THRESH:
            continue
        # print(cv2.contourArea(s_cnt), (gs_bottom - gs_top) * (gs_right - gs_left))
        stamp_contours.append(s_cnt)
    if len(stamp_contours) == 1:
        cv2.drawContours(frame, [stamp_contours[0]], 0, (0, 0, 255), 3)
        peri = cv2.arcLength(stamp_contours[0], True)
        approx = cv2.approxPolyDP(stamp_contours[0], 0.01 * peri, True)
        cv2.drawContours(frame, [approx], 0, (0, 255, 0), 2)
        cv2.imshow("Approx Contour", cv2.resize(frame, None, fx=0.5, fy=0.5))
        cv2.waitKey()
        if len(approx) == 4:
            ret_val = "Single"
    elif len(stamp_contours) == 0:
        ret_val = "None"

    # print(f"[INFO] {ret_val} Stamp(s)")

    return ret_val

if __name__ == '__main__':
    import glob
    import os

    multi = estimate_multi_single_stamp(frame=cv2.imread(""))
    img_files = glob.glob(os.path.join("", "*.jpg"))
    for i_file in img_files:
        multi = estimate_multi_single_stamp(frame=cv2.imread(i_file))
        if multi != "Single":
            print(f"[WANR] {i_file}: {multi}")
