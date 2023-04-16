import cv2
import os
import json
import sys


xi = yi =0
# function to display the coordinates of
# of the points clicked on the image 
def click_event(event, x, y, flags, params):
  
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
  
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
        global xi
        global yi
        xi=x
        yi=y
  
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(x) + ',' +
                    str(y), (x,y), font,
                    1, (255, 0, 0), 2)

        
        cv2.imshow('image', img)
  
    # checking for right mouse clicks     
    if event==cv2.EVENT_RBUTTONDOWN:
  
        # displaying the coordinates
        # on the Shell
        print(xi, ' ', yi)
  
        # displaying the coordinates
        # on the image window
        #font = cv2.FONT_HERSHEY_SIMPLEX
        #b = img[y, x, 0]
        #g = img[y, x, 1]
        #r = img[y, x, 2]
        #cv2.putText(img, str(b) + ',' +
        #            str(g) + ',' + str(r),
        #            (x,y), font, 1,
        #            (255, 255, 0), 2)
        #cv2.imshow('image', img)
        cv2.destroyAllWindows()
  
# driver function
if __name__=="__main__":
    print("Labeling Image Centers")
    input_file = sys.argv[1]
    directory = os.path.dirname(input_file)

    input_str = open(input_file)
    input = json.loads(input_str.read())
    
    samples = 20
    n = len(input["frames"])
    print(n//samples)
    for i in range(len(input["frames"])):
        if i%(n//samples) !=0:
            continue
        print("On",i)
        img_name = input["frames"][i]["file_path"]
        img_filepath = os.path.join(directory,os.path.join("imgs",img_name)).replace("\\","/")

        # reading the image
        img = cv2.imread(img_filepath, 1)
    
        # displaying the image
        cv2.imshow("image", img)
    
        # setting mouse handler for the image
        # and calling the click_event() function
        cv2.setMouseCallback("image", click_event)
    
        # wait for a key to be pressed to exit
        cv2.waitKey(0)
        print(f"Coordinates selected:\n x:{xi} \t y:{yi}")
        input["frames"][i]["object_center"] = [xi,yi]
    
        # close the window
        cv2.destroyAllWindows()
    with open("centered_transforms.json", "w") as outfile:
        json.dump(input, outfile, indent=4)