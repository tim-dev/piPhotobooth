import time
import Image
import ImageTk
from Tkinter import *
import gdata.docs.service
import ConfigParser
import os.path

client = gdata.docs.service.DocsService()
camera = picamera.PiCamera()

# Constants
WIDTH = 1366
HEIGHT = 788
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSCOLOUR = 'gray'
RAW_FILENAME = 'image.jpg'


class Config:
    def __init__(self):
        self.conf = ConfigParser.ConfigParser()
        conf_filename = os.path.join("./", 'photobooth.conf')
        self.conf.read(conf_filename)
        self.username = self.conf.get("main", "username")
        self.password = self.conf.get("main", "password") # App-specific password so we don't need two step
        self.albumID = self.conf.get("main", "albumID")

config = Config()


def googleUpload(filen):
    #upload to picasa album
    album_url ='/data/feed/api/user/%s/albumid/%s' % (config.username, config.albumID)
    photo = client.InsertPhotoSimple(album_url, 'NoVa Snap', "", filen, content_type='image/jpeg')


def takePicture():
    countdown(camera)
    camera.capture(RAW_FILENAME, resize=(WIDTH, HEIGHT))
    snapshot = Image.open(RAW_FILENAME)
    camera.close()
    snapshot.save(RAW_FILENAME)
    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o = camera.add_overlay(snapshot.tobytes())
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we move it above
    # the preview
    o.layer = 3

    # Show it for a few seconds, then delete it
    time.sleep(10)
    camera.remove_overlay(o)

    return snapshot


def countdown(camera, countdown1=5):
    for i in range(countdown1):
        camera.annotate_text = str(countdown1 - i)
        #can.delete("text")
        #can.update()
        #can.create_text(WIDTH/2 - 50, 300, text=str(countdown1 - i), font=font, tags="text")
        #can.update()
        time.sleep(1)
    #can.delete("text")
    #can.update()

def main():
    # Authenticate using your Google Docs email address and password.
    client.ClientLogin(config.username, config.password)

    # Query the server for an Atom feed containing a list of your documents.
    documents_feed = client.GetDocumentListFeed()
    # Loop through the feed and extract each document entry.
    for document_entry in documents_feed.entry:
      # Display the title of the document on the command line.
      print document_entry.title.text

    ## This is a simple GUI, so we allow the root singleton to do the legwork
    root = Tk()
    WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

    # root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (WIDTH, HEIGHT))
    root.focus_set() # <-- move focus to this widget
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-transparentcolor", TRANSCOLOUR)

    frame = Frame(root)
    frame.pack()

    ## add a software button in case hardware button is not available
    #interface_frame = Frame(root)

    #snap_button = Button(interface_frame, text="*snap*", command=takePicture)
    #snap_button.pack(side=RIGHT)
    #interface_frame.pack(side=RIGHT)

    ## the canvas will display the images
    can = Canvas(root, width=WIDTH, height=HEIGHT)
    can.create_rectangle(0, 0, WIDTH, HEIGHT, fill=TRANSCOLOUR, outline=TRANSCOLOUR)
    can.bind("<Button-1>", takePicture)
    can.pack()

    ### check button after waiting for 200 ms
    #root.after(200, check_and_snap)
    root.wm_title("Wedding Photobooth")
    camera.start_preview()
    #camera.preview_alpha = 230
    camera.preview_window = (0, 0, WIDTH, HEIGHT)
    camera.preview_fullscreen = False

    root.mainloop()


if __name__ == "__main__":
    main()
