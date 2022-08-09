import configparser
import numpy as np
import cv2

from settings import CONFIG_FILE_PATH


class ImageUtils:
    def __init__(self):
        params = configparser.ConfigParser()
        params.read(CONFIG_FILE_PATH)
        self.gamma_val = float(params.get('DEFAULT', 'gamma'))
        self.brightness = int(params.get('DEFAULT', 'brightness'))
        self.contrast = int(params.get('DEFAULT', 'contrast'))
        self.sharpness = params.get('DEFAULT', 'sharpness')
        self.white_balance = params.get('DEFAULT', 'white_balance')

    @staticmethod
    def sharp_image(image):
        img_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpen_img = cv2.filter2D(image, -1, img_filter)

        return sharpen_img

    @staticmethod
    def correct_white_balance(image):
        b, g, r = cv2.split(image)
        r_avg = cv2.mean(r)[0]
        g_avg = cv2.mean(g)[0]
        b_avg = cv2.mean(b)[0]

        k = (r_avg + g_avg + b_avg) / 3
        kr = k / r_avg
        kg = k / g_avg
        kb = k / b_avg

        r = cv2.addWeighted(src1=r, alpha=kr, src2=0, beta=0, gamma=0)
        g = cv2.addWeighted(src1=g, alpha=kg, src2=0, beta=0, gamma=0)
        b = cv2.addWeighted(src1=b, alpha=kb, src2=0, beta=0, gamma=0)
        balance_img = cv2.merge([b, g, r])

        return balance_img

    def adjust_gamma(self, image):
        inv_gamma = 1.0 / float(self.gamma_val)
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def correct_contrast_brightness(self, image):
        brightness = int((float(self.brightness) - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast = int((float(self.contrast) - 0) * (127 - (-127)) / (254 - 0) + (-127))

        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                max_val = 255
            else:
                shadow = 0
                max_val = 255 + brightness
            al_pha = (max_val - shadow) / 255
            ga_mma = shadow
            con_bri_image = cv2.addWeighted(image, al_pha, image, 0, ga_mma)
        else:
            con_bri_image = image

        if contrast != 0:
            alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            gamma = 127 * (1 - alpha)
            con_bri_image = cv2.addWeighted(con_bri_image, alpha, con_bri_image, 0, gamma)

        return con_bri_image

    def run(self, frame):
        cont_bri_image = self.correct_contrast_brightness(image=frame)
        if self.sharpness == "true":
            sharp_image = self.sharp_image(image=cont_bri_image)
        else:
            sharp_image = cont_bri_image
        gam_image = self.adjust_gamma(image=sharp_image)
        if self.white_balance == "true":
            final_image = self.correct_white_balance(image=gam_image)
        else:
            final_image = gam_image

        return final_image


if __name__ == '__main__':
    i_image = cv2.imread("")
    # adjusted_image = adjust_gamma(image=i_image, gamma_val=2.0)
    # cont_image = correct_contrast_brightness(image=i_image, brightness=200, contrast=170)
    # sha_image = sharp_image(image=i_image)
    # bal_image = correct_white_balance(image=i_image)
    # cv2.imshow("Original Image", i_image)
    # cv2.imshow("Gamma Image", adjusted_image)
    # cv2.imshow("Contrast Image", cont_image)
    # cv2.imshow("Sharpen Image", sha_image)
    # cv2.imshow("White Balance Image", bal_image)
    # cv2.waitKey()
