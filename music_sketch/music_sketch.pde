import ddf.minim.*;
import ddf.minim.ugens.*;
import java.util.*;
import processing.sound.*;

// Buffer for JSON data loading
int BUFFER_SIZE = 500;

// Convert OpenCV speed to feet per second
double SPEED_MULTIPLIER = 6;

// Window size, in seconds, for computing average speed
int ROLL_AVG_SPEED_SEC = 8;

// Number of frames to show as past trace
int PAST_TRACE_FRAMES = 5;

// Sets if we should render frames to a folder instead of realtime playback
// Not rendering has live playback and saves speed-adjusted audio while printing a beat string
// Rendering saves frames and switches visuals based on beats string instead of live audio
boolean RENDER = true;

// To merge as an MP4 afterwards:
// ffmpeg -r 30 -f image2 -i "%04d.png" -i speed_audio.wav -crf 25 -c:v libx264 -pix_fmt yuv420p output.mp4

JSONArray[] danceTraces;
int frameNum;

BeatDetector detector;
SoundFile file;
Minim minim;
AudioInput in;
AudioRecorder recorder;
AudioOutput out;
FilePlayer player;

color frameColor;
MovingAverage avgCalculator;
ArrayList<JSONArray> pastTraces;

// Copied from printed output for beat detection
String beats = "00000000000000000000000000000000000000000000000000000000000000000010000001000000010000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000100000000000000000100000000000100000000000001000000000000000000000000000000000000000000000000000000000100000000000000000001000000000001000000000000000000100000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000010000000000000000000100000000000000000000000000001000000000000000010000000100000000000000000000000000100000000000000000000000000000000000000000010000000000000000000000000001000000000000000000100000000100000000000000000000000000000001000000000000000010000000000000000000100000000010000000000100000100000000000100000000010000000000000000000000000000000100000000000000000010000000000000000000000000000010000000000000000000000000000000000001000000000000001000000000010000000000000000000000000000100000000000000001000000000010000000000000001000000000000000010000000000000000010000000000000000100000000000000000000000000000100000000000000000000000000000100000000000000000000000000010000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000100000000000000000000100000000000000000000010000000000100000000001000000000010000000000000000000000100000000000000100000000000000000001000000000000000001000000000000001000000000000000000000000000010000000000010000000000000000000000000010000000000100000000001000000000000000100000000000000000000000000000000001000000000000000100000000000000000000000000000000000000000000000000000000000000000000000000";

void setup() {
  //size(640, 360, P2D);
  size(3840, 2160, P2D);
  
  frameNum = 0;

  frameColor = color(random(0, 256), random(0, 256), random(0, 256));
  // Number of JSON files here
  danceTraces = new JSONArray[5];

  for (int i = 0; i < danceTraces.length; i++) {
    danceTraces[i] = loadJSONArray("data-" + i + ".json");
  }
  
  frameRate(30);
  
  if (!RENDER) {
    file = new SoundFile(this, "bgm.wav");
    file.play();
    detector = new BeatDetector(this);  
    detector.input(file);
    detector.sensitivity(250);
    minim = new Minim(this);
    in = minim.getLineIn();
    // To record properly, open PulseAudio and monitor for system output
    recorder = minim.createRecorder(in, "output/speed_audio.wav", true);
    
    out = minim.getLineOut(Minim.STEREO);
  }
  
  avgCalculator = new MovingAverage(30 * ROLL_AVG_SPEED_SEC);
  pastTraces = new ArrayList<JSONArray>();
}



void draw() {
  if (frameNum == 0 && !RENDER) {
    recorder.beginRecord(); 
  }
  if ((RENDER && beats.charAt(frameNum) == '1') || (!RENDER && detector.isBeat())) {
    do {
      frameColor = color(random(0, 256), random(0, 256), random(0, 256));
    } while (brightness(frameColor) < 180);
    print(1);
  } else {
    print(0);
  }
  
  JSONObject frameInfo = danceTraces[frameNum / BUFFER_SIZE].getJSONObject(frameNum % BUFFER_SIZE);
  
  background(lerpColor(#000000, frameColor, 0.6));
  strokeWeight(0);
  stroke(frameColor, 0.0);

  pastTraces.add(frameInfo.getJSONArray("contours"));
  
  if (pastTraces.size() > PAST_TRACE_FRAMES) {
     pastTraces.remove(0); 
  }
  
  double speed = Math.sqrt(Math.pow(frameInfo.getFloat("mean_motion_py"), 2) + Math.pow(frameInfo.getFloat("mean_motion_px"), 2));
  avgCalculator.add(speed * SPEED_MULTIPLIER);

  
  float rate = 2.5 / (float) (1 + Math.pow(Math.E, -1.25 * (avgCalculator.getMean() - 5.5))) + 0.5;
  
  if (!RENDER) {
    file.rate(rate);  
  }
  
  int pastRecordNum = 1;
  for (JSONArray contours : pastTraces) {
    // Interpolate between background color and trace "foreground"
    fill(lerpColor(#000000, frameColor, 0.6 + 0.4 * pastRecordNum / pastTraces.size()));
    for (int i = 0; i < contours.size(); i++) {
      JSONArray contourSet = contours.getJSONArray(i);
      beginShape();
      for (int j = 0; j < contourSet.size(); j++) {
        JSONArray line = contourSet.getJSONArray(j);
        vertex(line.getFloat(0) * width, line.getFloat(1) * height);
      }
      endShape(CLOSE);
    }
    pastRecordNum += 1;
  }

  
  if (RENDER) {
    saveFrame("output/####.png");  
  }
  
  if (frameNum ==(danceTraces.length - 1) * BUFFER_SIZE + danceTraces[danceTraces.length - 1].size() - 1) {
    if (!RENDER) {
      saveRecording();
    }
    exit();
    frameNum = -1;
  }
  frameNum++;
}

void saveRecording() {
  recorder.endRecord();
  if (player != null) {
        player.unpatch( out );
        player.close();
    }
    player = new FilePlayer(recorder.save());
    player.patch( out );
    player.play();
}

class MovingAverage {
  Queue<Double> stream = new LinkedList<Double>(); 
  int period;
  double sum;
  MovingAverage(int period) {
     this.period = period; 
     this.sum = 0.0;
  }
  
  public void add(double num) {
     sum += num;
     stream.add(num);
     if (stream.size() > period) {
      sum -= stream.remove(); 
     }
  }
     
   public double getMean() {
    return sum / stream.size(); 
   }
  }
