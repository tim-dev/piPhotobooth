import time
from PIL import Image
import ImageTk
from Tkinter import *
import picamera
import gdata.docs.service
import ConfigParser
import os.path
from io import BytesIO

client = gdata.docs.service.DocsService()

# Constants
WIDTH = 1366
HEIGHT = 788
SCALE = 1.25 ### was 2
TRANSCOLOUR = ''
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

class Photobooth:
    def __init__(self, root):
        self.camera = picamera.PiCamera()

        ## the canvas will display the images
        self.canv = Canvas(root, width=WIDTH, height=HEIGHT)
        self.canv.create_rectangle(0, 0, WIDTH, HEIGHT) #fill=TRANSCOLOUR, outline=TRANSCOLOUR
        self.canv.bind("<Button-1>", self.takePicture)
        self.canv.pack()
        self.previewImage()


    def loop(self):
        # Show a psuedo preview while the preview isn't going
        while True:
            if not self.previewing:
                self.previewImage()
                time.sleep(0.1)

    def previewImage(self):
        stream = BytesIO()
        self.camera.capture(stream, format='jpeg')
        # "Rewind" the stream to the beginning so we can read its content
        stream.seek(0)
        image = Image.open(stream)
        self.displayImage(image)


    def displayImage(self, im=None):
        '''
        display image im in GUI window
        '''
        x,y = im.size
        x = int(x / SCALE)
        y = int(y / SCALE)

        im = im.resize((x,y));
        image_tk = ImageTk.PhotoImage(im)

        ## delete all canvas elements with "image" in the tag
        self.canv.delete("image")
        self.canv.create_image([(WIDTH + x) / 2 - x/2,
                          0 + y / 2],
                         image=image_tk,
                         tags="image")


    def takePicture(self):
        self.camera.start_preview()
        #camera.preview_alpha = 230
        self.camera.preview_window = (0, 0, WIDTH, HEIGHT)
        self.camera.preview_fullscreen = False

        self.countdown()
        self.camera.capture(RAW_FILENAME, resize=(WIDTH, HEIGHT))
        snapshot = Image.open(RAW_FILENAME)

        # Show it for a few seconds, then delete it
        self.camera.stop_preview()
        self.displayImage(snapshot)
        time.sleep(10)
        self.camera.remove_overlay(o)

        return snapshot


    def countdown(self, countdown1=5):
        for i in range(countdown1):
            self.camera.annotate_text = str(countdown1 - i)
            #self.canv.delete("text")
            #self.canv.update()
            #self.canv.create_text(WIDTH/2 - 50, 300, text=str(countdown1 - i), font=font, tags="text")
            #self.canv.update()
            time.sleep(1)
        #self.canv.delete("text")
        #self.canv.update()



def googleUpload(filen):
    #upload to picasa album
    album_url ='/data/feed/api/user/%s/albumid/%s' % (config.username, config.albumID)
    photo = client.InsertPhotoSimple(album_url, 'NoVa Snap', "", filen, content_type='image/jpeg')



def main():
    # Authenticate using your Google Docs email address and password.
    client.ClientLogin(config.username, config.password)

    ## Query the server for an Atom feed containing a list of your documents.
    #documents_feed = client.GetDocumentListFeed()
    ## Loop through the feed and extract each document entry.
    #for document_entry in documents_feed.entry:
    #  # Display the title of the document on the command line.
    #  print document_entry.title.text

    ## This is a simple GUI, so we allow the root singleton to do the legwork
    root = Tk()
    WIDTH, HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()

    # root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (WIDTH, HEIGHT))
    root.focus_set() # <-- move focus to this widget
    root.wm_attributes("-topmost", True)
    root.wm_title("Wedding Photobooth")

    frame = Frame(root)
    frame.pack()

    photobooth = Photobooth(root)

    ## add a software button in case hardware button is not available
    #interface_frame = Frame(root)

    #snap_button = Button(interface_frame, text="*snap*", command=takePicture)
    #snap_button.pack(side=RIGHT)
    #interface_frame.pack(side=RIGHT)

    ### check button after waiting for 200 ms
    #root.after(200, check_and_snap)

    # Instead of the preview, we might write an image every half second or so
    photobooth.loop()
    root.mainloop()


if __name__ == "__main__":
    main()
