import processing.sound.*;
SoundFile file;

JSONArray[] danceTraces;
int frameNum;
int BUFFER_SIZE = 500;
color[] colors;
int colorIdx = 0;
BeatDetector detector;

color frameColor;
ArrayList<Double> pastSpeeds;
ArrayList<JSONArray> pastTraces;

void setup() {
  size(1280, 720);
  frameNum = 0;

  frameColor = #ff0000;
  danceTraces = new JSONArray[5];

  for (int i = 0; i < danceTraces.length; i++) {
    danceTraces[i] = loadJSONArray("data-no-lines-" + i + ".json");
  }
  frameRate(30);
  colors = new color[] { #E80606, #F1d639, #E88b1a };
  detector = new BeatDetector(this);
  file = new SoundFile(this, "output.wav");
  file.play();
  detector.input(file);
  detector.sensitivity(80);
  pastSpeeds = new ArrayList<Double>();
  pastTraces = new ArrayList<JSONArray>();
}

// Convert OpenCV speed to feet per second
double SPEED_MULTIPLIER = 6;

void draw() {
  JSONObject frameInfo = danceTraces[frameNum / BUFFER_SIZE].getJSONObject(frameNum % BUFFER_SIZE);
  
  background(lerpColor(#000000, frameColor, 0.6));
  strokeWeight(0);
  stroke(frameColor, 0.0);

  pastTraces.add(frameInfo.getJSONArray("contours"));
  
  if (pastTraces.size() > 5) {
     pastTraces.remove(0); 
  }
  
  double speed = Math.sqrt(Math.pow(frameInfo.getFloat("mean_motion_py"), 2) + Math.pow(frameInfo.getFloat("mean_motion_px"), 2));

  pastSpeeds.add(speed);
  
  if (pastSpeeds.size() > 30 * 8) {
     pastSpeeds.remove(0); 
  }
  
  double rollingAvgSpeed = 0.0;
  
  for (double pastSpeed : pastSpeeds) {
    rollingAvgSpeed += pastSpeed * SPEED_MULTIPLIER;
  }
  
  rollingAvgSpeed /= pastSpeeds.size();
  
  float rate = (float) 2.5 / (float) (1 + Math.pow(Math.E, -1.25 * (rollingAvgSpeed - 5.5))) + 0.5;
  file.rate(rate);
  
  int pastRecordNum = 1;
  for (JSONArray contours : pastTraces) {
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

  if (detector.isBeat()) {
    frameColor = color(random(0, 256), random(0, 256), random(0, 256));
  }
  // saveFrame("output/####.png");
  if (frameNum == (danceTraces.length - 1) * BUFFER_SIZE + danceTraces[danceTraces.length - 1].size() - 1) {
    exit();
    frameNum = -1;
  }
  frameNum++;
}
