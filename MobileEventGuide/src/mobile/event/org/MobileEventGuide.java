package mobile.event.org;


import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

import org.apache.http.HttpConnection;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.ImageView;

public class MobileEventGuide extends Activity implements OnClickListener{
    /** Called when the activity is first created. */
	
	private int CAMERA_PIC_REQUEST=3333;
	private Bitmap pic=null;

	
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.main);
        ImageView CameraButton= (ImageView) findViewById(R.id.camera3);
        CameraButton.setOnClickListener(this);
    }
    
    
    public void Camera(){
      	Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
      	startActivityForResult(cameraIntent, CAMERA_PIC_REQUEST);  
      }
      
      
      protected void onActivityResult(int requestCode, int resultCode, Intent data) {
      	if (requestCode == CAMERA_PIC_REQUEST) //
              if (resultCode == Activity.RESULT_OK) {
                 // Display image received on the view
                  Bundle b = data.getExtras(); // Kept as a Bundle to check for other things in my actual code
                  pic = (Bitmap) b.get("data");
                 // String Image=data.getData();

                  if (pic != null) { 
                   //Display your image in an ImageView in your layout (if you want to test it)
                      ImageView pictureHolder = (ImageView) this.findViewById(R.id.pictureholder);
                      pictureHolder.setImageBitmap(pic);
                      //handlePicture(pic, "jpg");
                      pictureHolder.invalidate();
                  }
              }
              else if (resultCode == Activity.RESULT_CANCELED) {}
      	} 	
      
      /*public void  post(){
    	  String url = "http://???.???.??/CommunicationOfficeService/TempExchangeRatesService.asmx";
          HttpURLConnection hc = (HttpURLConnection) Connector.open(url);
          //Some web servers requires these properties 
          hc.setRequestMethod(HttpConnection.POST);
          
          hc.setRequestProperty("SOAPAction", "http://www.???.??/TempExchangeRatesService/GetCurrentExchangeRatesXML");
          hc.setRequestProperty("User-Agent", "Profile/MIDP-1.0 Configuration/CLDC-1.0");
          hc.setRequestProperty("Content-Type", "text/xml;charset=utf-8");
          hc.setRequestProperty("Content-Length", Integer.toString(message.length()));
          hc.setRequestProperty("Connection", "close");
          OutputStream os = hc.openOutputStream();
          
          os.write(message.getBytes());
          os.close();
      }*/
      
      
      private boolean handlePicture(String mimeType) {       
    	    HttpURLConnection connection = null;
    	    DataOutputStream outStream = null;
    	    DataInputStream inStream = null;

    	    String lineEnd = "\r\n";
    	    String twoHyphens = "--";
    	    String boundary = "*****";

    	    int bytesRead, bytesAvailable, bufferSize;

    	    byte[] buffer;

    	    int maxBufferSize = 1*1024*1024;

    	    String urlString = "http://megimage.heroku.com/upload";

    	    try {
    	        /*FileInputStream fileInputStream = null;
    	        try {
    	            fileInputStream = new FileInputStream(new File(filePath));
    	        } catch(FileNotFoundException e) { }   	        
    	        */
    	    	
    	        URL url = new URL(urlString);
    	        connection = (HttpURLConnection) url.openConnection();
    	        connection.setDoInput(true);
    	        connection.setDoOutput(true);
    	        connection.setUseCaches(false);

    	        connection.setRequestMethod("POST");
    	        connection.setRequestProperty("Connection", "Keep-Alive");
    	        connection.setRequestProperty("Content-Type", "multipart/form-data;boundary="+boundary);            
				
    	        outStream = new DataOutputStream(connection.getOutputStream());
   
    	        ByteArrayOutputStream baos = new ByteArrayOutputStream();  
    	        pic.compress(Bitmap.CompressFormat.PNG, 100, baos);  
    	        byte[] byteArray  = baos.toByteArray(); 
    	        //byte[] byteArray  = {(byte) 1, (byte) 2}; 

    	        outStream.write(byteArray);
    	        outStream.flush();
    	        outStream.close();


    	        /*outStream.writeBytes(addParam("someparam", "content of some param", twoHyphens, boundary, lineEnd));                
    	        //outStream.writeBytes(twoHyphens + boundary + lineEnd);
    	        outStream.writeBytes("Content-Disposition: form-data; name=\"uploadedfile\";filename=\"" + filePath +"\"" + lineEnd + "Content-Type: " + mimeType + lineEnd + "Content-Transfer-Encoding: binary" + lineEnd);           
    	        outStream.writeBytes(lineEnd);

    	        bytesAvailable = fileInputStream.available();
    	        bufferSize = Math.min(bytesAvailable, maxBufferSize);
    	        buffer = new byte[bufferSize];

    	        bytesRead = fileInputStream.read(buffer, 0, bufferSize);

    	          while (bytesRead > 0) {
    	              outStream.write(buffer, 0, bufferSize);
    	            bytesAvailable = fileInputStream.available();
    	            bufferSize = Math.min(bytesAvailable, maxBufferSize);
    	            bytesRead = fileInputStream.read(buffer, 0, bufferSize);
    	        }

    	          outStream.writeBytes(lineEnd);
    	          outStream.writeBytes(twoHyphens + boundary + twoHyphens + lineEnd);

    	        fileInputStream.close();
    	        outStream.flush();
    	        outStream.close();  */
    	    } catch (MalformedURLException e) {
    	        Log.e("DEBUG", "[MalformedURLException while sending a picture]");
    	    } catch (IOException e) {
    	        Log.e("DEBUG", "[IOException while sending a picture]"); 
    	    }

    	    try {
    	           inStream = new DataInputStream( connection.getInputStream() );
    	           String str;

    	           while (( str = inStream.readLine()) != null) {
    	               if(str=="1") {
    	                   return true;
    	               } else {
    	                   return false;
    	               }
    	           }
    	           inStream.close();
    	      } catch (IOException e){
    	          Log.e("DEBUG", "[IOException while sending a picture and receiving the response]");
    	      }
    	    return false;
    	}

    	private String addParam(String key, String value, String twoHyphens, String boundary, String lineEnd) {
    	        return twoHyphens + boundary + lineEnd + "Content-Disposition: form-data; name=\"" + key + "\"" + lineEnd + lineEnd + value + lineEnd;
    	}      

	@Override
	public void onClick(View v) {
		 switch (v.getId()) {
		 	case R.id.camera3:
		 		Camera();
		 		break;		
		 }		
	}
}