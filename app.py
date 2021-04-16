import tkinter
import cv2
import PIL
from PIL import Image, ImageEnhance
import time
import keyboard
from tkinter import *
from PIL import Image, ImageTk
import os
import shutil


# this function (delete old images) will be called when the application is started
def delete_prev_images():
    # delete old directory
    shutil.rmtree("img")
    # create a new one
    os.mkdir("img")


# this function (take a picture and automatically save it) will be called after delete_prev_images() function
def take_picture_and_save():
    # define variables
    global frame
    has_taken_picture = False
    # open camera
    cv2.namedWindow("Camera", cv2.WINDOW_AUTOSIZE)
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # try to get the first frame
    if camera.isOpened():
        return_value, frame = camera.read()

    # show image as long as window is open
    while cv2.getWindowProperty('Camera', 0) >= 0:
        cv2.imshow("Camera", frame)
        return_value, frame = camera.read()
        key_code = cv2.waitKey(1)

        # close camera if user uses the 'esc'-key
        if key_code == 27:
            break

        # take picture and save it if space is pressed
        if keyboard.is_pressed(' '):
            # set boolean to True to distinguish between two cases: taken an image or closed the camera
            has_taken_picture = True
            # try to save the image
            img_name = 'img/takenPicture.jpg'
            print(img_name + " written to img/")
            if not cv2.imwrite(img_name, frame):
                raise Exception("Could not write image")
            time.sleep(.2)
            break
    # if users closes the camera, the program is closed
    if not has_taken_picture:
        quit()
    # release the camera and close the window
    camera.release()
    cv2.destroyWindow("Camera")


# this function (open image and add a onClick()-listener) will be called after having taken and saved the picture
def open_image(path, name):
    # read wanted image
    img = cv2.imread(path, None)
    # scale the image and place it in a window that will be displayed
    scale_width = 640 / img.shape[1]
    scale_height = 480 / img.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(img.shape[1] * scale)
    window_height = int(img.shape[0] * scale)
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(name, window_width, window_height)

    # add an onclick-listener to the taken image (for the user, so that he can choose the pixel for the white-balance)
    if name == "Taken Image":
        # set mouse callback function for window
        cv2.setMouseCallback(name, mouse_callback)

    # display the window
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# this function will be called whenever the mouse is left-clicked
def mouse_callback(event, x, y, flags, params):
    # left-click event value is 1
    if event == 1:
        # save coordinates of the clicked pixel
        left_clicks = list()
        left_clicks.append((x, y))

        # get the RGB-Value of the clicked pixel
        get_rgb_value(left_clicks)
        # develop Y(UV)-Image
        rgb_to_y()
        rgb_to_u()
        rgb_to_v()

        # clear coordinates
        left_clicks.clear()
        cv2.destroyWindow("Taken Image")


# this function (get RGB-Value from pixel) will be called after having clicked a pixel
def get_rgb_value(clicks):
    # print("Coordinates:" + str(left_clicks))
    # open taken image
    image = PIL.Image.open("img/takenPicture.jpg")
    # convert it to a RGB-image
    image_rgb = image.convert("RGB")
    # get RGB-value from clicked pixel
    white_rgb = image_rgb.getpixel(clicks[0])
    # print("Pixel 1 RGB:" + str(white_rgb))
    # white-balance the picture
    white_balance(white_rgb)


# this function (do a white balance correction) will be called after having gotten the RGB-Value of the clicked pixel
def white_balance(white_rgb):
    # open image and save a copy for the RGB to YUV conversion
    img_to_change = Image.open("img/takenPicture.jpg")
    img_to_change.save("img/takenPictureY.jpg")
    # create the pixel map
    pixels = img_to_change.load()
    # white-balance all the RGB-Pixels
    for i in range(img_to_change.size[0]):
        for j in range(img_to_change.size[1]):
            # split the pixel up to R G B
            img_red = pixels[i, j][0]
            img_green = pixels[i, j][1]
            img_blue = pixels[i, j][2]
            # add the RGB-value of the clicked pixel and then divide it by 3
            lum = (white_rgb[0] + white_rgb[1] + white_rgb[2]) / 3
            # set 1 for the case that one (or more) values of the RGB-pixel are zero
            if white_rgb[0] == 0:
                white_rgb = (1, white_rgb[1], white_rgb[2])
            if white_rgb[1] == 0:
                white_rgb = (white_rgb[0], 1, white_rgb[2])
            if white_rgb[2] == 0:
                white_rgb = (white_rgb[0], white_rgb[1], 1)
            # calculate new (white-balanced) RGB-value
            img_red = img_red * lum / white_rgb[0]
            img_green = img_green * lum / white_rgb[1]
            img_blue = img_blue * lum / white_rgb[2]
            # overwrite the old RGB-value with the new (white-balanced) one
            pixels[i, j] = (int(img_red), int(img_green), int(img_blue))
    # save the modified image
    img_to_change.save("img/modifiedPicture.jpg")
    # open_image("img/modifiedPicture.jpg", "Modified Image")


# this function (get the Y(UV) value and so display the pictures luminance, which basically is the picture's brightness)
# will be called after the white balance has been done
def rgb_to_y():
    # load Image
    y_img = Image.open("img/takenPictureY.jpg")
    # create the pixel map
    y_pixels = y_img.load()
    # convert all the RGB-Pixels to Y(UV)-Values
    for i in range(y_img.size[0]):  # for every pixel:
        for j in range(y_img.size[1]):
            # split the pixel up to R G B
            y_red = y_pixels[i, j][0]
            y_green = y_pixels[i, j][1]
            y_blue = y_pixels[i, j][2]
            # conversion to y
            y = y_red * .299000 + y_green * .587000 + y_blue * .114000
            y = int(round(y))
            # place for all R, G and B the y-value to get a black-white image
            y_pixels[i, j] = (y, y, y)
    # save the modified image
    y_img.save("img/yPicture.jpg")
    # open_image("img/yPicture.jpg", "Y Image")


def rgb_to_u():
    u_img = Image.open("img/takenPictureY.jpg")
    u_pixels = u_img.load()
    for i in range(u_img.size[0]):  # for every pixel:
        for j in range(u_img.size[1]):
            y_red = u_pixels[i, j][0]
            y_green = u_pixels[i, j][1]
            y_blue = u_pixels[i, j][2]
            # U
            r = y_red*-.168736
            g = y_green*-.331264 + 128
            b = y_blue*.500000
            r = int(round(r))
            g = int(round(g))
            b = int(round(b))
            u_pixels[i, j] = (r, g, b)
    u_img.save("img/uPicture.jpg")
    # open_image("img/uPicture.jpg", "U Image")


def rgb_to_v():
    v_img = Image.open("img/takenPictureY.jpg")
    v_pixels = v_img.load()
    for i in range(v_img.size[0]):  # for every pixel:
        for j in range(v_img.size[1]):
            y_red = v_pixels[i, j][0]
            y_green = v_pixels[i, j][1]
            y_blue = v_pixels[i, j][2]
            # V
            r = y_red * .500000
            g = y_green * -.418688 + 128
            b = y_blue * -.081312
            r = int(round(r))
            g = int(round(g))
            b = int(round(b))
            v_pixels[i, j] = (r, g, b)
    v_img.save("img/vPicture.jpg")
    # open_image("img/vPicture.jpg", "V Image")


def set_brightness(args):
    manually_modify_image(args, "brightness")


def set_saturation(args):
    manually_modify_image(args, "saturation")


def set_contrast(args):
    manually_modify_image(args, "contrast")


def set_sharpness(args):
    manually_modify_image(args, "sharpness")


def manually_modify_image(args, call_from):
    value = int(args)
    value /= 100.00

    im = Image.open("img/takenPicture.jpg")
    if call_from == "brightness":
        enhancer = ImageEnhance.Brightness(im)
    elif call_from == "saturation":
        enhancer = ImageEnhance.Color(im)
    elif call_from == "sharpness":
        enhancer = ImageEnhance.Sharpness(im)
    elif call_from == "contrast":
        enhancer = ImageEnhance.Contrast(im)

    global enhanced_im
    enhanced_im = enhancer.enhance(value)

    modified_pic = ImageTk.PhotoImage(enhanced_im)
    modified_pic_label = tkinter.Label(image=modified_pic)
    modified_pic_label.image = modified_pic
    modified_pic_label.grid(column=1, row=0)


# this function (builds a GUI) will be called after the taken picture has been opened
def save_image():
    enhanced_im.save("img/takenPicture.jpg")


def gui():
    # root-field
    root = tkinter.Tk()
    root.title("Your Images")

    # canvas on the root-field
    canvas = tkinter.Canvas(root, width=600, height=300)
    canvas.grid(columnspan=3, rowspan=3)

    # taken Picture will be displayed
    pic = Image.open("img/takenPicture.jpg")
    pic = ImageTk.PhotoImage(pic)
    pic_label = tkinter.Label(image=pic)
    pic_label.image = pic
    pic_label.grid(column=1, row=0)

    # 'Modified Image' button
    modified_text = tkinter.StringVar()
    modified_btn = tkinter.Button(root, textvariable=modified_text, command=lambda: modified_image(), font="Raleway")
    modified_text.set("Modified Image")
    modified_btn.grid(column=1, row=3)

    # 'Y Image' button
    y_text = tkinter.StringVar()
    y_btn = tkinter.Button(root, textvariable=y_text, command=lambda: y_image(), font="Raleway")
    y_text.set("Y Image")
    y_btn.grid(column=1, row=4)

    slider_brightness = Scale(root, from_=0, to=200, orient=HORIZONTAL, command=set_brightness)
    slider_brightness.set(100)
    slider_brightness.grid(column=2, row=1)

    brightness_text = tkinter.StringVar()
    brightness_btn = tkinter.Button(root, textvariable=brightness_text, command=lambda: save_image(), font="Raleway")
    brightness_text.set("OK")
    brightness_btn.grid(column=3, row=1)

    slider_saturation = Scale(root, from_=0, to=200, orient=HORIZONTAL, command=set_saturation)
    slider_saturation.set(100)
    slider_saturation.grid(column=2, row=2)

    brightness_text = tkinter.StringVar()
    brightness_btn = tkinter.Button(root, textvariable=brightness_text, command=lambda: save_image(), font="Raleway")
    brightness_text.set("OK")
    brightness_btn.grid(column=3, row=2)

    slider_contrast = Scale(root, from_=0, to=200, orient=HORIZONTAL, command=set_contrast)
    slider_contrast.set(100)
    slider_contrast.grid(column=2, row=3)

    brightness_text = tkinter.StringVar()
    brightness_btn = tkinter.Button(root, textvariable=brightness_text, command=lambda: save_image(), font="Raleway")
    brightness_text.set("OK")
    brightness_btn.grid(column=3, row=3)

    slider_sharpness = Scale(root, from_=0, to=200, orient=HORIZONTAL, command=set_sharpness)
    slider_sharpness.set(100)
    slider_sharpness.grid(column=2, row=4)

    brightness_text = tkinter.StringVar()
    brightness_btn = tkinter.Button(root, textvariable=brightness_text, command=lambda: save_image(), font="Raleway")
    brightness_text.set("OK")
    brightness_btn.grid(column=3, row=4)

    # this is needed to display the GUI
    root.mainloop()


# this function (displays the white-balanced-image) will be called if the user clicks on the 'Modified Image' Button
def modified_image():
    # open image
    pic = Image.open("img/modifiedPicture.jpg")
    pic = ImageTk.PhotoImage(pic)
    # add image to the canvas
    pic_label = tkinter.Label(image=pic)
    pic_label.image = pic
    pic_label.grid(column=2, row=0)
    pic_label.size()


# this function (displays the Y(UV)-image) will be called if the user clicks on the 'Y Image' Button
def y_image():
    # open image
    pic = Image.open("img/yPicture.jpg")
    pic = pic.resize((round(128), round(96)))
    pic = ImageTk.PhotoImage(pic)
    # add image to the canvas
    pic_label = tkinter.Label(image=pic)
    pic_label.image = pic
    pic_label.grid(column=1, row=5)
    pic_label.size()

    pic = Image.open("img/uPicture.jpg")
    pic = pic.resize((round(128), round(96)))
    pic = ImageTk.PhotoImage(pic)
    # add image to the canvas
    pic_label = tkinter.Label(image=pic)
    pic_label.image = pic
    pic_label.grid(column=2, row=5)
    pic_label.size()

    pic = Image.open("img/vPicture.jpg")
    pic = pic.resize((round(128), round(96)))
    pic = ImageTk.PhotoImage(pic)
    # add image to the canvas
    pic_label = tkinter.Label(image=pic)
    pic_label.image = pic
    pic_label.grid(column=3, row=5)
    pic_label.size()


if __name__ == '__main__':
    # 1
    delete_prev_images()
    # 2
    take_picture_and_save()
    # 3
    open_image("img/takenPicture.jpg", 'Taken Image')
    gui()