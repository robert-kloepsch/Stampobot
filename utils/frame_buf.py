import cv2

from kivy.graphics.texture import Texture


def frame_to_buf(frame):
    """
    Convert OpenCV image frame to the texture that can be used in Image widget.
    :param frame:
    :return:
    """
    if frame is None:
        return
    buf1 = cv2.flip(frame, 0)
    if buf1 is not None:
        buf = buf1.tostring()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture


if __name__ == '__main__':

    frame_to_buf(frame=cv2.imread(""))
