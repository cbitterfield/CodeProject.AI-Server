
import base64
import io
import json
import base64
from io import BytesIO

from PIL import Image

# from common import JSON
# from logging import LogMethod

class AIRequestData:
    """
    Contains information on the request passed in by a client for an AI
    inference operation, and provides helper methods to access this information
    """

    # Constructor
    def __init__(self, json_request_data):

        self._verbose_exceptions = True

        self.request_data = json.JSONDecoder().decode(json_request_data)
        
        self.request_id   = self.request_data.get("reqid", "") # No longer needed, and same as command

        self.payload      = self.request_data["payload"]
        self.queue_name   = self.payload.get("queue","N/A")
        self.value_list   = self.payload.get("values", None)
        self.files        = self.payload.get("files", None)
        self.segments     = self.payload.get("urlSegments", None)
        self.command      = self.payload.get("command", None)
       
    def encode_image(self, image: Image, image_format: str = "PNG") -> str:
        """
        Encodes an Image as a base64 encoded string
        """

        buffered = BytesIO()
        try:
            image.save(buffered, format=image_format)
            img_dataB64_bytes : bytes = base64.b64encode(buffered.getvalue())
            img_dataB64 : str = img_dataB64_bytes.decode("ascii");

            # Alternative that had issues
            # img_dataB64 = base64.b64encode(processed_img)

            return img_dataB64

        finally:
            # Release the buffer dummy (me)
            buffered.close()

     
    def get_image(self, index : int) -> Image:
        """
        Gets an image from the requests 'files' array that was passed in as 
        part of a HTTP POST.
        Param: index - the index of the image to return
        Returns: An image if succesful; None otherwise.
        """

        try:
            if self.files is None or len(self.files) <= index:
                return None

            img_file    = self.files[index]
            img_dataB64 = img_file["data"]
            img_bytes   = base64.b64decode(img_dataB64)
            img_stream  = io.BytesIO(img_bytes)
            try:
                img         = Image.open(img_stream).convert("RGB")
                return img

            finally:
                # Release the buffer dummy (me)
                img_stream.close()


        except Exception as ex:

            if self._verbose_exceptions:
                print(f"Error getting image {index} from request")

            """
            err_msg = "Unable to get image from request"
            if self._verbose_exceptions:
                err_msg = str(ex)

            self.log(LogMethod.Error|LogMethod.Server|LogMethod.Cloud, {
                "message": err_msg,
                "method": "get_image",
                "process": self.queue_name,
                "filename": "requestdata.py",
                "exception_type": "Exception"
            })
            """
            return None


    def get_value(self, key : str, defaultValue : str = None) -> any:
        """
        Gets a value from the HTTP request Form send by the client
        Param: key - the name of the key holding the data in the form collection
        Returns: The data if successful; None otherwise.
        Remarks: Note that HTTP forms contain multiple values per key (a string
        array) to allow for situations like checkboxes, where a set of checkbox
        controls share a name but have unique IDs. The form will contain an
        array of values for the shared name. 
        ** WE ONLY RETURN THE FIRST VALUE HERE **
        """

        # self.log(LogMethod.Info, {"message": f"Getting request for module {self.module_id}"})

        try:
            # value_list is a list. Note that in a HTML form, each element may
            #  have multiple values 
            if self.value_list is None:
                return defaultValue

            for value in self.value_list:
                if value["key"] == key :
                    return value["value"][0]
        
            return defaultValue

        except Exception as ex:
            if self._verbose_exceptions:
                print(f"Error getting get_request_value: {str(ex)}")
            return defaultValue
