# performance-captured

Processing sketches and Python pipelines for remixing captured performance from video or webcam feeds into new audio/video. Rotoscoping code [adapted from Marc Downie](http://openendedgroup.com/field2/pythonhead.html).

## Music and Motion Pipeline

Change the speed of a background music track based on optical flow speed in a video, then visualize subjects and beat changes in Processing

1. Set up an input data folder at `music_sketch/data/`
2. Analyze an input video with OpenCV and generate outputs as image frames and `data-*.json` files:

```
python3 rotoscoping/process.py --video <video path> --do_flow --do_background \
	--compute_contours --area_threshold 150 --output_directory music_sketch/data/ 
```

Each JSON file (segmented for every 500 frames) contains an array of JSON objects, each with info on the frame number, a set of points that define foreground contours, and the x and y average motion from optical flow.

3. Pick the desired background music track and place it in `music_sketch/data/` (default name: `bgm.wav`)
4. Open PulseAudio or a similar app to reroute system audio output into the input audio device
5. Open `music_sketch.pde` in Processing, setting `RENDER` to `false`. Adjust the number of JSON files you have and the background music filename accordingly. Set `SPEED_MULTIPLIER` based on the real-world width of your camera shot, with a good rule of thumb being 3/4 the width of your foreground in feet. Run the sketch afterwards (with a small, approx. 480p resolution). This will generate `music_sketch/output/speed_audio.wav` and a string of 1's and 0's for beat changes in the console output.
6. Copy/paste the beat changes from the console output into the `beats` string in the sketch, set `RENDER` to `true`, and set your desired render resolution in `size()`. Run the sketch again, which will generate a series of PNG frames in `music_sketch/output`.
7. Navigate to `music_sketch/output` on the command line, then convert the frames into a video and merge them with the sped-up audio:

```
ffmpeg -r 30 -f image2 -i "%04d.png" -i speed_audio.wav \
	-crf 25 -c:v libx264 -pix_fmt yuv420p output.mp4
```

The result will be saved in `music_sketch/output/output.mp4`

**Coming up:** making a live pipeline for all of this!
