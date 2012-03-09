package mobile.event.org;


import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.ImageView;

public class MobileEventGuide extends Activity implements OnClickListener{
    /** Called when the activity is first created. */
	
	int CAMERA_PIC_REQUEST=3333;

	
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
                  Bitmap pic = (Bitmap) b.get("data");

                  if (pic != null) { 
                   //Display your image in an ImageView in your layout (if you want to test it)
                      ImageView pictureHolder = (ImageView) this.findViewById(R.id.pictureholder);
                      pictureHolder.setImageBitmap(pic);
                      pictureHolder.invalidate();
                  }
              }
              else if (resultCode == Activity.RESULT_CANCELED) {}
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