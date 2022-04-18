import processing.sound.*;
SoundFile file;

JSONArray[] danceTraces;
int frameNum;
int BUFFER_SIZE = 500;
color[] colors;
int colorIdx = 0;

void setup() {
  size(1920, 1080);
  frameNum = 0;
  
  danceTraces = new JSONArray[9];
 
  for (int i = 0; i < danceTraces.length; i++) {
    danceTraces[i] = loadJSONArray("data-no-lines-" + i + ".json");
  }
  frameRate(30);
  colors = new color[] { #E80606, #F1d639, #E88b1a };
  file = new SoundFile(this, "dance-audio.mp3");
  file.play();
  
}

void draw() {
  JSONObject frameInfo = danceTraces[frameNum / BUFFER_SIZE].getJSONObject(frameNum % BUFFER_SIZE);
  color frameColor = colors[colorIdx % colors.length];
  background(frameColor);
  strokeWeight(3);
  stroke(lerpColor(frameColor, #000000, 0.5));
  
  JSONArray contours = frameInfo.getJSONArray("contours");
  
  
  for (int i = 0; i < contours.size(); i++) {
    color newColor = lerpColor(frameColor, #ffffff, random(0.2, 0.4));
    fill(newColor);
    
    JSONArray contourSet = contours.getJSONArray(i);
    beginShape();
    for (int j = 0; j < contourSet.size(); j++) {
      JSONArray line = contourSet.getJSONArray(j);
      vertex(line.getFloat(0) * width, line.getFloat(1) * height);  
      
    }
    endShape(CLOSE);  
    beginShape();
    for (int j = 0; j < contourSet.size(); j++) {
      JSONArray line = contourSet.getJSONArray(j);
      vertex(line.getFloat(0) * width + 120, line.getFloat(1) * height + 100);  
      
    }
    endShape(CLOSE);  
    beginShape();
    for (int j = 0; j < contourSet.size(); j++) {
      JSONArray line = contourSet.getJSONArray(j);
      vertex(line.getFloat(0) * width - 100, line.getFloat(1) * height + 80);  
      
    }
    endShape(CLOSE);  
  }
  
  if ((frameNum - 68) % 44 == 0) {
   colorIdx += 1; 
  }
  
  if (frameNum == (danceTraces.length - 1) * BUFFER_SIZE + danceTraces[danceTraces.length - 1].size() - 1) {
    break;
    frameNum = -1;
  }
  frameNum++;
  saveFrame("output/####.png");
}
